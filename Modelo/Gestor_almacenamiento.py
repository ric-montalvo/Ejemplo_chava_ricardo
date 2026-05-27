import os
import cv2

class Gestor_almacenamiento:

    def obtener_ruta_guardar(self, path, sufijo):
        directorio, archivo = os.path.split(path)
        nombre_base, ext = os.path.splitext(archivo)
        nuevo_nombre = f"{nombre_base}{sufijo}{ext}"
        return os.path.join(directorio, nuevo_nombre)

    def guardar_resultado(self, path_original, matriz_cv2, sufijo):
        nueva_ruta = self.obtener_ruta_guardar(path_original, sufijo)
        exito = cv2.imwrite(nueva_ruta, matriz_cv2)
        if not exito:
            raise RuntimeError(f"No se pudo guardar la imagen en disco: {nueva_ruta}")
        return nueva_ruta