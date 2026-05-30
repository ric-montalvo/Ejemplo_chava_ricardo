import numpy as np
from Modelo.Bordes_coronarios import Bordes_coronarios
from Modelo.Bordes_ventana import bordes_ventana
from Modelo.Operador_Sobel import Operador_Sobel
from Modelo.Utilidades_npListas import Utilidades_npListas
import math
from Modelo.Seguidor_basado_vertices import Seguidor_basado_vertices


class Seguimiento:
    estadisticos = bordes_ventana()
    coronarios = Bordes_coronarios()
    sobel = Operador_Sobel()
    utilidades = Utilidades_npListas()
    vertices = Seguidor_basado_vertices()


    def aplicar_seguimiento(self, imagen, pts_maxilares, pts_mandibulares):
        maxilares, mandibulares = self.seguimiento_hacia_oclusion(imagen, pts_maxilares, pts_mandibulares)

        return 0


    def seguimiento_hacia_oclusion(self, imagen, pts_maxilares, pts_mandibulares, bordes_cuello, bordes_corona):
        """Retorna Lista de listas"""
        sobel_gamma = self.coronarios.atenuar_ruido_gradiente(self.sobel.magnitud_sobel(imagen))
        direccion = self.sobel.orientacion_sobel(imagen)
        pts_unidos = pts_maxilares + pts_mandibulares
        #brds_estadisticos, puntos_ajustados = self.estadisticos.obtener_bordes(sobel_gamma, direccion, pts_unidos, (60, 30))
        #bordes_cuello, bordes_corona = self.coronarios.extraer_contornos_dentales(self.sobel.magnitud_sobel(imagen), pts_maxilares, pts_mandibulares)

        maxilares = []
        mandibulares = []

        for punto in pts_maxilares:
            borde = self.union_corona_punto_inicial(punto, bordes_cuello, bordes_corona, sobel_gamma, True, 1)
            maxilares.append(borde)

        for punto in pts_mandibulares:
            borde = self.union_corona_punto_inicial(punto, bordes_cuello, bordes_corona, sobel_gamma, False, 1)
            mandibulares.append(borde)
        return maxilares, mandibulares

    def union_corona_punto_inicial(self, punto, bordes_cuello, bordes_corona, magnitud, es_maxilar,
                                   radio):
        """Retorna Lista"""
        h, w = magnitud.shape
        camino = []
        bandera = True
        punto_actual = punto
        while bandera:
            camino.append(punto_actual)

            if punto_actual in bordes_corona:
                bandera = False
                continue

            y, x = punto_actual
            if es_maxilar:
                y = y + 1
            else:
                y = y - 1

            if y < 0 or y >= h:
                break

            vecinos = [(y, nx) for nx in range(x - radio, x + radio + 1)]
            vecinos = [p for p in vecinos if 0 <= p[1] < w]

            if not vecinos:
                break

            vecino_corona = next((v for v in vecinos if v in bordes_corona), False)
            if vecino_corona:
                camino.append(vecino_corona)
                break

            vecino_cuello = next((v for v in vecinos if v in bordes_cuello), False)
            if vecino_cuello:
                punto_actual = vecino_cuello
                continue

            magnitud_actual = magnitud[punto_actual]
            valores_y_coords = [(magnitud[vy, vx], (vy, vx)) for vy, vx in vecinos]
            valor_maximo, coordenada_maxima = max(valores_y_coords)


            punto_actual = coordenada_maxima


        return camino

    def proyectar_inercia(self, puntos_visitados, set_colision, magnitud, umbral_gradiente):
        if len(puntos_visitados) < 2:
            return [], None

        # 1. Dirección basada en los últimos 5 puntos (o los que haya)
        n_puntos = min(len(puntos_visitados), 5)
        y_ini, x_ini = puntos_visitados[-n_puntos]
        y_fin, x_fin = puntos_visitados[-1]

        dy = y_fin - y_ini
        dx = x_fin - x_ini
        distancia = math.hypot(dy, dx)

        if distancia == 0:
            return [], None

        vy = dy / distancia
        vx = dx / distancia

        puntos_generados = []
        punto_parada = None
        h, w = magnitud.shape

        y_actual = float(y_fin)
        x_actual = float(x_fin)
        paso = 0.5
        limite_espacial = 30  # Seguro anti-bucles
        distancia_recorrida = 0.0

        # 2. Avance limitado por el dominio del gradiente
        while distancia_recorrida < limite_espacial:
            y_actual += vy * paso
            x_actual += vx * paso
            distancia_recorrida += paso

            punto_grid = (round(y_actual), round(x_actual))

            if not (0 <= punto_grid[0] < h and 0 <= punto_grid[1] < w):
                break

            if punto_grid == (y_fin, x_fin) or (puntos_generados and puntos_generados[-1] == punto_grid):
                continue

            puntos_generados.append(punto_grid)

            ### NUEVO: Red de captura para la inercia (evita el efecto túnel diagonal)
            y_g, x_g = punto_grid
            vecindad_inercia = [(y_g, x_g - 1), (y_g, x_g), (y_g, x_g + 1)]

            choque = next((v for v in vecindad_inercia if v in set_colision), None)
            if choque:
                punto_parada = choque
                break
            ### ----------------------------------------------------

            # Frenar si el gradiente vuelve a ser aceptable
            if magnitud[punto_grid] >= umbral_gradiente:
                punto_parada = punto_grid
                break

        if punto_parada is None and puntos_generados:
            punto_parada = puntos_generados[-1]

        return puntos_generados, punto_parada