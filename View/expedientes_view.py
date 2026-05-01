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
                      width=80, height=35, corner_radius=15, fg_color="#9ca3af",
                      hover_color="#6b7280").pack(side="left")

        # Título
        ctk.CTkLabel(self, text="Expedientes de Pacientes",
                     font=ctk.CTkFont(size=28, weight="bold"),
                     text_color="#1f2937").pack(pady=20)

        # Filtros (barra de búsqueda y orden - UI solamente por ahora)
        filtros_frame = ctk.CTkFrame(self, fg_color="transparent")
        filtros_frame.pack(fill="x", padx=40, pady=10)

        entry_buscar = ctk.CTkEntry(filtros_frame, placeholder_text="Buscar por nombre...",
                                    width=250, height=35, corner_radius=15,
                                    border_color="#d1d5db")
        entry_buscar.pack(side="left", padx=5)

        combo_orden = ctk.CTkOptionMenu(filtros_frame,
                                        values=["Más recientes", "Más antiguos", "A-Z", "Z-A"],
                                        width=150, height=35, corner_radius=15,
                                        fg_color="#f3f4f6", button_color="#3b82f6")
        combo_orden.pack(side="right", padx=5)

        # Contenedor de lista de expedientes (scroll)
        lista_frame = ctk.CTkScrollableFrame(self, width=800, height=450,
                                             fg_color="transparent")
        lista_frame.pack(pady=20, padx=40, fill="both", expand=True)

        if not expedientes:
            empty_frame = ctk.CTkFrame(lista_frame, fg_color="transparent")
            empty_frame.pack(expand=True)
            ctk.CTkLabel(empty_frame, text="📂 No hay expedientes registrados",
                         font=ctk.CTkFont(size=16), text_color="#6b7280").pack(pady=30)
        else:
            for carpeta in expedientes:
                fecha_mod = formatear_fecha(carpeta.stat().st_mtime)
                archivos = list(carpeta.glob("*"))
                num_piezas = len([f for f in archivos if "invertida" in f.name]) * 8

                # Tarjeta del expediente
                card = ctk.CTkFrame(lista_frame, corner_radius=15, border_width=1,
                                    border_color="#e5e7eb", fg_color="white")
                card.pack(fill="x", pady=8, padx=10)

                info_frame = ctk.CTkFrame(card, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=12)

                ctk.CTkLabel(info_frame, text=carpeta.name,
                             font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")
                ctk.CTkLabel(info_frame, text=f"{fecha_mod}  |  {num_piezas} piezas segmentadas",
                             font=ctk.CTkFont(size=12), text_color="#6b7280").pack(anchor="w")

                # Frame para botones (Ver Detalles + Eliminar)
                botones_card = ctk.CTkFrame(card, fg_color="transparent")
                botones_card.pack(side="right", padx=15)

                # Botón Ver Detalles
                btn_ver = ctk.CTkButton(botones_card, text="Ver Detalles", width=110, height=35,
                                        corner_radius=15, fg_color="#3b82f6",
                                        hover_color="#2563eb",
                                        command=lambda c=carpeta: self.mostrar_detalle(c))
                btn_ver.pack(side="left", padx=5)

                # Botón Eliminar (ícono 🗑️)
                btn_eliminar = ctk.CTkButton(botones_card, text="🗑️", width=40, height=35,
                                             corner_radius=15, fg_color="#ef4444",
                                             hover_color="#dc2626",
                                             command=lambda c=carpeta: self.confirmar_eliminacion(c))
                btn_eliminar.pack(side="left", padx=5)

        # Botones abajo: Actualizar + Nuevo
        botones_frame = ctk.CTkFrame(self, fg_color="transparent")
        botones_frame.pack(pady=10)

        ctk.CTkButton(botones_frame, text="🔄 Actualizar",
                      command=self.controller.mostrar_expedientes,
                      width=100, height=35, corner_radius=15,
                      fg_color="#9ca3af", hover_color="#6b7280").pack(side="left", padx=10)

        ctk.CTkButton(botones_frame, text="+ Nuevo",
                      command=self.controller.mostrar_carga,
                      width=100, height=35, corner_radius=15,
                      fg_color="#10b981", hover_color="#059669",
                      font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=10)

    def mostrar_detalle(self, carpeta):
        archivos = list(carpeta.glob("*"))
        archivos_str = "\n".join([f"  - {a.name}" for a in archivos[:8]])
        if len(archivos) > 8:
            archivos_str += f"\n  ... y {len(archivos) - 8} más"

        invertida = next((f for f in archivos if "invertida" in f.name.lower()), None)
        grises = next((f for f in archivos if "grises" in f.name.lower()), None)

        invertida_info = f"\n🖼️ Imagen invertida: {invertida.name}" if invertida else ""
        grises_info = f"\n🌫️ Escala de grises: {grises.name}" if grises else ""

        messagebox.showinfo(
            "Detalles del Expediente",
            f"📁 {carpeta.name}\n\n"
            f"📅 Fecha: {formatear_fecha(carpeta.stat().st_mtime)}\n"
            f"📄 Archivos: {len(archivos)}{invertida_info}{grises_info}\n\n"
            f"📋 Contenido:\n{archivos_str}"
        )

    def confirmar_eliminacion(self, carpeta):
        """Diálogo de confirmación de eliminación"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirmar Eliminación")
        dialog.geometry("400x180")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)

        # Centrar ventana
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (180 // 2)
        dialog.geometry(f"+{x}+{y}")

        # Frame principal
        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Título
        ctk.CTkLabel(frame, text="Confirmar Eliminación",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 10))

        # Mensaje
        ctk.CTkLabel(frame, text="¿Estás seguro de que deseas eliminar este expediente?",
                     font=ctk.CTkFont(size=12)).pack()
        ctk.CTkLabel(frame, text="Esta acción no se puede deshacer.",
                     font=ctk.CTkFont(size=12)).pack(pady=(5, 15))

        # Botones
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack()

        ctk.CTkButton(btn_frame, text="Cancelar", width=100,
                      command=dialog.destroy).pack(side="left", padx=10)

        ctk.CTkButton(btn_frame, text="Confirmar", width=100,
                      fg_color="#ef4444", hover_color="#dc2626",
                      command=lambda: self.controller.eliminar_expediente(carpeta, dialog)).pack(side="left", padx=10)