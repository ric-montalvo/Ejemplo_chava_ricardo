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

# Configurar tema claro para asemejar las capturas
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class SistemaDentalApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Sistema de Segmentación Dental")
        self.root.geometry("1100x750")
        self.root.minsize(900, 600)

        # Variables de estado (igual que antes)
        self.ruta_imagen_original = None
        self.imagenes_procesadas = []
        self.indice_actual = 0
        self.carpeta_actual = None
        self.ruta_grises_guardada = None

        # Directorio base y expedientes
        if getattr(sys, 'frozen', False):
            self.base_dir = Path(sys.executable).parent
        else:
            self.base_dir = Path(__file__).parent

        self.expedientes_dir = self.base_dir / "expedientes"
        self.expedientes_dir.mkdir(exist_ok=True)

        # Widgets que se usarán en diferentes pantallas
        self.nombre_entry = None
        self.btn_procesar = None
        self.lbl_imagen_info = None
        self.preview_label = None
        self.current_frame = None

        self.mostrar_menu_principal()

    def limpiar_frame(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = ctk.CTkFrame(self.root, fg_color="white")
        self.current_frame.pack(fill="both", expand=True, padx=0, pady=0)

    def volver_menu(self):
        self.limpiar_frame()
        self.mostrar_menu_principal()

    # ================== MENÚ PRINCIPAL (con tarjetas) ==================
    def mostrar_menu_principal(self):
        self.limpiar_frame()

        # Contenedor centrado
        main_container = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        main_container.pack(expand=True, fill="both")

        # Título
        titulo = ctk.CTkLabel(
            main_container,
            text="Sistema de Segmentación Dental",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color="#1f2937"
        )
        titulo.pack(pady=(40, 10))

        subtitulo = ctk.CTkLabel(
            main_container,
            text="Procesamiento automático de radiografías dentales",
            font=ctk.CTkFont(size=16),
            text_color="#6b7280"
        )
        subtitulo.pack(pady=(0, 60))

        # Frame para las dos tarjetas
        tarjetas_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        tarjetas_frame.pack(expand=True)

        # Tarjeta "Cargar Imagen"
        card_cargar = ctk.CTkFrame(
            tarjetas_frame,
            width=320,
            height=280,
            corner_radius=20,
            border_width=1,
            border_color="#e5e7eb",
            fg_color="white"
        )
        card_cargar.pack(side="left", padx=30, expand=True)
        card_cargar.pack_propagate(False)

        ctk.CTkLabel(card_cargar, text="📂", font=ctk.CTkFont(size=48)).pack(pady=(30, 10))
        ctk.CTkLabel(card_cargar, text="Cargar Imagen", font=ctk.CTkFont(size=20, weight="bold")).pack()
        ctk.CTkLabel(
            card_cargar,
            text="Sube una radiografía dental para procesamiento automático",
            font=ctk.CTkFont(size=12),
            wraplength=260,
            text_color="#6b7280"
        ).pack(pady=(10, 20))
        btn_cargar = ctk.CTkButton(
            card_cargar,
            text="Comenzar",
            command=self.mostrar_carga_imagen,
            width=180,
            height=40,
            corner_radius=20,
            fg_color="#3b82f6",
            hover_color="#2563eb"
        )
        btn_cargar.pack(pady=10)

        # Tarjeta "Ver Expedientes"
        card_exp = ctk.CTkFrame(
            tarjetas_frame,
            width=320,
            height=280,
            corner_radius=20,
            border_width=1,
            border_color="#e5e7eb",
            fg_color="white"
        )
        card_exp.pack(side="left", padx=30, expand=True)
        card_exp.pack_propagate(False)

        ctk.CTkLabel(card_exp, text="📋", font=ctk.CTkFont(size=48)).pack(pady=(30, 10))
        ctk.CTkLabel(card_exp, text="Ver Expedientes", font=ctk.CTkFont(size=20, weight="bold")).pack()
        ctk.CTkLabel(
            card_exp,
            text="Consulta y administra los registros de pacientes",
            font=ctk.CTkFont(size=12),
            wraplength=260,
            text_color="#6b7280"
        ).pack(pady=(10, 20))
        btn_exp = ctk.CTkButton(
            card_exp,
            text="Ver Registros",
            command=self.mostrar_expedientes,
            width=180,
            height=40,
            corner_radius=20,
            fg_color="#3b82f6",
            hover_color="#2563eb"
        )
        btn_exp.pack(pady=10)

    # ================== PANTALLA DE CARGA ==================
    def mostrar_carga_imagen(self):
        self.limpiar_frame()

        # Título
        titulo = ctk.CTkLabel(
            self.current_frame,
            text="Cargar Radiografía Dental",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#1f2937"
        )
        titulo.pack(pady=30)

        subtitulo = ctk.CTkLabel(
            self.current_frame,
            text="Ingresa el nombre del paciente y selecciona la imagen para procesamiento",
            font=ctk.CTkFont(size=14),
            text_color="#6b7280"
        )
        subtitulo.pack(pady=(0, 30))

        # Frame del formulario (centrado)
        form_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        form_frame.pack(expand=True)

        # Campo nombre
        ctk.CTkLabel(form_frame, text="Nombre del Paciente", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        self.nombre_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Ej: Juan Pérez",
            width=400,
            height=40,
            corner_radius=10,
            border_width=1,
            border_color="#d1d5db"
        )
        self.nombre_entry.pack(pady=(5, 20))
        self.nombre_entry.bind('<KeyRelease>', self.validar_formulario)

        # Área de carga de imagen
        ctk.CTkLabel(form_frame, text="Imagen de Radiografía", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")

        # Recuadro de selección (estilo área de clic)
        self.area_carga_frame = ctk.CTkFrame(
            form_frame,
            width=400,
            height=160,
            corner_radius=15,
            border_width=2,
            border_color="#3b82f6",
            fg_color="#f0f9ff"
        )
        self.area_carga_frame.pack(pady=10)
        self.area_carga_frame.pack_propagate(False)

        self.lbl_click = ctk.CTkLabel(
            self.area_carga_frame,
            text="📁 Haz clic para seleccionar una imagen\nPNG, JPG o JPEG",
            font=ctk.CTkFont(size=12),
            text_color="#3b82f6"
        )
        self.lbl_click.pack(expand=True)
        self.area_carga_frame.bind("<Button-1>", lambda e: self.seleccionar_imagen())
        self.lbl_click.bind("<Button-1>", lambda e: self.seleccionar_imagen())

        # Preview de imagen (inicialmente oculto)
        self.preview_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        self.preview_label = ctk.CTkLabel(self.preview_frame, text="")
        self.preview_label.pack()
        self.btn_remover = ctk.CTkButton(
            self.preview_frame,
            text="✕ Quitar imagen",
            width=100,
            height=30,
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=self.remover_imagen
        )

        self.lbl_imagen_info = ctk.CTkLabel(form_frame, text="", font=ctk.CTkFont(size=12))

        # Botón procesar
        self.btn_procesar = ctk.CTkButton(
            form_frame,
            text="Procesar Imagen",
            command=self.procesar_imagen,
            width=200,
            height=45,
            corner_radius=25,
            font=ctk.CTkFont(size=14, weight="bold"),
            state="disabled",
            fg_color="#3b82f6",
            hover_color="#2563eb"
        )
        self.btn_procesar.pack(pady=30)

        # Botón volver
        ctk.CTkButton(
            self.current_frame,
            text="← Volver",
            command=self.volver_menu,
            width=100,
            height=35,
            corner_radius=15,
            fg_color="#9ca3af",
            hover_color="#6b7280"
        ).pack(pady=10)

    def seleccionar_imagen(self):
        ruta = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp")])
        if ruta:
            self.ruta_imagen_original = ruta
            self.lbl_imagen_info.configure(text=f"✅ {os.path.basename(ruta)}", text_color="#10b981")
            # Ocultar área de carga y mostrar preview
            self.area_carga_frame.pack_forget()
            self.preview_frame.pack(pady=10)
            self.btn_remover.pack(pady=5)
            # Cargar preview
            img = Image.open(ruta)
            img.thumbnail((180, 120), Image.Resampling.LANCZOS)
            ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
            self.preview_label.configure(image=ctk_image, text="")
            self.preview_label.image = ctk_image
            self.lbl_imagen_info.pack()
            self.validar_formulario()

    def remover_imagen(self):
        self.ruta_imagen_original = None
        self.preview_frame.pack_forget()
        self.area_carga_frame.pack(pady=10)
        self.lbl_imagen_info.pack_forget()
        self.btn_procesar.configure(state="disabled")
        self.validar_formulario()

    def validar_formulario(self, event=None):
        nombre_valido = len(self.nombre_entry.get().strip()) > 0
        if nombre_valido and self.ruta_imagen_original:
            self.btn_procesar.configure(state="normal")
        else:
            self.btn_procesar.configure(state="disabled")

    # ================== GUARDADO Y PROCESAMIENTO ==================
    def guardar_imagen_grises(self, img_gris_pil, nombre_limpio, carpeta):
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

        # Overlay de procesamiento (similar a la captura)
        progress_window = ctk.CTkToplevel(self.root)
        progress_window.title("Procesando")
        progress_window.geometry("450x250")
        progress_window.transient(self.root)
        progress_window.grab_set()

        # Contenido del overlay
        ctk.CTkLabel(progress_window, text="Procesando imagen...", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=30)
        ctk.CTkLabel(progress_window, text=f"Analizando radiografía dental de {nombre}", font=ctk.CTkFont(size=12)).pack(pady=5)
        progress = ctk.CTkProgressBar(progress_window, width=300, mode="indeterminate")
        progress.pack(pady=20)
        progress.start()

        btn_cancelar = ctk.CTkButton(
            progress_window,
            text="Cancelar Procesamiento",
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=lambda: self.cancelar_procesamiento(progress_window)
        )
        btn_cancelar.pack(pady=10)

        self.root.update()

        try:
            modelo = Procesador_imagen()
            self.imagenes_procesadas = modelo.procesar_pipeline(str(imagen_destino))
            self.indice_actual = 0

            if len(self.imagenes_procesadas) >= 2:
                img_gris_pil, _ = self.imagenes_procesadas[1]
                self.ruta_grises_guardada = self.guardar_imagen_grises(img_gris_pil, nombre_limpio, self.carpeta_actual)

            progress_window.destroy()
            self.mostrar_visor_imagenes()

        except Exception as e:
            progress_window.destroy()
            messagebox.showerror("Error", f"Error al procesar:\n{str(e)}")

    def cancelar_procesamiento(self, window):
        window.destroy()
        # Opcional: puedes agregar lógica para abortar el procesamiento si es posible
        messagebox.showinfo("Cancelado", "Procesamiento cancelado por el usuario.")

    # ================== VISOR DE 3 IMÁGENES ==================
    def mostrar_visor_imagenes(self):
        visor = ctk.CTkToplevel(self.root)
        visor.title("Resultados del Procesamiento")
        visor.geometry("1000x700")
        visor.transient(self.root)
        visor.grab_set()

        nombre = self.nombre_entry.get().strip()
        ctk.CTkLabel(visor, text=f"Resultados - {nombre}", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=15)

        lbl_info = ctk.CTkLabel(visor, text="", font=ctk.CTkFont(size=14))
        lbl_info.pack(pady=5)

        img_frame = ctk.CTkFrame(visor, width=900, height=550, fg_color="white", corner_radius=10)
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
                     font=ctk.CTkFont(size=12), text_color="#6b7280").pack()

        action_frame = ctk.CTkFrame(visor, fg_color="transparent")
        action_frame.pack(pady=10)
        ctk.CTkButton(action_frame, text="📋 Ver Expedientes",
                      command=lambda: [visor.destroy(), self.mostrar_expedientes()], width=150).pack(side="left", padx=10)
        ctk.CTkButton(action_frame, text="📂 Nueva Imagen",
                      command=lambda: [visor.destroy(), self.mostrar_carga_imagen()], width=150).pack(side="left", padx=10)
        ctk.CTkButton(action_frame, text="🏠 Menú Principal",
                      command=lambda: [visor.destroy(), self.volver_menu()], width=150, fg_color="#9ca3af").pack(side="left", padx=10)

        actualizar_visor()

    # ================== PANTALLA DE EXPEDIENTES ==================
    def mostrar_expedientes(self):
        self.limpiar_frame()

        # Barra superior con título y botón volver
        top_bar = ctk.CTkFrame(self.current_frame, fg_color="transparent", height=50)
        top_bar.pack(fill="x", padx=30, pady=(20, 0))
        btn_volver = ctk.CTkButton(
            top_bar,
            text="← Volver",
            command=self.volver_menu,
            width=80,
            height=35,
            corner_radius=15,
            fg_color="#9ca3af",
            hover_color="#6b7280"
        )
        btn_volver.pack(side="left")

        titulo = ctk.CTkLabel(
            self.current_frame,
            text="Expedientes de Pacientes",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#1f2937"
        )
        titulo.pack(pady=20)

        # Barra de búsqueda y ordenamiento (UI solamente)
        filtros_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        filtros_frame.pack(fill="x", padx=40, pady=10)
        entry_buscar = ctk.CTkEntry(
            filtros_frame,
            placeholder_text="Buscar por nombre...",
            width=250,
            height=35,
            corner_radius=15,
            border_color="#d1d5db"
        )
        entry_buscar.pack(side="left", padx=5)
        combo_orden = ctk.CTkOptionMenu(
            filtros_frame,
            values=["Más recientes", "Más antiguos", "A-Z", "Z-A"],
            width=150,
            height=35,
            corner_radius=15,
            fg_color="#f3f4f6",
            button_color="#3b82f6"
        )
        combo_orden.pack(side="right", padx=5)

        # Contenedor de lista de expedientes
        lista_frame = ctk.CTkScrollableFrame(self.current_frame, width=800, height=450, fg_color="transparent")
        lista_frame.pack(pady=20, padx=40, fill="both", expand=True)

        expedientes = [c for c in self.expedientes_dir.iterdir() if c.is_dir()]
        expedientes.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        if expedientes:
            for carpeta in expedientes:
                fecha_mod = datetime.fromtimestamp(carpeta.stat().st_mtime).strftime("%d de %B de %Y, %H:%M")
                archivos = list(carpeta.glob("*"))
                # Mock de piezas segmentadas (podría calcularse, pero dejamos un número simbólico)
                num_piezas = len([f for f in archivos if "invertida" in f.name]) * 8  # solo para mostrar

                card = ctk.CTkFrame(
                    lista_frame,
                    corner_radius=15,
                    border_width=1,
                    border_color="#e5e7eb",
                    fg_color="white"
                )
                card.pack(fill="x", pady=8, padx=10)

                info_frame = ctk.CTkFrame(card, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=12)

                ctk.CTkLabel(info_frame, text=carpeta.name, font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")
                ctk.CTkLabel(
                    info_frame,
                    text=f"{fecha_mod}  |  {num_piezas} piezas segmentadas",
                    font=ctk.CTkFont(size=12),
                    text_color="#6b7280"
                ).pack(anchor="w")

                def ver_detalle(c=carpeta):
                    archivos_lista = list(c.glob("*"))
                    archivos_str = "\n".join([f"  - {a.name}" for a in archivos_lista[:8]])
                    if len(archivos_lista) > 8:
                        archivos_str += f"\n  ... y {len(archivos_lista) - 8} más"
                    invertida = [f for f in archivos_lista if "invertida" in f.name.lower()]
                    invertida_info = f"\n🖼️ Imagen invertida: {invertida[0].name}" if invertida else ""
                    grises = [f for f in archivos_lista if "grises" in f.name.lower()]
                    grises_info = f"\n🌫️ Escala de grises: {grises[0].name}" if grises else ""
                    messagebox.showinfo(
                        "Detalles del Expediente",
                        f"📁 {c.name}\n\n📅 Fecha: {datetime.fromtimestamp(c.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\n📄 Archivos: {len(archivos_lista)}{invertida_info}{grises_info}\n\n📋 Contenido:\n{archivos_str}"
                    )

                btn_ver = ctk.CTkButton(
                    card,
                    text="Ver Detalles",
                    width=110,
                    height=35,
                    corner_radius=15,
                    fg_color="#3b82f6",
                    hover_color="#2563eb",
                    command=ver_detalle
                )
                btn_ver.pack(side="right", padx=15)
        else:
            # Mensaje cuando no hay expedientes
            empty_frame = ctk.CTkFrame(lista_frame, fg_color="transparent")
            empty_frame.pack(expand=True, fill="both")
            ctk.CTkLabel(
                empty_frame,
                text="📂 No hay expedientes registrados",
                font=ctk.CTkFont(size=16),
                text_color="#6b7280"
            ).pack(pady=30)
            btn_primera = ctk.CTkButton(
                empty_frame,
                text="Cargar Primera Imagen",
                command=self.mostrar_carga_imagen,
                width=200,
                height=40,
                corner_radius=20,
                fg_color="#3b82f6"
            )
            btn_primera.pack(pady=10)

        # Botón actualizar (opcional)
        ctk.CTkButton(
            self.current_frame,
            text="🔄 Actualizar",
            command=self.mostrar_expedientes,
            width=100,
            height=35,
            corner_radius=15,
            fg_color="#9ca3af"
        ).pack(pady=10)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = SistemaDentalApp()
    app.run()