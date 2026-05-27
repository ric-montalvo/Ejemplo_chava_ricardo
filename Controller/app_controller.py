# controller/app_controller.py
import os
import sys
from pathlib import Path
from tkinter import messagebox
import csv
import random
import threading
import customtkinter as ctk
import shutil
from View.visor_view import VisorView

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from Modelo.Orquestador import Orquestador
from Model.file_manager import FileManager
from View.main_window import MainWindow
from View.menu_view import MenuView
from View.carga_view import CargaView
from View.expedientes_view import ExpedientesView


class AppController:
    def __init__(self):
        self.root = MainWindow()
        # Directorio base (compatible con .exe)
        if getattr(sys, 'frozen', False):
            base = Path(sys.executable).parent
        else:
            base = Path(__file__).parent.parent
        self.file_manager = FileManager(base)
        self.modelo = Orquestador()

        self.nombre_actual = ""
        self.imagenes_procesadas = []

        # Bandera de cancelación
        self.procesamiento_cancelado = False
        self.carpeta_temporal = None

        self.mostrar_menu()

    # -------------------- Navegación --------------------
    def mostrar_menu(self):
        self.root.cambiar_vista(MenuView(self.root, self))

    def mostrar_carga(self):
        self.root.cambiar_vista(CargaView(self.root, self))

    def mostrar_expedientes(self):
        expedientes = self.file_manager.listar_expedientes()
        expedientes.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        self.root.cambiar_vista(ExpedientesView(self.root, self, expedientes))

    def volver_menu(self):
        self.mostrar_menu()

    # -------------------- Procesamiento principal --------------------
    def procesar_imagen(self, nombre_paciente, ruta_imagen):
        """Punto de entrada: valida, extrae nombre del archivo, crea carpeta y lanza procesamiento"""
        if not nombre_paciente or not ruta_imagen:
            messagebox.showerror("Error", "Complete todos los campos")
            return

        ext = os.path.splitext(ruta_imagen)[1].lower()
        if ext not in ('.jpg', '.jpeg'):
            messagebox.showerror("Formato no válido", "La imagen debe ser JPG o JPEG.")
            return

        # Obtener el nombre base del archivo (sin extensión) para buscar en el CSV
        nombre_archivo = Path(ruta_imagen).stem   # ej: "LAURA CAROLINA HERNANDEZ"

        nombre_limpio = self.file_manager.sanitizar_nombre_carpeta(nombre_paciente)
        carpeta_existente = self.file_manager.obtener_carpeta_por_nombre(nombre_limpio)

        if not carpeta_existente:
            try:
                carpeta_destino = self.file_manager.crear_carpeta_raiz(nombre_limpio)
                nombre_base = carpeta_destino.name
                ext = Path(ruta_imagen).suffix
                ruta_copia = carpeta_destino / f"{nombre_base}_original{ext}"
                shutil.copy2(ruta_imagen, ruta_copia)
                self.ejecutar_procesamiento(nombre_paciente, ruta_copia, carpeta_destino,
                                            nombre_base, nombre_archivo)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo crear la carpeta:\n{str(e)}")
        else:
            self.mostrar_dialogo_duplicado(nombre_paciente, ruta_imagen, carpeta_existente, nombre_archivo)

    def ejecutar_procesamiento(self, nombre_paciente, ruta_copia, carpeta_destino,
                               nombre_base, nombre_archivo):
        """Inicia el procesamiento en un hilo con botón de cancelar"""
        self.nombre_actual = nombre_paciente
        self.carpeta_temporal = carpeta_destino
        self.procesamiento_cancelado = False
        self.nombre_archivo = nombre_archivo   # para pasarlo al modelo

        # Overlay de progreso
        progress = ctk.CTkToplevel(self.root)
        progress.title("Procesando")
        progress.geometry("450x250")
        progress.transient(self.root)
        progress.grab_set()

        ctk.CTkLabel(progress, text="Procesando imagen...", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=30)
        ctk.CTkLabel(progress, text=f"Analizando radiografía dental de {nombre_paciente}").pack(pady=5)

        bar = ctk.CTkProgressBar(progress, width=300, mode="indeterminate")
        bar.pack(pady=20)
        bar.start()

        btn_cancelar = ctk.CTkButton(
            progress, text="Cancelar", width=120, height=30,
            fg_color="#ef4444", hover_color="#dc2626",
            command=lambda: self._cancelar_procesamiento(progress)
        )
        btn_cancelar.pack(pady=10)

        # Hilo de procesamiento
        def procesar():
            try:
                # Pasar el nombre del archivo (sin extensión) al orquestador
                resultados = self.modelo.procesar_pipeline(str(ruta_copia), self.nombre_archivo)
                if not self.procesamiento_cancelado:
                    self.imagenes_procesadas = resultados
                    self.root.after(0, self._finalizar_procesamiento_exitoso, progress)
                else:
                    self.root.after(0, self._limpiar_y_cerrar, progress, cancelado=True)
            except Exception as e:
                if not self.procesamiento_cancelado:
                    self.root.after(0, self._finalizar_procesamiento_con_error, progress, str(e))
                else:
                    self.root.after(0, self._limpiar_y_cerrar, progress, cancelado=True)

        hilo = threading.Thread(target=procesar, daemon=True)
        hilo.start()

    def _cancelar_procesamiento(self, progress_window):
        self.procesamiento_cancelado = True
        try:
            progress_window.destroy()
        except:
            pass
        self._limpiar_carpeta_expediente()
        messagebox.showinfo("Cancelado", "El procesamiento ha sido cancelado.\nNo se ha guardado ningún archivo.")

    def _limpiar_carpeta_expediente(self):
        if self.carpeta_temporal and self.carpeta_temporal.exists():
            try:
                shutil.rmtree(self.carpeta_temporal)
            except Exception as e:
                print(f"Error al limpiar carpeta: {e}")

    def _limpiar_y_cerrar(self, progress_window, cancelado=False):
        try:
            progress_window.destroy()
        except:
            pass

    def _finalizar_procesamiento_exitoso(self, progress_window):
        try:
            progress_window.destroy()
        except:
            pass

        # Guardar la imagen final (última de la lista) como Renderizada.bmp
        if self.imagenes_procesadas and self.carpeta_temporal:
            img_final, _ = self.imagenes_procesadas[-1]   # la última es la imagen final
            nombre_base = self.carpeta_temporal.name      # ej: "juan_perez"
            ruta_bmp = self.carpeta_temporal / f"{nombre_base}_Renderizada.bmp"
            img_final.save(ruta_bmp)                      # PIL guarda en BMP

        self.mostrar_expedientes()
        visor = VisorView(self.root, self.imagenes_procesadas, self.nombre_actual)
        visor.focus_force()

    def _finalizar_procesamiento_con_error(self, progress_window, mensaje_error):
        try:
            progress_window.destroy()
        except:
            pass
        import traceback
        traceback.print_exc()  # imprime en consola la línea exacta
        messagebox.showerror("Error", f"Error al procesar:\n{mensaje_error}")

    def _limpiar_carpeta_si_vacia(self):
        if self.carpeta_temporal and self.carpeta_temporal.exists():
            archivos = list(self.carpeta_temporal.glob("*"))
            if not archivos:
                try:
                    shutil.rmtree(self.carpeta_temporal)
                except:
                    pass

    # -------------------- Manejo de expedientes duplicados --------------------
    def on_visor_cerrado(self, destino):
        if destino == "menu":
            self.mostrar_menu()
        elif destino == "carga":
            self.mostrar_carga()
        elif destino == "expedientes":
            self.mostrar_expedientes()

    def eliminar_expediente(self, carpeta, dialog=None):
        try:
            shutil.rmtree(carpeta)
            if dialog:
                dialog.destroy()
            self.mostrar_expedientes()
            messagebox.showinfo("Éxito", "Expediente eliminado correctamente")
        except Exception as e:
            if dialog:
                dialog.destroy()
            messagebox.showerror("Error", f"No se pudo eliminar:\n{str(e)}")

    def obtener_expedientes(self):
        return self.file_manager.listar_expedientes()

    def sanitizar_nombre_carpeta(self, nombre: str) -> str:
        from utils.helpers import sanitizar_nombre
        import re
        nombre = sanitizar_nombre(nombre).lower().replace(' ', '_')
        nombre = re.sub(r'[^a-z_]', '', nombre)
        return nombre

    def mostrar_dialogo_duplicado(self, nombre_paciente, ruta_imagen, carpeta_existente, nombre_archivo):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Paciente Existente")
        dialog.geometry("450x200")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"+{x}+{y}")

        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(frame, text="Paciente Existente",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 10))
        ctk.CTkLabel(frame, text=f"Ya existe un expediente para {nombre_paciente}.",
                     font=ctk.CTkFont(size=12)).pack()
        ctk.CTkLabel(frame, text="¿Deseas sustituir la imagen existente o crear una subcarpeta?",
                     font=ctk.CTkFont(size=12)).pack(pady=(5, 15))

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack()

        def cerrar():
            dialog.destroy()

        def opcion_subcarpeta():
            dialog.destroy()
            self.procesar_con_subcarpeta(nombre_paciente, ruta_imagen, carpeta_existente, nombre_archivo)

        def opcion_sustituir():
            dialog.destroy()
            self.procesar_con_sustitucion(nombre_paciente, ruta_imagen, carpeta_existente, nombre_archivo)

        ctk.CTkButton(btn_frame, text="Cancelar", width=100, command=cerrar).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Crear Subcarpeta", width=130, command=opcion_subcarpeta,
                      fg_color="#10b981").pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Sustituir Imagen", width=130, command=opcion_sustituir,
                      fg_color="#3b82f6").pack(side="left", padx=10)

    def procesar_con_subcarpeta(self, nombre_paciente, ruta_imagen, carpeta_base, nombre_archivo):
        try:
            carpeta_destino = self.file_manager.crear_subcarpeta(carpeta_base)
            nombre_base = carpeta_destino.name
            ext = Path(ruta_imagen).suffix
            ruta_copia = carpeta_destino / f"{nombre_base}_original{ext}"
            shutil.copy2(ruta_imagen, ruta_copia)
            self.ejecutar_procesamiento(nombre_paciente, ruta_copia, carpeta_destino,
                                        nombre_base, nombre_archivo)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la subcarpeta:\n{str(e)}")

    def procesar_con_sustitucion(self, nombre_paciente, ruta_imagen, carpeta_existente, nombre_archivo):
        try:
            nombre_base = carpeta_existente.name
            ext = Path(ruta_imagen).suffix
            ruta_copia = carpeta_existente / f"{nombre_base}_original{ext}"
            shutil.copy2(ruta_imagen, ruta_copia)
            self.ejecutar_procesamiento(nombre_paciente, ruta_copia, carpeta_existente,
                                        nombre_base, nombre_archivo)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo sustituir la imagen:\n{str(e)}")

    # -------------------- Utilería de detalles y CSV --------------------
    def ver_detalles(self, carpeta):
        from View.detalles_view import DetallesView
        DetallesView(self.root, self, carpeta)

    def generar_csv_mock(self, carpeta: Path, nombre_base: str):
        csv_path = carpeta / "metricas.csv"
        dientes = [11,12,13,14,15,16,17,18,
                   21,22,23,24,25,26,27,28,
                   31,32,33,34,35,36,37,38,
                   41,42,43,44,45,46,47,48]
        metricas = []
        for diente in dientes:
            inclinacion = round(random.uniform(0,45),1)
            corona_raiz = round(random.uniform(0.5,2.0),2)
            longitud_raiz = random.randint(30,60)
            diastema = round(random.uniform(0,5),1)
            if 11 <= diente <= 18:
                ubicacion = "Superior Derecho"
            elif 21 <= diente <= 28:
                ubicacion = "Superior Izquierdo"
            elif 31 <= diente <= 38:
                ubicacion = "Inferior Izquierdo"
            else:
                ubicacion = "Inferior Derecho"
            metricas.append([diente, inclinacion, corona_raiz, longitud_raiz, diastema, ubicacion])

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Pieza","Inclinacion","CoronaRaiz","LongitudRaiz","Diastema","Ubicacion"])
            writer.writerows(metricas)

    def run(self):
        self.root.mainloop()