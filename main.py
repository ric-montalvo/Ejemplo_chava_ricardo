import tkinter as tk
from View.Interfaz_basica import Interfaz_basica
from Model.Procesador_imagen import Procesador_imagen
from Controller.Pipeline import Pipeline

if __name__ == "__main__":
    # crear ventana con tkinter
    root = tk.Tk()

    # crear el modelo ,el motor de procesamiento de imagenes
    modelo = Procesador_imagen()

    #La interfaz grafica que modificaremos sin cambiar los callbacks
    vista = Interfaz_basica(root)

    #se encarga de enlazar la vista y el modelo
    controlador = Pipeline(vista, modelo)

    #iniciar bucle de ventaja con tkinter y que se quede abierta
    root.mainloop()