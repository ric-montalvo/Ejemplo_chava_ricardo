# Controller/Pipeline.py
# NOTA IMPORTANTE: El enlace se hace mediante 'on_open_image_callback'. La vista
#                  tiene un atributo que es una función; el controlador asigna su propio
#                  método a ese atributo. Así la vista no necesita conocer al controlador.
#                  Esto es un callback (patrón Observer/Delegación).
#
# Para mantener la comunicación: NO cambiar el nombre de 'on_open_image_callback'
# ni la firma de 'manejar_nueva_imagen'. Si se modifica la vista, asegurarse de que
# siga existiendo 'on_open_image_callback' y que se llame con un solo argumento (path).
class Pipeline:
    def __init__(self, vista, modelo):
        #guardando referencias de vista y modelo
        self.vista = vista
        self.modelo = modelo
        #asigna el callback de la vista, cuando el usuario abre una imagen la vista llamara a self.manejar_nueva_imagen
        self.vista.on_open_image_callback = self.manejar_nueva_imagen

    def manejar_nueva_imagen(self, path):
        """
        Esta función se ejecuta automáticamente cuando el usuario selecciona una imagen.
        path: ruta del archivo seleccionado.
        """
        try:
            #pide al modelo que procese la imagen
            resultados = self.modelo.procesar_pipeline(path)

            #actualiza la vista con los resultados de las imagenes
            self.vista.update_images(resultados)

        except ValueError as e:
            #error de formato o restriccion
            self.vista.show_error(str(e))
        except RuntimeError as e:
            #error durante el procesamiento de no poder guardarse
            self.vista.show_error(str(e))