import tkinter as tk
from View.Interfaz_basica import Interfaz_basica
from Model.Procesador_imagen import Procesador_imagen
from Controller.Pipeline import Pipeline

if __name__ == "__main__":
    root = tk.Tk()
    modelo = Procesador_imagen()
    vista = Interfaz_basica(root)
    controlador = Pipeline(vista, modelo)
    root.mainloop()