class Pipeline:
    def __init__(self, vista, modelo):
        self.vista = vista
        self.modelo = modelo
        self.vista.on_open_image_callback = self.manejar_nueva_imagen

    def manejar_nueva_imagen(self, path):
        try:
            resultados = self.modelo.procesar_pipeline(path)
            self.vista.update_images(resultados)

        except ValueError as e:
            self.vista.show_error(str(e))
        except RuntimeError as e:
            self.vista.show_error(str(e))