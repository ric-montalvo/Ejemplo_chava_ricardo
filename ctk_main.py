import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime

sys.path.append(os.path.dirname(__file__))
from Model.Procesador_imagen import Procesador_imagen

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SistemaDentalApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Sistema de Segmentación Dental")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)

        self.ruta_imagen_original = None
        self.imagenes_procesadas = []
        self.indice_actual = 0
        self.carpeta_actual = None
        self.ruta_grises_guardada = None

        if getattr(sys, 'frozen', False):
            self.base_dir = Path(sys.executable).parent
        else:
            self.base_dir = Path(__file__).parent

        self.expedientes_dir = self.base_dir / "expedientes"
        self.expedientes_dir.mkdir(exist_ok=True)

        self.nombre_entry = None
        self.btn_procesar = None
        self.lbl_imagen_info = None
        self.preview_label = None
        self.current_frame = None

        self.mostrar_menu_principal()

    def limpiar_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = ctk.CTkFrame(self.root)
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def volver_menu(self):
        self.limpiar_frame()
        self.mostrar_menu_principal()

    def mostrar_menu_principal(self):
        self.limpiar_frame()

        ctk.CTkLabel(
            self.current_frame,
            text="Sistema de Segmentación Dental",
            font=ctk.CTkFont(size=32, weight="bold")
        ).pack(pady=40)

        ctk.CTkLabel(
            self.current_frame,
            text="Procesamiento automático de radiografías dentales",
            font=ctk.CTkFont(size=16)
        ).pack(pady=10)

        botones_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        botones_frame.pack(pady=60)

        btn_cargar = ctk.CTkButton(
            botones_frame,
            text="📂 Cargar Imagen\n\nSube una radiografía dental\npara procesamiento automático",
            font=ctk.CTkFont(size=16),
            width=300,
            height=180,
            corner_radius=15,
            command=self.mostrar_carga_imagen
        )
        btn_cargar.pack(side="left", padx=40)

        btn_expedientes = ctk.CTkButton(
            botones_frame,
            text="📋 Ver Expedientes\n\nConsulta y administra\nlos registros de pacientes",
            font=ctk.CTkFont(size=16),
            width=300,
            height=180,
            corner_radius=15,
            command=self.mostrar_expedientes
        )
        btn_expedientes.pack(side="left", padx=40)

    def mostrar_carga_imagen(self):
        self.limpiar_frame()

        ctk.CTkLabel(
            self.current_frame,
            text="Cargar Radiografía Dental",
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=20)

        form_frame = ctk.CTkFrame(self.current_frame)
        form_frame.pack(pady=30, padx=40, fill="both", expand=True)

        ctk.CTkLabel(form_frame, text="Nombre del Paciente", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(20, 5))
        self.nombre_entry = ctk.CTkEntry(form_frame, placeholder_text="Ej: Juan Pérez", width=400, height=40)
        self.nombre_entry.pack(pady=(0, 20))
        self.nombre_entry.bind('<KeyRelease>', self.validar_formulario)

        ctk.CTkLabel(form_frame, text="Imagen de Radiografía", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(10, 5))

        self.btn_seleccionar = ctk.CTkButton(
            form_frame,
            text="📁 Seleccionar imagen",
            command=self.seleccionar_imagen,
            width=200
        )
        self.btn_seleccionar.pack(pady=10)

        self.lbl_imagen_info = ctk.CTkLabel(form_frame, text="No se ha seleccionado ninguna imagen", text_color="gray")
        self.lbl_imagen_info.pack()

        self.preview_frame = ctk.CTkFrame(form_frame, width=300, height=200, fg_color="transparent")
        self.preview_frame.pack(pady=15)
        self.preview_label = ctk.CTkLabel(self.preview_frame, text="")
        self.preview_label.pack()

        self.btn_procesar = ctk.CTkButton(
            form_frame,
            text="Procesar Imagen",
            command=self.procesar_imagen,
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            state="disabled"
        )
        self.btn_procesar.pack(pady=20)

        ctk.CTkButton(
            self.current_frame,
            text="← Volver",
            command=self.volver_menu,
            width=100,
            fg_color="gray"
        ).pack(pady=10)

    def seleccionar_imagen(self):
        ruta = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp")])
        if ruta:
            self.ruta_imagen_original = ruta
            self.lbl_imagen_info.configure(text=f"✅ {os.path.basename(ruta)}", text_color="green")

            img = Image.open(ruta)
            img.thumbnail((200, 150), Image.Resampling.LANCZOS)
            ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
            self.preview_label.configure(image=ctk_image, text="")
            self.preview_label.image = ctk_image

            self.validar_formulario()

    def validar_formulario(self, event=None):
        if len(self.nombre_entry.get().strip()) > 0 and self.ruta_imagen_original:
            self.btn_procesar.configure(state="normal")
        else:
            self.btn_procesar.configure(state="disabled")

    def guardar_imagen_grises(self, img_gris_pil, nombre_limpio, carpeta):
        """Guarda la imagen en escala de grises en la carpeta del paciente"""
        ruta_grises = carpeta / f"{nombre_limpio}_grises.png"
        img_gris_pil.save(ruta_grises)
        return ruta_grises

    def procesar_imagen(self):
        nombre = self.nombre_entry.get().strip()
        if not nombre or not self.ruta_imagen_original:
            messagebox.showerror("Error", "Complete todos los campos")
            return

        fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_limpio = "".join(c for c in nombre if c.isalnum() or c in " ._-")
        self.carpeta_actual = self.expedientes_dir / f"{nombre_limpio}_{fecha_str}"
        self.carpeta_actual.mkdir(parents=True, exist_ok=True)

        ext = os.path.splitext(self.ruta_imagen_original)[1]
        imagen_destino = self.carpeta_actual / f"{nombre_limpio}_original{ext}"
        shutil.copy2(self.ruta_imagen_original, imagen_destino)

        # Ventana de progreso
        progress_window = ctk.CTkToplevel(self.root)
        progress_window.title("Procesando")
        progress_window.geometry("400x200")
        progress_window.transient(self.root)
        progress_window.grab_set()

        ctk.CTkLabel(progress_window, text="Procesando...", font=ctk.CTkFont(size=18)).pack(pady=30)
        ctk.CTkLabel(progress_window, text=f"Analizando radiografía dental de {nombre}").pack(pady=10)
        progress = ctk.CTkProgressBar(progress_window, width=300, mode="indeterminate")
        progress.pack(pady=20)
        progress.start()

        self.root.update()

        try:
            modelo = Procesador_imagen()
            self.imagenes_procesadas = modelo.procesar_pipeline(str(imagen_destino))
            self.indice_actual = 0

            # Guardar SOLO la imagen de grises (step_1 es la grises)
            # self.imagenes_procesadas[1] = (img_gris, "2. Escala de Grises")
            if len(self.imagenes_procesadas) >= 2:
                img_gris_pil, _ = self.imagenes_procesadas[1]
                self.ruta_grises_guardada = self.guardar_imagen_grises(img_gris_pil, nombre_limpio, self.carpeta_actual)

            progress_window.destroy()
            self.mostrar_visor_imagenes()

        except Exception as e:
            progress_window.destroy()
            messagebox.showerror("Error", f"Error al procesar:\n{str(e)}")

    def mostrar_visor_imagenes(self):
        """Muestra las 3 imágenes con navegación por teclado y botones"""
        visor = ctk.CTkToplevel(self.root)
        visor.title("Resultados del Procesamiento - 3 Imágenes")
        visor.geometry("1000x700")
        visor.transient(self.root)
        visor.grab_set()

        nombre = self.nombre_entry.get().strip()
        ctk.CTkLabel(visor, text=f"Resultados - {nombre}", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=10)

        lbl_info = ctk.CTkLabel(visor, text="", font=ctk.CTkFont(size=14))
        lbl_info.pack(pady=5)

        img_frame = ctk.CTkFrame(visor, width=900, height=550)
        img_frame.pack(pady=20, padx=20, fill="both", expand=True)
        img_frame.pack_propagate(False)

        image_label = ctk.CTkLabel(img_frame, text="")
        image_label.pack(fill="both", expand=True)

        def actualizar_visor():
            if not self.imagenes_procesadas:
                return
            img_pil, texto = self.imagenes_procesadas[self.indice_actual]

            max_width = 850
            max_height = 500
            img_pil.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            ctk_image = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(img_pil.width, img_pil.height))
            image_label.configure(image=ctk_image, text="")
            image_label.image = ctk_image

            total = len(self.imagenes_procesadas)
            lbl_info.configure(text=f"{texto} | Imagen {self.indice_actual + 1} de {total}")

        def anterior():
            if self.imagenes_procesadas:
                self.indice_actual = (self.indice_actual - 1) % len(self.imagenes_procesadas)
                actualizar_visor()

        def siguiente():
            if self.imagenes_procesadas:
                self.indice_actual = (self.indice_actual + 1) % len(self.imagenes_procesadas)
                actualizar_visor()

        def on_key_press(event):
            if event.keysym == 'Left':
                anterior()
            elif event.keysym == 'Right':
                siguiente()
            elif event.keysym == 'Escape':
                visor.destroy()

        visor.bind('<Key>', on_key_press)

        nav_frame = ctk.CTkFrame(visor, fg_color="transparent")
        nav_frame.pack(pady=10)

        ctk.CTkButton(nav_frame, text="◀ Anterior (←)", command=anterior, width=140).pack(side="left", padx=20)
        ctk.CTkButton(nav_frame, text="Siguiente (→)", command=siguiente, width=140).pack(side="left", padx=20)

        indicador_frame = ctk.CTkFrame(visor, fg_color="transparent")
        indicador_frame.pack(pady=5)

        ctk.CTkLabel(indicador_frame,
                     text="📸 1. Original     |     2. Escala de Grises     |     3. Inversión de grises",
                     font=ctk.CTkFont(size=12), text_color="gray").pack()

        action_frame = ctk.CTkFrame(visor, fg_color="transparent")
        action_frame.pack(pady=10)

        ctk.CTkButton(action_frame, text="📋 Ver Expedientes",
                      command=lambda: [visor.destroy(), self.mostrar_expedientes()], width=150).pack(side="left",
                                                                                                     padx=10)
        ctk.CTkButton(action_frame, text="📂 Nueva Imagen",
                      command=lambda: [visor.destroy(), self.mostrar_carga_imagen()], width=150).pack(side="left",
                                                                                                      padx=10)
        ctk.CTkButton(action_frame, text="🏠 Menú Principal",
                      command=lambda: [visor.destroy(), self.volver_menu()], width=150, fg_color="gray").pack(
            side="left", padx=10)

        actualizar_visor()

    def mostrar_expedientes(self):
        self.limpiar_frame()

        ctk.CTkLabel(
            self.current_frame,
            text="Expedientes de Pacientes",
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=20)

        lista_frame = ctk.CTkScrollableFrame(self.current_frame, width=800, height=450)
        lista_frame.pack(pady=20, padx=40, fill="both", expand=True)

        expedientes = [c for c in self.expedientes_dir.iterdir() if c.is_dir()]
        expedientes.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        if expedientes:
            for carpeta in expedientes:
                fecha_mod = datetime.fromtimestamp(carpeta.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                archivos = list(carpeta.glob("*"))
                tiene_invertida = any("invertida" in f.name for f in archivos)
                tiene_grises = any("grises" in f.name for f in archivos)

                card = ctk.CTkFrame(lista_frame)
                card.pack(fill="x", pady=5, padx=10)

                info_frame = ctk.CTkFrame(card, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True, padx=10, pady=10)

                ctk.CTkLabel(info_frame, text=carpeta.name, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")

                estado = "✅ Completado"
                if not tiene_invertida:
                    estado = "⚠️ Sin invertida"
                elif not tiene_grises:
                    estado = "⚠️ Sin grises"

                ctk.CTkLabel(info_frame, text=f"📅 {fecha_mod} | 📄 {len(archivos)} archivos | {estado}",
                             font=ctk.CTkFont(size=11)).pack(anchor="w")

                def ver_detalle(c=carpeta):
                    archivos_lista = list(c.glob("*"))
                    archivos_str = "\n".join([f"  - {a.name}" for a in archivos_lista[:8]])
                    if len(archivos_lista) > 8:
                        archivos_str += f"\n  ... y {len(archivos_lista) - 8} más"
                    invertida = [f for f in archivos_lista if "invertida" in f.name.lower()]
                    invertida_info = f"\n🖼️ Imagen invertida: {invertida[0].name}" if invertida else ""
                    grises = [f for f in archivos_lista if "grises" in f.name.lower()]
                    grises_info = f"\n🌫️ Escala de grises: {grises[0].name}" if grises else ""
                    messagebox.showinfo("Detalles",
                                        f"📁 {c.name}\n\n📅 Fecha: {datetime.fromtimestamp(c.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\n📄 Archivos: {len(archivos_lista)}{invertida_info}{grises_info}\n\n📋 Contenido:\n{archivos_str}")

                btn_ver = ctk.CTkButton(card, text="Ver Detalles", width=100, height=30, command=ver_detalle)
                btn_ver.pack(side="right", padx=10)
        else:
            ctk.CTkLabel(lista_frame, text="📂 No hay expedientes aún.\nProcesa una imagen para crear uno.",
                         font=ctk.CTkFont(size=14)).pack(pady=50)

        ctk.CTkButton(self.current_frame, text="🔄 Actualizar", command=self.mostrar_expedientes, width=100).pack(pady=5)
        ctk.CTkButton(self.current_frame, text="← Volver", command=self.volver_menu, width=100, fg_color="gray").pack(
            pady=10)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = SistemaDentalApp()
    app.run()