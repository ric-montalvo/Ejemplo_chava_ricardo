# view/expedientes_view.py
import customtkinter as ctk
from tkinter import messagebox
from utils.helpers import formatear_fecha

class ExpedientesView(ctk.CTkFrame):
    def __init__(self, parent, controller, expedientes):
        super().__init__(parent, fg_color="white")
        self.controller = controller
        self.pack(fill="both", expand=True)

        # Guardar lista completa de expedientes
        self.todos_expedientes = expedientes  # lista de Paths

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

        # Filtros: búsqueda y orden
        filtros_frame = ctk.CTkFrame(self, fg_color="transparent")
        filtros_frame.pack(fill="x", padx=40, pady=10)

        self.entry_buscar = ctk.CTkEntry(filtros_frame, placeholder_text="Buscar por nombre...",
                                         width=250, height=35, corner_radius=15,
                                         border_color="#d1d5db")
        self.entry_buscar.pack(side="left", padx=5)
        self.entry_buscar.bind('<KeyRelease>', self.on_search)

        self.combo_orden = ctk.CTkOptionMenu(filtros_frame,
                                             values=["Más recientes", "Más antiguos", "A-Z", "Z-A"],
                                             width=150, height=35, corner_radius=15,
                                             fg_color="#f3f4f6", button_color="#3b82f6",
                                             command=self.on_order_change)
        self.combo_orden.pack(side="right", padx=5)
        self.combo_orden.set("Más recientes")

        # Contenedor de lista de expedientes (scroll)
        self.lista_frame = ctk.CTkScrollableFrame(self, width=800, height=450,
                                                  fg_color="transparent")
        self.lista_frame.pack(pady=20, padx=40, fill="both", expand=True)

        # Botones abajo: Actualizar + Nuevo
        botones_frame = ctk.CTkFrame(self, fg_color="transparent")
        botones_frame.pack(pady=10)

        ctk.CTkButton(botones_frame, text="🔄 Actualizar",
                      command=self.refrescar_lista,
                      width=100, height=35, corner_radius=15,
                      fg_color="#9ca3af", hover_color="#6b7280").pack(side="left", padx=10)

        ctk.CTkButton(botones_frame, text="+ Nuevo",
                      command=self.controller.mostrar_carga,
                      width=100, height=35, corner_radius=15,
                      fg_color="#10b981", hover_color="#059669",
                      font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=10)

        # Dibujar lista inicial
        self.actualizar_lista()

    def on_search(self, event):
        self.actualizar_lista()

    def on_order_change(self, choice):
        self.actualizar_lista()

    def refrescar_lista(self):
        self.todos_expedientes = self.controller.obtener_expedientes()
        self.actualizar_lista()

    def actualizar_lista(self):
        """Filtra, ordena y redibuja las tarjetas de expedientes"""
        texto = self.entry_buscar.get().strip().lower()
        filtrados = [c for c in self.todos_expedientes if texto in c.name.lower()]

        orden = self.combo_orden.get()
        if orden == "Más recientes":
            filtrados.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        elif orden == "Más antiguos":
            filtrados.sort(key=lambda x: x.stat().st_mtime)
        elif orden == "A-Z":
            filtrados.sort(key=lambda x: x.name.lower())
        elif orden == "Z-A":
            filtrados.sort(key=lambda x: x.name.lower(), reverse=True)

        self.redibujar_lista(filtrados)

    def redibujar_lista(self, expedientes):
        """Dibuja las tarjetas en el lista_frame"""
        for widget in self.lista_frame.winfo_children():
            widget.destroy()

        if not expedientes:
            empty_frame = ctk.CTkFrame(self.lista_frame, fg_color="transparent")
            empty_frame.pack(expand=True)
            ctk.CTkLabel(empty_frame, text="📂 No hay expedientes registrados",
                         font=ctk.CTkFont(size=16), text_color="#6b7280").pack(pady=30)
            return

        for carpeta in expedientes:
            self.crear_tarjeta(carpeta)

    # ---------- Tarjetas principales y expansión ----------
    def crear_tarjeta(self, carpeta, parent_frame=None, nivel=0):
        if parent_frame is None:
            parent_frame = self.lista_frame

        # Detectar subcarpetas válidas
        subcarpetas = []
        for subdir in carpeta.iterdir():
            if subdir.is_dir() and any("_original." in f.name for f in subdir.glob("*")):
                subcarpetas.append(subdir)

        fecha_mod = formatear_fecha(carpeta.stat().st_mtime)
        archivos = list(carpeta.glob("*"))
        num_piezas = len([f for f in archivos if "invertida" in f.name]) * 8

        # Tarjeta principal
        card = ctk.CTkFrame(parent_frame, corner_radius=15, border_width=1,
                            border_color="#e5e7eb", fg_color="white")
        card.pack(fill="x", pady=(8 if nivel == 0 else 4), padx=(20 if nivel == 0 else 40), expand=False)

        # Frame superior (info + botones)
        top_frame = ctk.CTkFrame(card, fg_color="transparent")
        top_frame.pack(fill="x", padx=15, pady=12)

        # Parte izquierda: información
        info_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)

        if nivel > 0:
            ctk.CTkLabel(info_frame, text="  " * nivel, font=ctk.CTkFont(size=12)).pack(side="left")

        ctk.CTkLabel(info_frame, text=carpeta.name, font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(info_frame, text=f"{fecha_mod}  |  {num_piezas} piezas segmentadas",
                     font=ctk.CTkFont(size=12), text_color="#6b7280").pack(anchor="w")

        # Parte derecha: botones
        botones_card = ctk.CTkFrame(top_frame, fg_color="transparent")
        botones_card.pack(side="right")

        btn_ver = ctk.CTkButton(botones_card, text="Ver Detalles", width=110, height=35,
                                corner_radius=15, fg_color="#3b82f6",
                                hover_color="#2563eb",
                                command=lambda c=carpeta: self.controller.ver_detalles(c))
        btn_ver.pack(side="left", padx=5)

        if nivel == 0:
            btn_eliminar = ctk.CTkButton(botones_card, text="🗑️", width=40, height=35,
                                         corner_radius=15, fg_color="#ef4444",
                                         hover_color="#dc2626",
                                         command=lambda c=carpeta: self.confirmar_eliminacion(c))
            btn_eliminar.pack(side="left", padx=5)

        # Frame interno para subcarpetas (inicialmente vacío)
        sub_frame = None

        # Botón de expansión (solo si hay subcarpetas y es nivel raíz)
        if subcarpetas and nivel == 0:
            expandido = False
            btn_expand = ctk.CTkButton(botones_card, text="▼", width=40, height=35,
                                       corner_radius=15, fg_color="#6b7280",
                                       hover_color="#4b5563",
                                       command=lambda: toggle_expand())
            btn_expand.pack(side="left", padx=5)

            def toggle_expand():
                nonlocal sub_frame, expandido
                if expandido:
                    # Contraer: destruir el frame de subcarpetas
                    if sub_frame:
                        sub_frame.destroy()
                        sub_frame = None
                    btn_expand.configure(text="▼")
                else:
                    # Expandir: crear frame de subcarpetas dentro de card (debajo de top_frame)
                    sub_frame = ctk.CTkFrame(card, fg_color="transparent")
                    sub_frame.pack(fill="x", padx=15, pady=(0, 12))
                    for sub in subcarpetas:
                        self.crear_tarjeta_simple(sub, sub_frame, nivel=1)
                    btn_expand.configure(text="▲")
                expandido = not expandido

        return card

    def crear_tarjeta_simple(self, carpeta, parent_frame, nivel=1):
        """Crea una tarjeta para subcarpetas (sin botones de acción, solo información)"""
        fecha_mod = formatear_fecha(carpeta.stat().st_mtime)
        archivos = list(carpeta.glob("*"))
        num_piezas = len([f for f in archivos if "invertida" in f.name]) * 8

        card = ctk.CTkFrame(parent_frame, corner_radius=12, border_width=1,
                            border_color="#e5e7eb", fg_color="#f9fafb")
        card.pack(fill="x", pady=4, padx=(30 if nivel == 1 else 50), expand=False)

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=8)

        ctk.CTkLabel(info_frame, text=carpeta.name, font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(info_frame, text=f"{fecha_mod}  |  {num_piezas} piezas segmentadas",
                     font=ctk.CTkFont(size=11), text_color="#6b7280").pack(anchor="w")

        # No se agregan botones de ver detalles ni eliminar
        return card

    # ---------- Métodos existentes (mostrar_detalle, confirmar_eliminacion, etc.) ----------
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
        """Diálogo de confirmación de eliminación (solo para carpetas raíz)"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirmar Eliminación")
        dialog.geometry("400x180")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (180 // 2)
        dialog.geometry(f"+{x}+{y}")

        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(frame, text="Confirmar Eliminación",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 10))

        ctk.CTkLabel(frame, text="¿Estás seguro de que deseas eliminar este expediente?",
                     font=ctk.CTkFont(size=12)).pack()
        ctk.CTkLabel(frame, text="Esta acción no se puede deshacer.",
                     font=ctk.CTkFont(size=12)).pack(pady=(5, 15))

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack()

        ctk.CTkButton(btn_frame, text="Cancelar", width=100,
                      command=dialog.destroy).pack(side="left", padx=10)

        ctk.CTkButton(btn_frame, text="Confirmar", width=100,
                      fg_color="#ef4444", hover_color="#dc2626",
                      command=lambda: self.controller.eliminar_expediente(carpeta, dialog)).pack(side="left", padx=10)