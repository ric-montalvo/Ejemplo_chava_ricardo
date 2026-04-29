# view/main_window.py
import customtkinter as ctk

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Segmentación Dental")
        self.geometry("1100x750")
        self.minsize(900, 600)

        self.current_view = None

    def cambiar_vista(self, nueva_vista):
        if self.current_view:
            self.current_view.destroy()
        self.current_view = nueva_vista
        self.current_view.pack(fill="both", expand=True)