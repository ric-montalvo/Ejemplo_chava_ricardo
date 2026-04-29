# view/carga_view.py
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image

class CargaView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="white")
        self.controller = controller
        self.pack(fill="both", expand=True)

        self.nombre_entry = None
        self.ruta_imagen = None
        self.area_carga_frame = None
        self.preview_label = None

        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(self, text="Cargar Radiografía Dental", font=ctk.CTkFont(size=28, weight="bold"),
                     text_color="#1f2937").pack(pady=30)
        ctk.CTkLabel(self, text="Ingresa el nombre del paciente y selecciona la imagen para procesamiento",
                     font=ctk.CTkFont(size=14), text_color="#6b7280").pack(pady=(0, 30))

        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(expand=True)

        ctk.CTkLabel(form_frame, text="Nombre del Paciente", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        self.nombre_entry = ctk.CTkEntry(form_frame, placeholder_text="Ej: Juan Pérez", width=400, height=40,
                                         corner_radius=10, border_width=1, border_color="#d1d5db")
        self.nombre_entry.pack(pady=(5, 20))
        self.nombre_entry.bind('<KeyRelease>', self.validar)

        ctk.CTkLabel(form_frame, text="Imagen de Radiografía", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")

        self.area_carga_frame = ctk.CTkFrame(form_frame, width=400, height=160, corner_radius=15,
                                             border_width=2, border_color="#3b82f6", fg_color="#f0f9ff")
        self.area_carga_frame.pack(pady=10)
        self.area_carga_frame.pack_propagate(False)
        lbl_click = ctk.CTkLabel(self.area_carga_frame, text="📁 Haz clic para seleccionar una imagen\nPNG, JPG o JPEG",
                                 font=ctk.CTkFont(size=12), text_color="#3b82f6")
        lbl_click.pack(expand=True)
        self.area_carga_frame.bind("<Button-1>", lambda e: self.seleccionar_imagen())
        lbl_click.bind("<Button-1>", lambda e: self.seleccionar_imagen())

        self.preview_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        self.preview_label = ctk.CTkLabel(self.preview_frame, text="")
        self.preview_label.pack()
        self.btn_remover = ctk.CTkButton(self.preview_frame, text="✕ Quitar imagen", width=100, height=30,
                                         fg_color="#ef4444", hover_color="#dc2626", command=self.remover_imagen)

        self.lbl_info = ctk.CTkLabel(form_frame, text="", font=ctk.CTkFont(size=12))

        self.btn_procesar = ctk.CTkButton(form_frame, text="Procesar Imagen", command=self.procesar,
                                          width=200, height=45, corner_radius=25, state="disabled",
                                          font=ctk.CTkFont(size=14, weight="bold"), fg_color="#3b82f6")
        self.btn_procesar.pack(pady=30)

        ctk.CTkButton(self, text="← Volver", command=self.controller.volver_menu,
                      width=100, height=35, corner_radius=15, fg_color="#9ca3af").pack(pady=10)

    def seleccionar_imagen(self):
        ruta = filedialog.askopenfilename(filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.bmp")])
        if ruta:
            self.ruta_imagen = ruta
            self.lbl_info.configure(text=f"✅ {ruta.split('/')[-1]}", text_color="#10b981")
            self.area_carga_frame.pack_forget()
            self.preview_frame.pack(pady=10)
            self.btn_remover.pack(pady=5)
            img = Image.open(ruta)
            img.thumbnail((180, 120), Image.Resampling.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
            self.preview_label.configure(image=ctk_img, text="")
            self.preview_label.image = ctk_img
            self.lbl_info.pack()
            self.validar()

    def remover_imagen(self):
        self.ruta_imagen = None
        self.preview_frame.pack_forget()
        self.area_carga_frame.pack(pady=10)
        self.lbl_info.pack_forget()
        self.btn_procesar.configure(state="disabled")
        self.validar()

    def validar(self, event=None):
        nombre = self.nombre_entry.get().strip()
        if nombre and self.ruta_imagen:
            self.btn_procesar.configure(state="normal")
        else:
            self.btn_procesar.configure(state="disabled")

    def procesar(self):
        nombre = self.nombre_entry.get().strip()
        if not nombre or not self.ruta_imagen:
            return
        self.controller.procesar_imagen(nombre, self.ruta_imagen)