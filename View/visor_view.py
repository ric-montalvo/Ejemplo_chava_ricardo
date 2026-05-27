# view/visor_view.py
import customtkinter as ctk
from PIL import Image, ImageTk

class VisorView(ctk.CTkToplevel):
    def __init__(self, parent, imagenes_procesadas, nombre_paciente, on_volver=None):
        super().__init__(parent)
        self.title("Resultados del Procesamiento")
        self.geometry("1000x700")
        self.transient(parent)

        self.imagenes = imagenes_procesadas
        self.indice = 0
        self.on_volver = on_volver

        # Variables para zoom y pan
        self.zoom_factor = 1.0
        self.zoom_min = 0.5
        self.zoom_max = 5.0
        self.pan_x = 0
        self.pan_y = 0
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.is_dragging = False
        self.image_pil = None
        self.tk_image = None

        # Debounce para el zoom (evita redibujar demasiado rápido)
        self.zoom_pending = False
        self.zoom_target_factor = 1.0
        self.zoom_target_pan_x = 0
        self.zoom_target_pan_y = 0

        # Título
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(15, 5))
        ctk.CTkLabel(top_frame, text=f"Resultados - {nombre_paciente}",
                     font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")

        # Canvas para la imagen
        self.canvas_frame = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=10)
        self.canvas_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.canvas = ctk.CTkCanvas(self.canvas_frame, bg="#2b2b2b", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Barra de navegación
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(pady=10)
        ctk.CTkButton(nav_frame, text="◀ Anterior (←)", command=self.anterior, width=140).pack(side="left", padx=10)
        ctk.CTkButton(nav_frame, text="Siguiente (→)", command=self.siguiente, width=140).pack(side="left", padx=10)
        self.lbl_info = ctk.CTkLabel(nav_frame, text="", font=ctk.CTkFont(size=14))
        self.lbl_info.pack(side="left", padx=20)
        ctk.CTkButton(nav_frame, text="Zoom reset", command=self.reset_zoom, width=100).pack(side="left", padx=10)

        # Eventos
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel)
        self.canvas.bind("<Button-5>", self.on_mousewheel)
        self.canvas.bind("<ButtonPress-1>", self.on_drag_start)
        self.canvas.bind("<B1-Motion>", self.on_drag_move)
        self.bind('<Left>', lambda e: self.anterior())
        self.bind('<Right>', lambda e: self.siguiente())
        self.bind('<Escape>', lambda e: self.cerrar_y_volver())
        self.protocol("WM_DELETE_WINDOW", self.cerrar_y_volver)

        self.actualizar()

    def actualizar(self):
        img_pil, texto = self.imagenes[self.indice]
        self.image_pil = img_pil.copy()
        self.zoom_factor = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self._redibujar()
        total = len(self.imagenes)
        self.lbl_info.configure(text=f"{texto} | Imagen {self.indice+1} de {total}")

    def _redibujar(self):
        if self.image_pil is None:
            return
        w, h = self.image_pil.size
        new_w = int(w * self.zoom_factor)
        new_h = int(h * self.zoom_factor)
        # Usar NEAREST para mayor velocidad (zoom fluido)
        img_resized = self.image_pil.resize((new_w, new_h), Image.Resampling.NEAREST)
        self.tk_image = ImageTk.PhotoImage(img_resized)

        self.canvas.delete("all")
        self.canvas.config(scrollregion=(0, 0, new_w, new_h))
        self.canvas.create_image(self.pan_x, self.pan_y, anchor="nw", image=self.tk_image)

    def on_mousewheel(self, event):
        # Calcular nuevo zoom y pan
        if event.num == 5 or event.delta < 0:
            delta = -1
        else:
            delta = 1
        factor = 1.1 if delta > 0 else 0.9
        nuevo_zoom = self.zoom_factor * factor
        if nuevo_zoom < self.zoom_min or nuevo_zoom > self.zoom_max:
            return
        mouse_x = self.canvas.canvasx(event.x)
        mouse_y = self.canvas.canvasy(event.y)
        nuevo_pan_x = mouse_x - (mouse_x - self.pan_x) * factor
        nuevo_pan_y = mouse_y - (mouse_y - self.pan_y) * factor

        # Aplazar el redibujado para no saturar eventos
        self.zoom_target_factor = nuevo_zoom
        self.zoom_target_pan_x = nuevo_pan_x
        self.zoom_target_pan_y = nuevo_pan_y
        if not self.zoom_pending:
            self.zoom_pending = True
            self.after(20, self._aplicar_zoom)

    def _aplicar_zoom(self):
        self.zoom_factor = self.zoom_target_factor
        self.pan_x = self.zoom_target_pan_x
        self.pan_y = self.zoom_target_pan_y
        self._redibujar()
        self.zoom_pending = False

    def on_drag_start(self, event):
        self.is_dragging = True
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_drag_move(self, event):
        if self.is_dragging:
            dx = event.x - self.drag_start_x
            dy = event.y - self.drag_start_y
            self.pan_x += dx
            self.pan_y += dy
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self._redibujar()

    def reset_zoom(self):
        self.zoom_factor = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self._redibujar()

    def anterior(self):
        self.indice = (self.indice - 1) % len(self.imagenes)
        self.actualizar()

    def siguiente(self):
        self.indice = (self.indice + 1) % len(self.imagenes)
        self.actualizar()

    def cerrar_y_volver(self):
        self.destroy()
        if self.on_volver:
            self.on_volver("menu")