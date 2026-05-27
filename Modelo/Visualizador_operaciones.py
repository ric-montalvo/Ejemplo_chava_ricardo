import numpy as np
from Modelo.Utilidades_npListas import Utilidades_npListas

class Visualizador_operaciones:

    utl_npListas = Utilidades_npListas()

    def sobreponer_imagen_reducida(self, img, img_reducida):
        h, w = img.shape
        h_r, w_r = img_reducida.shape
        dif_h = (h - h_r) // 2
        dif_w = (w - w_r) // 2
        img_final = img.copy()
        img_final[dif_h:h - dif_h, dif_w:w - dif_w] = img_reducida[:h_r, :w_r]
        return img_final

    def lista_sobre_imagen(self, img, lista):
        img_final = img.copy()
        h, w = img.shape
        if len(lista) == 0:
            return img_final
        for punto in lista:
            if(0 <= punto[0] < h and 0 <= punto[1] < w):
                img_final[punto] = 255
        return img_final

    def listas_sobre_imagen(self, img, lista_listas):
        lista = self.utl_npListas.aplanar_lista_de_tuplas(lista_listas)
        img_final = self.lista_sobre_imagen(img, lista)
        return img_final

    def mapear_a_visualizable(self, imagen):
        img_abs = np.abs(imagen)
        max_val = np.max(img_abs)
        if max_val < 1e-5:
            return np.zeros(imagen.shape, dtype=np.uint8)
        img_normalizada = (img_abs / max_val) * 255

        return img_normalizada.astype(np.uint8)

    def set_sobre_imagen(self, imagen, set_puntos):
        return self.lista_sobre_imagen(imagen, list(set_puntos))

    def lista_sobre_imagen_color(self, img, lista, color='rojo'):

        if len(img.shape) < 3:
            img_color = np.stack((img, img, img), axis=-1)
        else:
            img_color = img.copy()
            if len(lista) == 0:
                return img_color
        colores_rgb = {
            'rojo': [255, 0, 0],
            'verde': [0, 255, 0],
            'azul': [0, 0, 255]
        }
        valor_rgb = colores_rgb.get(color.lower(), [255, 255, 255])
        h, w = img_color.shape[:2]
        for y, x in lista:
            if 0 <= y < h and 0 <= x < w:
                img_color[y, x] = valor_rgb
        return img_color

    def listas_sobre_imagen_color(self, img, lista_listas, color='rojo'):
        lista = self.utl_npListas.aplanar_lista_de_tuplas(lista_listas)
        img_final = self.lista_sobre_imagen_color(img, lista, color)
        return img_final

    def sobreponer_ventana(self, imagen_original, sub_imagen, rango_y, rango_x):
        imagen_resultado = imagen_original.copy()
        imagen_resultado[rango_y[0]:rango_y[1], rango_x[0]:rango_x[1]] = sub_imagen
        return imagen_resultado
