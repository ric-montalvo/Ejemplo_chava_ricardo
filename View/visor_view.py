# view/visor_view.py
import customtkinter as ctk
from PIL import Image

class VisorView(ctk.CTkToplevel):
    def __init__(self, parent, imagenes_procesadas, nombre_paciente, on_volver=None):
        super().__init__(parent)
        self.title("Resultados del Procesamiento")
        self.geometry("1000x700")
        self.transient(parent)
        self.grab_set()

        self.imagenes = imagenes_procesadas
        self.indice = 0
        self.on_volver = on_volver

        ctk.CTkLabel(self, text=f"Resultados - {nombre_paciente}",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=15)
        self.lbl_info = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=14))
        self.lbl_info.pack(pady=5)

        img_frame = ctk.CTkFrame(self, width=900, height=550, fg_color="white", corner_radius=10)
        img_frame.pack(pady=20, padx=20, fill="both", expand=True)
        img_frame.pack_propagate(False)
        self.image_label = ctk.CTkLabel(img_frame, text="")
        self.image_label.pack(fill="both", expand=True)

        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(pady=10)
        ctk.CTkButton(nav_frame, text="◀ Anterior (←)", command=self.anterior, width=140).pack(side="left", padx=20)
        ctk.CTkButton(nav_frame, text="Siguiente (→)", command=self.siguiente, width=140).pack(side="left", padx=20)

        indicador = ctk.CTkLabel(self, text="📸 1. Original | 2. Escala de Grises | 3. Inversión de grises",
                                 font=ctk.CTkFont(size=12), text_color="#6b7280")
        indicador.pack(pady=5)

        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(pady=10)
        ctk.CTkButton(action_frame, text="📋 Ver Expedientes", command=lambda: self.cerrar_y_volver("expedientes"),
                      width=150).pack(side="left", padx=10)
        ctk.CTkButton(action_frame, text="📂 Nueva Imagen", command=lambda: self.cerrar_y_volver("carga"),
                      width=150).pack(side="left", padx=10)
        ctk.CTkButton(action_frame, text="🏠 Menú Principal", command=lambda: self.cerrar_y_volver("menu"),
                      width=150, fg_color="#9ca3af").pack(side="left", padx=10)

        self.bind('<Key>', self.on_key)
        self.actualizar()

    def actualizar(self):
        img_pil, texto = self.imagenes[self.indice]
        max_w, max_h = 850, 500
        img_pil.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
        ctk_img = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(img_pil.width, img_pil.height))
        self.image_label.configure(image=ctk_img, text="")
        self.image_label.image = ctk_img
        total = len(self.imagenes)
        self.lbl_info.configure(text=f"{texto} | Imagen {self.indice+1} de {total}")

    def anterior(self):
        self.indice = (self.indice - 1) % len(self.imagenes)
        self.actualizar()

    def siguiente(self):
        self.indice = (self.indice + 1) % len(self.imagenes)
        self.actualizar()

    def on_key(self, event):
        if event.keysym == 'Left':
            self.anterior()
        elif event.keysym == 'Right':
            self.siguiente()
        elif event.keysym == 'Escape':
            self.cerrar_y_volver("menu")

    def cerrar_y_volver(self, dest):
        self.destroy()
        if self.on_volver:
            self.on_volver(dest)