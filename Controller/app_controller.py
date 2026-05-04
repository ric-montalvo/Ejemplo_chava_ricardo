# controller/app_controller.py
from pathlib import Path
import sys
import os
from tkinter import messagebox
import customtkinter as ctk

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from Model.Procesador_imagen import Procesador_imagen
from Model.file_manager import FileManager
from View.main_window import MainWindow
from View.menu_view import MenuView
from View.carga_view import CargaView
from View.visor_view import VisorView
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
        self.modelo = Procesador_imagen()   # ← aquí se reemplazará con el pipeline real

        self.nombre_actual = ""
        self.imagenes_procesadas = []

        self.mostrar_menu()

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

    def procesar_imagen(self, nombre_paciente, ruta_imagen):
        """Punto de entrada principal: verifica si existe la carpeta y decide qué hacer"""
        if not nombre_paciente or not ruta_imagen:
            from tkinter import messagebox
            messagebox.showerror("Error", "Complete todos los campos")
            return

        # ===== VALIDACIÓN DE FORMATO (aquí) =====
        import os
        from tkinter import messagebox
        ext = os.path.splitext(ruta_imagen)[1].lower()
        if ext not in ('.jpg', '.jpeg'):
            messagebox.showerror("Formato no válido", "La imagen debe ser JPG o JPEG.")
            return
        # =======================================

        from pathlib import Path
        import shutil

        nombre_limpio = self.file_manager.sanitizar_nombre_carpeta(nombre_paciente)

        # Buscar si ya existe una carpeta con ese nombre (en cualquier nivel)
        carpeta_existente = self.file_manager.obtener_carpeta_por_nombre(nombre_limpio)

        if not carpeta_existente:
            # Caso 1: No existe -> crear carpeta raíz (sin fecha)
            try:
                carpeta_destino = self.file_manager.crear_carpeta_raiz(nombre_limpio)
                nombre_base = carpeta_destino.name
                ext = Path(ruta_imagen).suffix
                ruta_copia = carpeta_destino / f"{nombre_base}_original{ext}"
                shutil.copy2(ruta_imagen, ruta_copia)
                self.ejecutar_procesamiento(nombre_paciente, ruta_copia, carpeta_destino, nombre_base)
            except Exception as e:
                from tkinter import messagebox
                messagebox.showerror("Error", f"No se pudo crear la carpeta:\n{str(e)}")
        else:
            # Caso 2: Ya existe -> mostrar diálogo
            self.mostrar_dialogo_duplicado(nombre_paciente, ruta_imagen, carpeta_existente)

    def on_visor_cerrado(self, destino):
        if destino == "menu":
            self.mostrar_menu()
        elif destino == "carga":
            self.mostrar_carga()
        elif destino == "expedientes":
            self.mostrar_expedientes()

    # controller/app_controller.py (agregar este método)

    def eliminar_expediente(self, carpeta, dialog=None):
        """Elimina la carpeta del expediente y cierra el diálogo"""
        try:
            import shutil
            shutil.rmtree(carpeta)
            if dialog:
                dialog.destroy()
            self.mostrar_expedientes()
            messagebox.showinfo("Éxito", "Expediente eliminado correctamente")
        except Exception as e:
            if dialog:
                dialog.destroy()
            messagebox.showerror("Error", f"No se pudo eliminar:\n{str(e)}")

    # En AppController, agregar:
    def obtener_expedientes(self):
        """Devuelve la lista actual de expedientes (carpetas)"""
        return self.file_manager.listar_expedientes()

    def sanitizar_nombre_carpeta(self, nombre: str) -> str:
        from utils.helpers import sanitizar_nombre
        import re
        nombre = sanitizar_nombre(nombre).lower().replace(' ', '_')
        nombre = re.sub(r'[^a-z_]', '', nombre)  # solo letras y guion bajo
        return nombre

    def mostrar_dialogo_duplicado(self, nombre_paciente, ruta_imagen, carpeta_existente):
        """Muestra el diálogo con tres opciones: cancelar, subcarpeta, sustituir"""
        import customtkinter as ctk
        from tkinter import messagebox

        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Paciente Existente")
        dialog.geometry("450x200")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        # Centrar ventana
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
            self.procesar_con_subcarpeta(nombre_paciente, ruta_imagen, carpeta_existente)

        def opcion_sustituir():
            dialog.destroy()
            self.procesar_con_sustitucion(nombre_paciente, ruta_imagen, carpeta_existente)

        ctk.CTkButton(btn_frame, text="Cancelar", width=100, command=cerrar).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Crear Subcarpeta", width=130, command=opcion_subcarpeta,
                      fg_color="#10b981").pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Sustituir Imagen", width=130, command=opcion_sustituir, fg_color="#3b82f6").pack(
            side="left", padx=10)

    def procesar_con_subcarpeta(self, nombre_paciente, ruta_imagen, carpeta_base):
        """Crea una subcarpeta y guarda la imagen allí"""
        try:
            from pathlib import Path
            import shutil
            carpeta_destino = self.file_manager.crear_subcarpeta(carpeta_base)
            nombre_base = carpeta_destino.name
            ext = Path(ruta_imagen).suffix
            ruta_copia = carpeta_destino / f"{nombre_base}_original{ext}"
            shutil.copy2(ruta_imagen, ruta_copia)
            self.ejecutar_procesamiento(nombre_paciente, ruta_copia, carpeta_destino, nombre_base)
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"No se pudo crear la subcarpeta:\n{str(e)}")

    def procesar_con_sustitucion(self, nombre_paciente, ruta_imagen, carpeta_existente):
        """Sobrescribe la imagen en la carpeta existente"""
        try:
            from pathlib import Path
            import shutil
            nombre_base = carpeta_existente.name
            ext = Path(ruta_imagen).suffix
            ruta_copia = carpeta_existente / f"{nombre_base}_original{ext}"
            shutil.copy2(ruta_imagen, ruta_copia)
            self.ejecutar_procesamiento(nombre_paciente, ruta_copia, carpeta_existente, nombre_base)
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", f"No se pudo sustituir la imagen:\n{str(e)}")

    def ejecutar_procesamiento(self, nombre_paciente, ruta_copia, carpeta_destino, nombre_base):
        """Realiza el procesamiento de la imagen (overlay, modelo, guardar grises, mostrar expedientes y visor)"""
        import customtkinter as ctk
        from tkinter import messagebox
        from View.visor_view import VisorView

        # Overlay de procesamiento
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
        self.root.update()

        try:
            # Llamada al modelo de Montoya
            self.imagenes_procesadas = self.modelo.procesar_pipeline(str(ruta_copia))

            # Guardar imagen en grises
            if len(self.imagenes_procesadas) >= 2:
                img_gris, _ = self.imagenes_procesadas[1]
                self.file_manager.guardar_imagen_grises(img_gris, carpeta_destino, nombre_paciente)

            progress.destroy()

            # Mostrar expedientes y luego visor
            self.mostrar_expedientes()
            visor = VisorView(self.root, self.imagenes_procesadas, nombre_paciente)
            visor.focus_force()

        except Exception as e:
            progress.destroy()
            messagebox.showerror("Error", f"Error al procesar:\n{str(e)}")

    def run(self):
        self.root.mainloop()