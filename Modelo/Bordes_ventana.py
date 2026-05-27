import numpy as np
from Modelo.Morfologia import Morfologia
from collections import deque


class bordes_ventana():
    morf = Morfologia()

    def obtener_bordes(self, magnitud, orientacion, lista_puntos, radios):
        # Logica de implementacion
        lista_bordes = []
        puntos = self.ajustar_iniciales(magnitud, orientacion, lista_puntos, radios)
        puntos = self.ajustar_iniciales(magnitud, orientacion, puntos, radios)
        for punto in puntos:
            ventana, punto_referencia = self.obtener_ventana(magnitud, punto, radios)
            borde = self.obtener_bordes_ventana(ventana, punto_referencia, 90)
            lista_bordes.append(borde)
            # self.imprimir_histograma(ventana)
        bordes_adelgazados = self.suprimir_no_maximos(lista_bordes, magnitud, orientacion)
        bordes_verticales = self.union_bordes(bordes_adelgazados, orientacion)
        puntos = self.ajustar_puntos_a_bordes(bordes_verticales, puntos)
        return bordes_verticales, puntos

    def ajustar_iniciales(self, magnitud, orientacion, puntos, radios):
        #Logica de implementacion
        lista_bordes = []

        for punto in puntos:
            ventana, punto_referencia = self.obtener_ventana(magnitud, punto, radios)
            borde = self.obtener_bordes_ventana(ventana, punto_referencia, 90)
            lista_bordes.append(borde)
            #self.imprimir_histograma(ventana)
        bordes_adelgazados = self.suprimir_no_maximos(lista_bordes, magnitud, orientacion)
        bordes_verticales = self.union_bordes(bordes_adelgazados, orientacion)
        puntos_iniciales_ajustados = self.ajustar_puntos_a_bordes(bordes_verticales, puntos)
        return puntos_iniciales_ajustados


#=======================UTILIDADES=================================
    def obtener_ventana(self, img, punto, radios):
        h_img, w_img = img.shape
        y, x = punto
        h_ventana, w_ventana = radios
        y_min = max(0, y - h_ventana)
        y_max = min(h_img, y + h_ventana)
        x_min = max(0, x - w_ventana)
        x_max = min(w_img, x + w_ventana)
        return img[y_min:y_max, x_min:x_max], (y_min, x_min)


#=======================BORDE ESTADISTICO GRUESO=====================
    def obtener_bordes_ventana(self, ventana, punto_referencia, percentil_top=90):
        y0, x0 = punto_referencia
        umbral_claros = np.percentile(ventana, percentil_top)
        idx_y, idx_x = np.where(ventana > umbral_claros)
        bordes = [(y + y0, x + x0) for y, x in zip(idx_y, idx_x)]
        return bordes

#======================BORDE ADELGAZADO=========================================

    def suprimir_no_maximos(self, bordes_gruesos, magnitud, direccion):
        angulo = direccion % 180
        bordes_finos = []
        max_y, max_x = magnitud.shape

        for grupo in bordes_gruesos:
            grupo_fino = []
            for y, x in grupo:
                if y == 0 or y == max_y - 1 or x == 0 or x == max_x - 1:
                    continue
                ang = angulo[y, x]
                mag = magnitud[y, x]
                vecino_1, vecino_2 = self.obtener_vecinos_nms(ang, y, x, magnitud)
                if (mag >= vecino_1) and (mag >= vecino_2):
                    grupo_fino.append((y, x))
            if len(grupo_fino) > 0:
                bordes_finos.append(grupo_fino)
        return bordes_finos

    #.....................SUBMODULO 1..................
    def obtener_vecinos_nms(self, ang, y, x, magnitud):
        vecino_1 = float('inf')
        vecino_2 = float('inf')
        if (0 <= ang < 22.5) or (157.5 <= ang <= 180):
            vecino_1 = magnitud[y, x + 1]
            vecino_2 = magnitud[y, x - 1]
        elif (22.5 <= ang < 67.5):
            vecino_1 = magnitud[y - 1, x + 1]
            vecino_2 = magnitud[y + 1, x - 1]
        elif (67.5 <= ang < 112.5):
            vecino_1 = magnitud[y - 1, x]
            vecino_2 = magnitud[y + 1, x]
        elif (112.5 <= ang < 157.5):
            vecino_1 = magnitud[y - 1, x - 1]
            vecino_2 = magnitud[y + 1, x + 1]

        return vecino_1, vecino_2



#========================UNION DE PUNTOS===============================

    #.......IMPLEMENTACION................
    def union_bordes(self, bordes_finos, orientacion):
        puntos_borde_vertical = self.filtrar_bordes_verticales(bordes_finos, orientacion)
        puntos_validos = self.filtrar_lineas_por_longitud(puntos_borde_vertical, 6)
        return puntos_validos


    #......LIMPIEZA EN BASE A LA DIRECCION.......
    def filtrar_bordes_verticales(self, bordes_finos, orientacion):
        bordes_purga_1 = []
        for grupo in bordes_finos:
            grupo_vertical = []
            for y, x in grupo:
                angulo_gradiente = orientacion[y, x]
                angulo_real_borde = (angulo_gradiente + 90) % 180
                if 40 <= angulo_real_borde <= 140:
                    grupo_vertical.append((y, x))
            if len(grupo_vertical) > 0:
                bordes_purga_1.append(grupo_vertical)
        return bordes_purga_1


    #.......MOVIMIENTO DE PUNTOS INICIALES......
    def ajustar_puntos_a_bordes(self, bordes, puntos_iniciales):
        puntos_borde = np.array([p for sublista in bordes for p in sublista])
        if puntos_borde.size == 0:
            return puntos_iniciales
        puntos_ajustados = []

        for p_ini in puntos_iniciales:
            punto_actual = np.array(p_ini)
            distancias = np.linalg.norm(puntos_borde - punto_actual, axis=1)
            indice_minimo = np.argmin(distancias)
            punto_cercano = tuple(puntos_borde[indice_minimo])
            puntos_ajustados.append(punto_cercano)
        return puntos_ajustados



    def filtrar_lineas_por_longitud(self, lista_de_listas, N, conectividad=8):
        puntos_set = set()
        for sublista in lista_de_listas:
            for y, x in sublista:
                puntos_set.add((y, x))

        if conectividad == 8:
            direcciones = [(-1, -1), (-1, 0), (-1, 1),
                           (0, -1), (0, 1),
                           (1, -1), (1, 0), (1, 1)]
        else:
            direcciones = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        visitados = set()
        puntos_filtrados = []
        for punto in puntos_set:
            if punto not in visitados:
                cola = deque([punto])
                visitados.add(punto)
                linea_actual = [punto]

                while cola:
                    py, px = cola.popleft()
                    for dy, dx in direcciones:
                        vecino = (py + dy, px + dx)
                        if vecino in puntos_set and vecino not in visitados:
                            visitados.add(vecino)
                            cola.append(vecino)
                            linea_actual.append(vecino)
                if len(linea_actual) >= N:
                    puntos_filtrados.append(linea_actual)

        return puntos_filtrados