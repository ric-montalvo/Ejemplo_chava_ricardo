# view/expedientes_view.py
import customtkinter as ctk
from tkinter import messagebox
from utils.helpers import formatear_fecha

class ExpedientesView(ctk.CTkFrame):
    def __init__(self, parent, controller, expedientes):
        super().__init__(parent, fg_color="white")
        self.controller = controller
        self.pack(fill="both", expand=True)

        # Barra superior con volver
        top_bar = ctk.CTkFrame(self, fg_color="transparent", height=50)
        top_bar.pack(fill="x", padx=30, pady=(20, 0))
        ctk.CTkButton(top_bar, text="← Volver", command=self.controller.volver_menu,
                      width=80, height=35, corner_radius=15, fg_color="#9ca3af").pack(side="left")

        ctk.CTkLabel(self, text="Expedientes de Pacientes", font=ctk.CTkFont(size=28, weight="bold"),
                     text_color="#1f2937").pack(pady=20)

        # Filtros (solo UI)
        filtros_frame = ctk.CTkFrame(self, fg_color="transparent")
        filtros_frame.pack(fill="x", padx=40, pady=10)
        ctk.CTkEntry(filtros_frame, placeholder_text="Buscar por nombre...", width=250, height=35,
                     corner_radius=15, border_color="#d1d5db").pack(side="left", padx=5)
        ctk.CTkOptionMenu(filtros_frame, values=["Más recientes"], width=150, height=35,
                          corner_radius=15, fg_color="#f3f4f6", button_color="#3b82f6").pack(side="right", padx=5)

        lista_frame = ctk.CTkScrollableFrame(self, width=800, height=450, fg_color="transparent")
        lista_frame.pack(pady=20, padx=40, fill="both", expand=True)

        if not expedientes:
            empty = ctk.CTkFrame(lista_frame, fg_color="transparent")
            empty.pack(expand=True)
            ctk.CTkLabel(empty, text="📂 No hay expedientes registrados", font=ctk.CTkFont(size=16),
                         text_color="#6b7280").pack(pady=30)
            ctk.CTkButton(empty, text="Cargar Primera Imagen", command=self.controller.mostrar_carga,
                          width=200, height=40, corner_radius=20, fg_color="#3b82f6").pack(pady=10)
        else:
            for carpeta in expedientes:
                fecha_mod = formatear_fecha(carpeta.stat().st_mtime)
                archivos = list(carpeta.glob("*"))
                num_piezas = len([f for f in archivos if "invertida" in f.name]) * 8

                card = ctk.CTkFrame(lista_frame, corner_radius=15, border_width=1, border_color="#e5e7eb", fg_color="white")
                card.pack(fill="x", pady=8, padx=10)

                info = ctk.CTkFrame(card, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True, padx=15, pady=12)
                ctk.CTkLabel(info, text=carpeta.name, font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")
                ctk.CTkLabel(info, text=f"{fecha_mod}  |  {num_piezas} piezas segmentadas",
                             font=ctk.CTkFont(size=12), text_color="#6b7280").pack(anchor="w")

                btn_ver = ctk.CTkButton(card, text="Ver Detalles", width=110, height=35, corner_radius=15,
                                        fg_color="#3b82f6", command=lambda c=carpeta: self.mostrar_detalle(c))
                btn_ver.pack(side="right", padx=15)

        ctk.CTkButton(self, text="🔄 Actualizar", command=self.controller.mostrar_expedientes,
                      width=100, height=35, corner_radius=15, fg_color="#9ca3af").pack(pady=10)

    def mostrar_detalle(self, carpeta):
        archivos = list(carpeta.glob("*"))
        archivos_str = "\n".join([f"  - {a.name}" for a in archivos[:8]])
        if len(archivos) > 8:
            archivos_str += f"\n  ... y {len(archivos)-8} más"
        invertida = next((f for f in archivos if "invertida" in f.name.lower()), None)
        grises = next((f for f in archivos if "grises" in f.name.lower()), None)
        invertida_info = f"\n🖼️ Invertida: {invertida.name}" if invertida else ""
        grises_info = f"\n🌫️ Grises: {grises.name}" if grises else ""
        messagebox.showinfo("Detalles", f"📁 {carpeta.name}\n\n📅 Fecha: {formatear_fecha(carpeta.stat().st_mtime)}\n📄 Archivos: {len(archivos)}{invertida_info}{grises_info}\n\n📋 Contenido:\n{archivos_str}")