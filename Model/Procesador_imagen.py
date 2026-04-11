import os
import cv2
import numpy as np
from PIL import Image, ImageOps
# Model/Procesador_imagen.py
# Descripción: Modelo que contiene la lógica de negocio (procesamiento de imágenes).
#              Actualmente solo hace: validar extensión, convertir a grises, invertir grises,
#              guardar resultado y devolver lista de imágenes para la vista.
#
# IMPORTANTE: Este archivo es un placeholder. El pipeline real de segmentación dental
#             (con detección de bordes, métricas, etc.) se implementará AQUÍ más adelante.
#             Por ahora, es solo un ejemplo funcional para probar la comunicación MVC.
#
# NOTA PARA MODIFICAR LA VISTA: El modelo NO debe cambiar por ahora. La función
# 'procesar_pipeline' debe seguir devolviendo una lista de tuplas (imagen_PIL, texto).
# La vista espera ese formato. Si se cambia el modelo, hay que actualizar la vista.

class Procesador_imagen:
    def procesar_pipeline(self, path):
        _, ext = os.path.splitext(path)
        if ext.lower() not in ['.jpg', '.jpeg', '.bmp']:
            raise ValueError("Restricción de entrada: El archivo debe ser un JPG o BMP.")

        try:
            #Lectura
            img_original = Image.open(path)

            #Preparacion para convertir en escala de grises
            img_gris = ImageOps.grayscale(img_original)
            np_grises = np.array(img_gris)

            #Procesado a inversion de grises
            np_invertida = self.grises_invertidos(np_grises)

            #Conversion a imagen nuevamente
            img_invertida = Image.fromarray(np_invertida)

            #Guaradado en misma carpeta que original
            self.guardar_resultado(path, np_invertida, "_invertida")

            #Retorno a la vista
            return [
                (img_original, "1. Imagen Original"),
                (img_gris, "2. Escala de Grises"),
                (img_invertida, "3. Inversión de grises")
            ]
        except Exception as e:
            raise RuntimeError(f"No se pudo procesar la imagen: {e}")


    #funcion de ejemplo, el procesamiento no estara en esta clase
    #si no en otras para mejorar legibilidad
    def grises_invertidos(self, gris):
        invertida = 255 - gris
        return np.clip(invertida, 0, 255).astype(np.uint8)


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