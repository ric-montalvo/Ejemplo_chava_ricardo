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
        # 1. Crear carpeta del paciente
        carpeta = self.file_manager.crear_carpeta_paciente(nombre_paciente)
        # 2. Copiar imagen original
        ruta_copia = self.file_manager.copiar_original(ruta_imagen, carpeta, nombre_paciente)

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
            # Llamar al modelo actual (placeholder de Montoya)
            self.imagenes_procesadas = self.modelo.procesar_pipeline(str(ruta_copia))
            # Guardar la imagen en grises
            if len(self.imagenes_procesadas) >= 2:
                img_gris, _ = self.imagenes_procesadas[1]
                self.file_manager.guardar_imagen_grises(img_gris, carpeta, nombre_paciente)

            progress.destroy()
            # Mostrar visor
            VisorView(self.root, self.imagenes_procesadas, nombre_paciente, self.on_visor_cerrado)
        except Exception as e:
            progress.destroy()
            messagebox.showerror("Error", f"Error al procesar:\n{str(e)}")

    def on_visor_cerrado(self, destino):
        if destino == "menu":
            self.mostrar_menu()
        elif destino == "carga":
            self.mostrar_carga()
        elif destino == "expedientes":
            self.mostrar_expedientes()

    def run(self):
        self.root.mainloop()