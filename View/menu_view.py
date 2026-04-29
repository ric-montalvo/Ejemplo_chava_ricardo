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

        # ========== TARJETA "CARGAR IMAGEN" - ELIMINADA ==========
        # Ya no está la tarjeta de cargar imagen

        # Tarjeta Ver Expedientes (única)
        card_exp = ctk.CTkFrame(tarjetas_frame, width=320, height=280, corner_radius=20,
                                border_width=1, border_color="#e5e7eb", fg_color="white")
        card_exp.pack(side="left", padx=30, expand=True)
        card_exp.pack_propagate(False)
        ctk.CTkLabel(card_exp, text="📋", font=ctk.CTkFont(size=48)).pack(pady=(30, 10))
        ctk.CTkLabel(card_exp, text="Ver Expedientes", font=ctk.CTkFont(size=20, weight="bold")).pack()
        ctk.CTkLabel(card_exp, text="Consulta y administra los registros de pacientes",
                     font=ctk.CTkFont(size=12), wraplength=260, text_color="#6b7280").pack(pady=(10, 20))
        ctk.CTkButton(card_exp, text="Ver Registros", command=self.controller.mostrar_expedientes,
                      width=180, height=40, corner_radius=20, fg_color="#3b82f6").pack(pady=10)