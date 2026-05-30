import numpy as np
import math
from Modelo.Metodos_numericos import Metodos_numericos

class Operaciones_anchura:
    metodos = Metodos_numericos()


    def orquestador(self, maxilares_pts, mandibulares_pts, maxilares_vert, mandibulares_vert, cuellos_max, cuellos_man, coronas_max, coronas_man):
        anchuras_maxilares = self.obtener_anchuras(maxilares_pts)
        anchuras_mandibulares = self.obtener_anchuras(mandibulares_pts)

        conexiones_maxilar = self.aplicar_conexion(maxilares_vert, anchuras_maxilares, cuellos_max, coronas_max, True)
        conexiones_mandibulares = self.aplicar_conexion(mandibulares_vert, anchuras_mandibulares, cuellos_man, coronas_man, False)
        return conexiones_maxilar, conexiones_mandibulares
        #return conexiones_maxilar[2], conexiones_mandibulares[-1]



    def obtener_anchuras(self, puntos):
        puntos_unidos = []
        if len(puntos) < 2:
            return
        puntos_ordenados = sorted(puntos, key=lambda p: p[1])
        distancias = []
        for i in range(len(puntos_ordenados) - 1):
            p1 = puntos_ordenados[i]
            p2 = puntos_ordenados[i + 1]
            distancia = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            distancias.append(distancia)

        media_distancia = sum(distancias) / len(distancias)
        for i in range(len(puntos_ordenados) - 1):
            if distancias[i] > media_distancia:
                p1 = puntos_ordenados[i]
                p2 = puntos_ordenados[i + 1]
                pts_unidos = self.metodos.algoritmo_Bresenham(p1, p2)
                puntos_unidos.append(pts_unidos)

        return puntos_unidos

    def obtener_diastemas(self, puntos):
        puntos_unidos = []
        if len(puntos) < 2:
            return puntos_unidos
        puntos_ordenados = sorted(puntos, key=lambda p: p[1])
        distancias = []
        for i in range(len(puntos_ordenados) - 1):
            p1 = puntos_ordenados[i]
            p2 = puntos_ordenados[i + 1]
            distancia = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
            distancias.append(distancia)
        media_distancia = sum(distancias) / len(distancias)


        for i in range(len(puntos_ordenados) - 1):
            if distancias[i] < media_distancia:
                p1 = puntos_ordenados[i]
                p2 = puntos_ordenados[i + 1]
                pts_unidos = self.metodos.algoritmo_Bresenham(p1, p2)
                puntos_unidos.append(pts_unidos)

        return puntos_unidos

    def centros_anchuras(self, anchuras):
        centros = []

        for anchura in anchuras:
            anchura_sorted = sorted(anchura, key=lambda anchura: anchura[1])
            centro = anchura_sorted[len(anchura_sorted)//2]
            centros.append(centro)

        return centros


    def bordes_conectados(self, anchura, bordes_verticales):
        set_horizontal = set(anchura)
        listas_conectadas = []

        for lista_vertical in bordes_verticales:
            if set_horizontal.intersection(lista_vertical):
                listas_conectadas.append(lista_vertical)
                if len(listas_conectadas) == 2:
                    return listas_conectadas[0], listas_conectadas[1]
        return listas_conectadas, listas_conectadas

    def corona_conectada(self, cuello1, cuello2, corona, es_Maxilar):
        brd1 = sorted(cuello1, key=lambda p: p[0])
        brd2 = sorted(cuello2, key=lambda p: p[0])
        if es_Maxilar:
            p1 = brd1[-1]
            p2 = brd2[-1]
        else:
            p1 = brd1[0]
            p2 = brd2[0]

        x_min = min(p1[1], p2[1])
        x_max = max(p1[1], p2[1])

        puntos_corona = [punto for punto in corona if x_min <= punto[1] <= x_max]
        return puntos_corona


    def conectar_puntos_finales(self, borde_vertical_1, borde_vertical_2, es_Maxilar = True):
        brd1 = sorted(borde_vertical_1, key=lambda p: p[0])
        brd2 = sorted(borde_vertical_2, key=lambda p: p[0])
        if es_Maxilar:
            pt1 = brd1[0]
            pt2 = brd2[0]
        else:
            pt1 = brd1[-1]
            pt2 = brd2[-1]
        if pt1 == pt2: return []

        borde_conectado = self.metodos.algoritmo_Bresenham(pt1, pt2)
        return borde_conectado


    def aplicar_conexion(self, bordes, anchuras, cuellos, coronas, es_Maxilar = True):
        brds_conectados = []
        for anchura in anchuras:
            brd1, brd2 = self.bordes_conectados(anchura, bordes)
            cuello1, cuello2 = self.bordes_conectados(anchura, cuellos)
            brd_conectado = self.conectar_puntos_finales(brd1, brd2, es_Maxilar)
            corona = self.corona_conectada(cuello1, cuello2, coronas, es_Maxilar)

            borde_conectado = brd1 + brd2 + brd_conectado + cuello1 + cuello2 + corona
            brds_conectados.append(borde_conectado)
        return brds_conectados


    def obtener_bordes_verticales_conectados(self, anchura, bordes, cuellos):
        brd1, brd2 = self.bordes_conectados(anchura, bordes)
        cuello1, cuello2 = self.bordes_conectados(anchura, cuellos)
        brd1_prom = np.mean(np.array(brd1)[:, 1])
        brd2_prom = np.mean(np.array(brd2)[:, 1])
        cuello1_prom = np.mean(np.array(cuello1)[:, 1])
        cuello2_prom = np.mean(np.array(cuello2)[:, 1])
        if cuello1_prom <= cuello2_prom:
            cuello_izq = cuello1
            cuello_der = cuello2
        else:
            cuello_izq = cuello2
            cuello_der = cuello1
        if brd1_prom <= brd2_prom:
            brd_izq = brd1
            brd_der = brd2
        else:
            brd_izq = brd2
            brd_der = brd1

        izq = brd_izq + cuello_izq
        der = brd_der + cuello_der
        return izq, der