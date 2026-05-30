import numpy as np
from Modelo.Operador_Sobel import Operador_Sobel

class seguidor_proyeccion:
    sobel = Operador_Sobel()

    def orquestador(self, imagen, maxilares, mandibulares):
        sobel = np.abs(self.sobel.gx_sobel(imagen))

        longitud = 20
        radio = 1
        maxilares = self.obtener_rectas_iniciales(sobel, maxilares, longitud, radio)
        mandibulares = self.obtener_rectas_iniciales(sobel, mandibulares, longitud, radio)

        return maxilares, mandibulares




    def obtener_rectas_iniciales(self, sobel, puntos, longitud, radio):
        rectas = []
        for punto in puntos:
            recta_1 = self.seguimiento_simple(sobel, punto, 1, longitud, radio)
            recta_2 = self.seguimiento_simple(sobel, punto, -1, longitud, radio)
            recta = list(set(recta_1 + recta_2))
            rectas.append(recta)
        return rectas


    def seguimiento_simple(self, sobel, punto_inicial, dy, longitud = 10, radio = 1):

        h, w = sobel.shape
        puntos_visitados = set()
        punto = punto_inicial
        for i in range(0, longitud):
            puntos_visitados.add(punto)
            y, x = punto
            y_siguiente = y + dy
            if y_siguiente < 0 or y_siguiente >= h: break
            x_ini = max(0, x - radio)
            x_fin = min(w, x + radio + 1)
            vecinos = [(y_siguiente, nx) for nx in range(x_ini, x_fin)]
            if not vecinos: break
            valores_y_coords = [(sobel[vy, vx], (vy, vx)) for vy, vx in vecinos]
            valor_maximo, coordenada_maxima = max(valores_y_coords)
            punto = coordenada_maxima


        return list(puntos_visitados)