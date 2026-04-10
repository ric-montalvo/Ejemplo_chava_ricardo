import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk


class Interfaz_basica:
    def __init__(self, root):
        self.root = root
        self.root.title("PDI - Visualizador Tamaño Real")

        self.image_stages = []
        self.stage_index = 0

        # Este callback será asignado por el Controlador
        self.on_open_image_callback = None

        # --- ZONA SUPERIOR: Botones ---
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self.btn_open = tk.Button(self.top_frame, text="📂 Abrir imagen", command=self.trigger_open_image)
        self.btn_open.pack(side=tk.LEFT)

        self.lbl_info = tk.Label(self.top_frame, text="Ninguna imagen cargada", font=("Arial", 10, "bold"))
        self.lbl_info.pack(side=tk.LEFT, padx=20)

        self.btn_next = tk.Button(self.top_frame, text="Siguiente >>", command=self.next_stage, state=tk.DISABLED)
        self.btn_next.pack(side=tk.RIGHT)

        self.btn_prev = tk.Button(self.top_frame, text="<< Anterior", command=self.prev_stage, state=tk.DISABLED)
        self.btn_prev.pack(side=tk.RIGHT, padx=5)

        # --- ZONA CENTRAL: Canvas con Scrollbars ---
        self.frame_canvas = tk.Frame(root)
        self.frame_canvas.pack(fill=tk.BOTH, expand=True)

        self.v_scroll = tk.Scrollbar(self.frame_canvas, orient=tk.VERTICAL)
        self.h_scroll = tk.Scrollbar(self.frame_canvas, orient=tk.HORIZONTAL)

        self.canvas = tk.Canvas(self.frame_canvas, bg="#333333",
                                yscrollcommand=self.v_scroll.set,
                                xscrollcommand=self.h_scroll.set)

        self.v_scroll.config(command=self.canvas.yview)
        self.h_scroll.config(command=self.canvas.xview)

        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.root.bind('<Left>', lambda e: self.prev_stage())
        self.root.bind('<Right>', lambda e: self.next_stage())

    def trigger_open_image(self):
        # La vista solo abre el explorador filtrando por JPG
        path = filedialog.askopenfilename(
            filetypes=[("Archivos imagen", "*.jpg *.jpeg *.bmp")]
        )
        if not path: return

        # Si hay un controlador escuchando, le manda la ruta
        if self.on_open_image_callback:
            self.on_open_image_callback(path)

    # --- Funciones que el Controlador usará para actualizar la Vista ---
    def update_images(self, images):
        """El controlador llama a esto cuando el modelo termina de procesar"""
        self.image_stages = images
        self.stage_index = 0
        self.display_image()
        self.btn_next.config(state=tk.NORMAL)
        self.btn_prev.config(state=tk.NORMAL)

    def show_error(self, message):
        """El controlador llama a esto si el modelo falla"""
        messagebox.showerror("Error", message)

    # --- Navegación y renderizado (Solo visual) ---
    def next_stage(self):
        if not self.image_stages: return
        self.stage_index = (self.stage_index + 1) % len(self.image_stages)
        self.display_image()

    def prev_stage(self):
        if not self.image_stages: return
        self.stage_index = (self.stage_index - 1) % len(self.image_stages)
        self.display_image()

    def display_image(self):
        image_obj = self.image_stages[self.stage_index]

        if isinstance(image_obj, tuple):
            image, text_info = image_obj[0], image_obj[1]
        else:
            image, text_info = image_obj, f"Etapa {self.stage_index}"

        self.tk_image = ImageTk.PhotoImage(image)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        self.canvas.config(scrollregion=(0, 0, image.width, image.height))
        self.lbl_info.config(text=f"{text_info} | Dimensiones: {image.width}x{image.height}")