import numpy as np
from Modelo.Convolucionador import Convolucionador

class Operador_Sobel:

    conv = Convolucionador()

    def __init__(self):
        self.kernel1 = np.array([-1, 0, 1])
        self.kernel2 = np.array([1, 2, 1])

    def gx_sobel(self, imagen):
        gx = self.conv.aplicar_convolucion_separable(imagen, self.kernel1, self.kernel2)
        return gx

    def gy_sobel(self, imagen):
        gy = self.conv.aplicar_convolucion_separable(imagen, self.kernel2, self.kernel1)
        return gy

    def magnitud_sobel(self, imagen):
        gx = self.gx_sobel(imagen)
        gy = self.gy_sobel(imagen)
        magnitud = np.sqrt(np.square(gx) + np.square(gy))
        return magnitud

    def orientacion_sobel(self, imagen):
        gx = self.gx_sobel(imagen)
        gy = self.gy_sobel(imagen)
        angulo_radianes = np.arctan2(gy, gx)
        angulo_grados = np.rad2deg(angulo_radianes)
        angulo_grados = (angulo_grados + 360) % 360

        return angulo_grados
