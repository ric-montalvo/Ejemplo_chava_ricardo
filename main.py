# main.py (en la raíz)
import customtkinter as ctk

from Controller.app_controller import AppController


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

if __name__ == "__main__":
    app = AppController()
    app.run()