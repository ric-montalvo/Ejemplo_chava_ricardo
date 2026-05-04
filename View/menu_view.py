# view/menu_view.py
import customtkinter as ctk

class MenuView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.pack(expand=True, fill="both")

        # Título
        ctk.CTkLabel(
            self, text="Sistema de Segmentación Dental",
            font=ctk.CTkFont(size=32, weight="bold"), text_color="#1f2937"
        ).pack(pady=(40, 10))
        ctk.CTkLabel(
            self, text="Procesamiento automático de radiografías dentales",
            font=ctk.CTkFont(size=16), text_color="#6b7280"
        ).pack(pady=(0, 60))

        tarjetas_frame = ctk.CTkFrame(self, fg_color="transparent")
        tarjetas_frame.pack(expand=True)

        # ========== Tarjeta Ver Expedientes (única, sin botón azul) ==========
        card_exp = ctk.CTkFrame(tarjetas_frame, width=320, height=280, corner_radius=20,
                                border_width=1, border_color="#e5e7eb", fg_color="white")
        card_exp.pack(side="left", padx=30, expand=True)
        card_exp.pack_propagate(False)

        # ✅ Hacer que TODO el cuadrado blanco sea cliqueable
        def on_card_click(event=None):
            self.controller.mostrar_expedientes()

        card_exp.bind("<Button-1>", on_card_click)

        # Hacer también cliqueables los elementos internos (para mejor experiencia)
        for child in card_exp.winfo_children():
            child.bind("<Button-1>", on_card_click)

        # Contenido de la tarjeta (sin botón azul)
        ctk.CTkLabel(card_exp, text="📋", font=ctk.CTkFont(size=48)).pack(pady=(30, 10))
        ctk.CTkLabel(card_exp, text="Ver Expedientes", font=ctk.CTkFont(size=20, weight="bold")).pack()
        ctk.CTkLabel(card_exp, text="Consulta y administra los registros de pacientes",
                     font=ctk.CTkFont(size=12), wraplength=260, text_color="#6b7280").pack(pady=(10, 20))

        # ✅ Opcional: cambiar cursor a mano al pasar sobre la tarjeta
        card_exp.bind("<Enter>", lambda e: card_exp.configure(cursor="hand2"))
        card_exp.bind("<Leave>", lambda e: card_exp.configure(cursor=""))