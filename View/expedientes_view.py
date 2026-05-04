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

        # Entry de búsqueda con manejo de foco
        self.entry_buscar = ctk.CTkEntry(filtros_frame, placeholder_text="Buscar por nombre...",
                                         width=250, height=35, corner_radius=15,
                                         border_color="#d1d5db")
        self.entry_buscar.pack(side="left", padx=5)
        self.entry_buscar.bind('<KeyRelease>', self.on_search)
        self.entry_buscar.bind("<FocusIn>", self.on_entry_focus)
        self.entry_buscar.bind("<FocusOut>", self.on_entry_blur)

        self.combo_orden = ctk.CTkOptionMenu(filtros_frame,
                                             values=["Más recientes", "Más antiguos", "A-Z", "Z-A"],
                                             width=150, height=35, corner_radius=15,
                                             fg_color="#f3f4f6", button_color="#3b82f6",
                                             command=self.on_order_change)
        self.combo_orden.pack(side="right", padx=5)
        self.combo_orden.set("Más recientes")  # valor por defecto

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

        # Binding global para quitar el foco del entry al hacer clic fuera
        self.bind("<Button-1>", self.on_root_click)

        # Dibujar lista inicial
        self.actualizar_lista()

    # ================== Eventos del Entry ==================
    def on_entry_focus(self, event):
        self.entry_buscar.configure(border_color="#3b82f6")  # Azul de foco

    def on_entry_blur(self, event):
        # Si el entry no tiene texto y no está activo, el placeholder se mostrará solo
        self.entry_buscar.configure(border_color="#d1d5db")  # Gris normal

    def on_root_click(self, event):
        """Quitar el foco del entry si se hace clic fuera de él (en el frame principal)"""
        if event.widget != self.entry_buscar:
            self.focus_set()  # Quita el foco del entry
            self.entry_buscar.configure(border_color="#d1d5db")

    # ================== Búsqueda y ordenamiento ==================
    def on_search(self, event):
        self.actualizar_lista()

    def on_order_change(self, choice):
        self.actualizar_lista()

    def refrescar_lista(self):
        """Recarga la lista completa desde el controlador y actualiza la vista"""
        self.todos_expedientes = self.controller.obtener_expedientes()
        self.actualizar_lista()

    def actualizar_lista(self):
        """Filtra, ordena y redibuja las tarjetas de expedientes"""
        texto = self.entry_buscar.get().strip().lower()
        # Filtrar por nombre de carpeta (case-insensitive)
        filtrados = [c for c in self.todos_expedientes if texto in c.name.lower()]

        # Ordenar según el combo
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
        # Limpiar frame
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

    # ================== Tarjetas ==================
    def crear_tarjeta(self, carpeta):
        """Crea una tarjeta individual de expediente"""
        fecha_mod = formatear_fecha(carpeta.stat().st_mtime)
        archivos = list(carpeta.glob("*"))
        num_piezas = len([f for f in archivos if "invertida" in f.name]) * 8

        card = ctk.CTkFrame(self.lista_frame, corner_radius=15, border_width=1,
                            border_color="#e5e7eb", fg_color="white")
        card.pack(fill="x", pady=8, padx=10)

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=12)

        ctk.CTkLabel(info_frame, text=carpeta.name,
                     font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(info_frame, text=f"{fecha_mod}  |  {num_piezas} piezas segmentadas",
                     font=ctk.CTkFont(size=12), text_color="#6b7280").pack(anchor="w")

        # Frame para botones
        botones_card = ctk.CTkFrame(card, fg_color="transparent")
        botones_card.pack(side="right", padx=15)

        # Botón Ver Detalles
        btn_ver = ctk.CTkButton(botones_card, text="Ver Detalles", width=110, height=35,
                                corner_radius=15, fg_color="#3b82f6",
                                hover_color="#2563eb",
                                command=lambda c=carpeta: self.mostrar_detalle(c))
        btn_ver.pack(side="left", padx=5)

        # Botón Eliminar
        btn_eliminar = ctk.CTkButton(botones_card, text="🗑️", width=40, height=35,
                                     corner_radius=15, fg_color="#ef4444",
                                     hover_color="#dc2626",
                                     command=lambda c=carpeta: self.confirmar_eliminacion(c))
        btn_eliminar.pack(side="left", padx=5)

    # ================== Detalles y eliminación ==================
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