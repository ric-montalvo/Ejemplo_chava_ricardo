import customtkinter as ctk
from PIL import Image
import os


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Segmentación Dental")
        self.geometry("950x650")
        self.minsize(800, 600)

        self.current_view = None
        self.agregar_logos()

    def agregar_logos(self):
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        ruta_logo = os.path.join(directorio_actual, "..", "Assets", "logo.png")

        try:
            imagen_pil = Image.open(ruta_logo)
            logo_image = ctk.CTkImage(light_image=imagen_pil, dark_image=imagen_pil, size=(120, 120))

            self.logo_label = ctk.CTkLabel(self, image=logo_image, text="")
            self.logo_label.place(relx=0.0, rely=1.0, anchor="sw", x=15, y=0)

        except FileNotFoundError:
            print(f"Error: No se encontró la imagen en: {ruta_logo}")

    def cambiar_vista(self, nueva_vista):
        if self.current_view:
            self.current_view.destroy()

        self.current_view = nueva_vista
        self.current_view.pack(fill="both", expand=True)

        if hasattr(self, 'logo_label'):
            self.logo_label.lift()