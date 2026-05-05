# view/detalles_view.py
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
from pathlib import Path
from utils.helpers import formatear_fecha
import csv

class DetallesView(ctk.CTkToplevel):
    def __init__(self, parent, controller, carpeta_raiz):
        super().__init__(parent)
        self.controller = controller
        self.carpeta_raiz = carpeta_raiz
        self.carpeta_actual = carpeta_raiz
        self.title("Detalles del Expediente")
        self.geometry("1000x750")
        self.transient(parent)
        self.grab_set()

        self._crear_widgets()
        self._cargar_datos(self.carpeta_actual)
        self._actualizar_lista_subcarpetas()

    # ---------- Construcción de la interfaz ----------
    def _crear_widgets(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Botón volver
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        ctk.CTkButton(top_frame, text="← Volver", width=80, command=self.destroy).pack(side="left")

        # Contenedor principal (un solo panel para info, imagen y tabla)
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)  # fila de la tabla expandible

        # Panel superior: información + imagen (en horizontal)
        top_panel = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_panel.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        top_panel.grid_columnconfigure(0, weight=1)  # info
        top_panel.grid_columnconfigure(1, weight=0)  # imagen (no se expande)

        # ---------- Información del paciente (izquierda) ----------
        info_frame = ctk.CTkFrame(top_panel, corner_radius=15, border_width=1, border_color="#e5e7eb", fg_color="white")
        info_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        info_frame.grid_columnconfigure(0, weight=1)

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

        # ---------- Imagen (derecha) ----------
        right_img_frame = ctk.CTkFrame(top_panel, width=280, height=280, corner_radius=15, border_width=1, border_color="#e5e7eb", fg_color="white")
        right_img_frame.grid(row=0, column=1, sticky="nsew")
        right_img_frame.grid_propagate(False)

        ctk.CTkLabel(right_img_frame, text="Radiografía Procesada", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.imagen_label = ctk.CTkLabel(right_img_frame, text="")
        self.imagen_label.pack(expand=True, padx=10, pady=10)

        # ---------- Tabla (scrollable) ----------
        self.tabla_frame = ctk.CTkScrollableFrame(self.main_frame, height=350, fg_color="transparent")
        self.tabla_frame.grid(row=1, column=0, sticky="nsew", pady=(10, 0))

        # ---------- Sección de subcarpetas (horizontal) ----------
        sub_frame = ctk.CTkFrame(self, fg_color="transparent")
        sub_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))

        ctk.CTkLabel(sub_frame, text="Procesamiento Adicional", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w")
        self.sub_scroll = ctk.CTkScrollableFrame(sub_frame, height=120, orientation="horizontal", fg_color="transparent")
        self.sub_scroll.pack(fill="x", pady=5)
        self.subcarpetas_container = self.sub_scroll

    # ---------- Carga de datos ----------
    def _cargar_datos(self, carpeta: Path):
        self.carpeta_actual = carpeta
        self.nombre_label.configure(text=carpeta.name)
        self.fecha_label.configure(text=formatear_fecha(carpeta.stat().st_mtime))

        archivos = list(carpeta.glob("*"))
        num_piezas = len([f for f in archivos if "invertida" in f.name]) * 8
        self.piezas_label.configure(text=f"{num_piezas} piezas dentales segmentadas")

        # Cargar imagen
        invertida_path = next((f for f in archivos if "invertida" in f.name.lower()), None)
        if invertida_path and invertida_path.exists():
            img = Image.open(invertida_path)
            max_size = (250, 250)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
            self.imagen_label.configure(image=ctk_img, text="")
            self.imagen_label.image = ctk_img
        else:
            self.imagen_label.configure(text="Sin imagen procesada", text_color="gray")

        self._mostrar_tabla(carpeta)

    # ---------- Tabla desde CSV ----------
    def _mostrar_tabla(self, carpeta: Path):
        # Limpiar frame
        for widget in self.tabla_frame.winfo_children():
            widget.destroy()

        csv_path = carpeta / "metricas.csv"
        print(f"Buscando CSV en: {csv_path}")  # Debug
        if not csv_path.exists():
            ctk.CTkLabel(self.tabla_frame, text="No hay datos de métricas (CSV no encontrado)", text_color="gray").pack(pady=20)
            return

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            # Contenedor para la tabla (para que el scroll funcione)
            container = ctk.CTkFrame(self.tabla_frame, fg_color="transparent")
            container.pack(fill="both", expand=True)

            # Cabecera
            header_frame = ctk.CTkFrame(container, fg_color="#e2e8f0", corner_radius=5)
            header_frame.pack(fill="x", pady=(0, 2))
            for col, header in enumerate(headers):
                header_frame.grid_columnconfigure(col, weight=1, minsize=80)
                ctk.CTkLabel(header_frame, text=header, font=ctk.CTkFont(weight="bold", size=12),
                             anchor="w", padx=5).grid(row=0, column=col, sticky="ew", padx=1, pady=5)

            # Filas
            for row_data in reader:
                row_frame = ctk.CTkFrame(container, fg_color="transparent")
                row_frame.pack(fill="x", pady=1)
                for col, value in enumerate(row_data):
                    row_frame.grid_columnconfigure(col, weight=1, minsize=80)
                    ctk.CTkLabel(row_frame, text=value, anchor="w", padx=5).grid(row=0, column=col, sticky="ew", padx=1, pady=2)

    # ---------- Lista de subcarpetas ----------
    def _actualizar_lista_subcarpetas(self):
        for widget in self.subcarpetas_container.winfo_children():
            widget.destroy()

        subcarpetas = [sub for sub in self.carpeta_raiz.iterdir() if sub.is_dir() and sub != self.carpeta_raiz]
        self._agregar_tarjeta_carpeta(self.carpeta_raiz, es_raiz=True)
        for sub in subcarpetas:
            self._agregar_tarjeta_carpeta(sub, es_raiz=False)
        if not subcarpetas:
            ctk.CTkLabel(self.subcarpetas_container, text="No hay subcarpetas").pack(pady=10)

    def _agregar_tarjeta_carpeta(self, carpeta: Path, es_raiz: bool):
        card = ctk.CTkFrame(self.subcarpetas_container, corner_radius=10, border_width=1, border_color="#e5e7eb",
                            fg_color="#f9fafb" if carpeta != self.carpeta_actual else "#dbeafe")
        card.pack(side="left", padx=5, pady=5, fill="y")
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", padx=10, pady=8)
        nombre_text = "📁 Raíz" if es_raiz else carpeta.name
        ctk.CTkLabel(info, text=nombre_text, font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w")
        fecha = formatear_fecha(carpeta.stat().st_mtime)
        archivos = list(carpeta.glob("*"))
        piezas = len([f for f in archivos if "invertida" in f.name]) * 8
        ctk.CTkLabel(info, text=f"{fecha} | {piezas} piezas", font=ctk.CTkFont(size=10)).pack(anchor="w")
        btn = ctk.CTkButton(card, text="VER", width=50, height=28,
                            command=lambda c=carpeta: self._cambiar_carpeta_activa(c))
        btn.pack(side="right", padx=10)

    def _cambiar_carpeta_activa(self, nueva_carpeta: Path):
        if nueva_carpeta == self.carpeta_actual:
            return
        self._cargar_datos(nueva_carpeta)
        self._actualizar_lista_subcarpetas()

    # ---------- Exportar CSV ----------
    def _descargar_csv(self):
        import os
        csv_path = self.carpeta_actual / "metricas.csv"
        if not csv_path.exists():
            messagebox.showerror("Error", "CSV no encontrado en esta carpeta")
            return
        descargas = os.path.join(os.path.expanduser("~"), "Downloads")
        destino = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialdir=descargas,
            initialfile=f"{self.carpeta_actual.name}_metricas.csv"
        )
        if destino:
            import shutil
            shutil.copy2(csv_path, destino)
            messagebox.showinfo("Éxito", f"CSV exportado a {destino}")