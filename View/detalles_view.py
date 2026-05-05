# view/detalles_view.py
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
from pathlib import Path
from utils.helpers import formatear_fecha

class DetallesView(ctk.CTkToplevel):
    def __init__(self, parent, controller, carpeta_raiz):
        super().__init__(parent)
        self.controller = controller
        self.carpeta_raiz = carpeta_raiz
        self.carpeta_actual = carpeta_raiz  # la que se muestra actualmente
        self.title("Detalles del Expediente")
        self.geometry("1000x750")
        self.transient(parent)
        self.grab_set()

        self._crear_widgets()
        self._cargar_datos(self.carpeta_actual)
        self._actualizar_lista_subcarpetas()

    # ---------- Construcción de la interfaz ----------
    def _crear_widgets(self):
        # Grid principal: fila 0: botón volver, fila 1: contenido, fila 2: subcarpetas
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Botón volver
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        ctk.CTkButton(top_frame, text="← Volver", width=80, command=self.destroy).pack(side="left")

        # Contenedor principal para contenido (dos columnas: izquierda info+tabla, derecha imagen)
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=3)   # izquierda
        self.main_frame.grid_columnconfigure(1, weight=2)   # derecha
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Panel izquierdo (información + tabla)
        left_panel = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Tarjeta de información del paciente
        info_frame = ctk.CTkFrame(left_panel, corner_radius=15, border_width=1, border_color="#e5e7eb", fg_color="white")
        info_frame.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(info_frame, text="Información del Paciente", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=20, pady=(15, 5))
        ctk.CTkLabel(info_frame, text="Nombre", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=20)
        self.nombre_label = ctk.CTkLabel(info_frame, text="", font=ctk.CTkFont(size=14))
        self.nombre_label.pack(anchor="w", padx=20)

        ctk.CTkLabel(info_frame, text="Fecha de Procesamiento", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=20, pady=(10, 0))
        self.fecha_label = ctk.CTkLabel(info_frame, text="", font=ctk.CTkFont(size=14))
        self.fecha_label.pack(anchor="w", padx=20)

        ctk.CTkLabel(info_frame, text="Estadísticas", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=20, pady=(10, 0))
        self.piezas_label = ctk.CTkLabel(info_frame, text="", font=ctk.CTkFont(size=14))
        self.piezas_label.pack(anchor="w", padx=20, pady=(0, 15))

        ctk.CTkButton(info_frame, text="Descargar CSV", width=150, fg_color="#10b981", command=self._descargar_csv).pack(anchor="w", padx=20, pady=(5, 15))

        # Tabla (scrollable, de momento vacía)
        self.tabla_frame = ctk.CTkScrollableFrame(left_panel, height=300, fg_color="transparent")
        self.tabla_frame.pack(fill="both", expand=True, pady=(10, 0))

        # Panel derecho (imagen)
        right_panel = ctk.CTkFrame(self.main_frame, corner_radius=15, border_width=1, border_color="#e5e7eb", fg_color="white")
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(right_panel, text="Radiografía Procesada", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=10)

        self.img_container = ctk.CTkFrame(right_panel, fg_color="transparent")
        self.img_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.img_container.grid_rowconfigure(0, weight=1)
        self.img_container.grid_columnconfigure(0, weight=1)

        self.imagen_label = ctk.CTkLabel(self.img_container, text="")
        self.imagen_label.grid(row=0, column=0, sticky="nsew")

        # ---------- Sección de subcarpetas (horizontal) ----------
        sub_frame = ctk.CTkFrame(self, fg_color="transparent")
        sub_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))

        ctk.CTkLabel(sub_frame, text="Procesamiento Adicional", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")

        # Scrollable horizontal para las tarjetas de subcarpetas
        self.sub_scroll = ctk.CTkScrollableFrame(sub_frame, height=120, orientation="horizontal", fg_color="transparent")
        self.sub_scroll.pack(fill="x", pady=5)
        self.subcarpetas_container = self.sub_scroll  # frame donde se pondrán las tarjetas

    # ---------- Carga de datos de la carpeta actual ----------
    def _cargar_datos(self, carpeta: Path):
        self.carpeta_actual = carpeta
        self.nombre_label.configure(text=carpeta.name)
        self.fecha_label.configure(text=formatear_fecha(carpeta.stat().st_mtime))

        archivos = list(carpeta.glob("*"))
        num_piezas = len([f for f in archivos if "invertida" in f.name]) * 8
        self.piezas_label.configure(text=f"{num_piezas} piezas dentales segmentadas")

        # Imagen invertida
        invertida_path = next((f for f in archivos if "invertida" in f.name.lower()), None)
        if invertida_path and invertida_path.exists():
            img = Image.open(invertida_path)
            max_width = 250
            if img.width > max_width:
                ratio = max_width / img.width
                new_size = (max_width, int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
            self.imagen_label.configure(image=ctk_img, text="")
            self.imagen_label.image = ctk_img
        else:
            self.imagen_label.configure(text="Sin imagen procesada", text_color="gray")

        # Resaltar visualmente la carpeta activa en la lista de subcarpetas (opcional)
        self._marcar_activo_en_lista()

    # ---------- Construcción de la lista horizontal de subcarpetas ----------
    def _actualizar_lista_subcarpetas(self):
        # Limpiar contenedor
        for widget in self.subcarpetas_container.winfo_children():
            widget.destroy()

        # Obtener todas las subcarpetas (directorios dentro de la carpeta raíz)
        # pero excluyendo la carpeta raíz misma
        subcarpetas = [sub for sub in self.carpeta_raiz.iterdir() if sub.is_dir() and sub != self.carpeta_raiz]

        # Siempre agregar un botón para la carpeta raíz (si no estamos ya en ella)
        # Este botón permitirá volver a la raíz fácilmente.
        self._agregar_tarjeta_carpeta(self.carpeta_raiz, es_raiz=True)

        for sub in subcarpetas:
            self._agregar_tarjeta_carpeta(sub, es_raiz=False)

        if not subcarpetas:
            ctk.CTkLabel(self.subcarpetas_container, text="No hay subcarpetas").pack(pady=10)

    def _agregar_tarjeta_carpeta(self, carpeta: Path, es_raiz: bool):
        """Crea una tarjeta horizontal para una carpeta (raíz o subcarpeta)"""
        card = ctk.CTkFrame(self.subcarpetas_container, corner_radius=10, border_width=1, border_color="#e5e7eb",
                            fg_color="#f9fafb" if carpeta != self.carpeta_actual else "#dbeafe")
        card.pack(side="left", padx=5, pady=5, fill="y")

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", padx=10, pady=8)

        nombre_text = "📁 Raíz" if es_raiz else carpeta.name
        ctk.CTkLabel(info, text=nombre_text, font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w")

        # Fecha y piezas (mock)
        fecha = formatear_fecha(carpeta.stat().st_mtime)
        archivos = list(carpeta.glob("*"))
        piezas = len([f for f in archivos if "invertida" in f.name]) * 8
        ctk.CTkLabel(info, text=f"{fecha} | {piezas} piezas", font=ctk.CTkFont(size=10)).pack(anchor="w")

        btn = ctk.CTkButton(card, text="VER", width=50, height=28,
                            command=lambda c=carpeta: self._cambiar_carpeta_activa(c))
        btn.pack(side="right", padx=10)

    def _cambiar_carpeta_activa(self, nueva_carpeta: Path):
        """Cambia la carpeta que se muestra en la vista principal y actualiza el resaltado"""
        if nueva_carpeta == self.carpeta_actual:
            return
        self._cargar_datos(nueva_carpeta)
        # Refrescar la lista de subcarpetas para actualizar el resaltado
        self._actualizar_lista_subcarpetas()

    def _marcar_activo_en_lista(self):
        """Resalta la tarjeta correspondiente a la carpeta actual"""
        # Esta función se llamará después de cada cambio para recolorear
        # Es más eficiente simplemente reconstruir la lista (ya lo hacemos en _cambiar_carpeta_activa).
        pass

    # ---------- Exportar CSV ----------
    def _descargar_csv(self):
        csv_path = self.carpeta_actual / "metricas.csv"
        if not csv_path.exists():
            messagebox.showerror("Error", "CSV no encontrado en esta carpeta")
            return
        destino = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if destino:
            import shutil
            shutil.copy2(csv_path, destino)
            messagebox.showinfo("Éxito", "CSV exportado")