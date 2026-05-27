import numpy as np
from Modelo.Metodos_numericos import Metodos_numericos
from Modelo.Utilidades_npListas import Utilidades_npListas


class Validador_puntos:
    metodos = Metodos_numericos()
    utl = Utilidades_npListas()

    def obtener_puntos_validos(self, lista_puntos, gradiente, radio=3):
        h, w = gradiente.shape
        puntos_corregidos = set()
        for punto in lista_puntos:
            y, x = punto
            if (x - radio < 0 or x + radio >= w):
                continue
            else:
                x1, x2 = x - radio, x + radio + 1
                ventana = gradiente[y, x1:x2]
                x_max = np.argmax(ventana)
                x_normalizado = x + x_max
                punto_maximo = (y, x_normalizado)
                if punto_maximo not in puntos_corregidos:
                    puntos_corregidos.add(punto_maximo)
                else:
                    puntos_corregidos.add(punto)
        return list(puntos_corregidos)

    #---------------------------------------------