import numpy as np
from Modelo.Visualizador_operaciones import Visualizador_operaciones
class Convolucionador:
    visualizador = Visualizador_operaciones()

    def aplicar_convolucion_separable(self, imagen, kernel_fila, kernel_columna):
        h, w = imagen.shape
        img_final = np.zeros((h , w))
        conv_inicial = self.convolucion_kernel1d(imagen, kernel_fila, "fila")
        img_sobrepuesta = self.visualizador.sobreponer_imagen_reducida(img_final, conv_inicial)
        img_final_reducida = self.convolucion_kernel1d(img_sobrepuesta, kernel_columna, "columna")
        img_final = self.visualizador.sobreponer_imagen_reducida(img_final, img_final_reducida)
        return img_final

    def convolucion_kernel1d(self, imagen, kernel, tipo_kernel = "fila"):
        ran = len(kernel)
        radio = ran // 2
        h, w = imagen.shape
        if tipo_kernel == "fila":
            w = w - (2 *radio)
            img_convolucion = np.zeros((h, w))
            for i in range (0, ran):
                ventana = imagen[0:h, i:i+w]
                img_convolucion += ventana * kernel[i]
        else:
            h = h - (2 *radio)
            img_convolucion = np.zeros((h, w))
            for i in range (0, ran):
                ventana = imagen[i:i+h, 0:w]
                img_convolucion += ventana * kernel[i]
        return img_convolucion

    def aplicar_convolucion_kernel2d(self, imagen, kernel): #devuelve en tamaño -2radio
        kernel = np.flip(kernel)
        ran_h, ran_w = kernel.shape
        rad_h = ran_h // 2
        rad_w = ran_w // 2
        h, w = imagen.shape
        h = h - (2 * rad_h)
        w = w - (2 * rad_w)
        img_convolucion = np.zeros((h, w))
        for i in range (0, ran_h):
            for j in range (0, ran_w):
                ventana = imagen[i:i+h, j:j+w]
                img_convolucion += ventana * kernel[i, j]
        return img_convolucion



