import numpy as np
import math
from Modelo.Operaciones_anchura import Operaciones_anchura
from Modelo.Metodos_numericos import Metodos_numericos


class Metricas:
    anchura = Operaciones_anchura()
    met = Metodos_numericos()


    def Orquestador(self, dientes_maxilares, dientes_mandibulares, centros_maxilares, centros_mandibulares,
                    coronas_max, coronas_man, cuellos_max, cuellos_man, anchuras_max, anchuras_man,
                    maxilares_ver, mandibulares_ver, puntos_maxilares, puntos_mandibulares, w):



        maxilares_etiquetados = self.etiquetar_lista_dientes(dientes_maxilares, w, centros_maxilares, True)
        mandibulares_etiquetados = self.etiquetar_lista_dientes(dientes_mandibulares, w, centros_mandibulares, False)

        inclinacion_max = self.obtener_angulo_inclinacion(cuellos_max, maxilares_ver, anchuras_max, maxilares_etiquetados)
        inclinacion_man = self.obtener_angulo_inclinacion(cuellos_man, mandibulares_ver, anchuras_man, mandibulares_etiquetados)

        proporciones_max = self.obtener_proporcion_corona_raiz(coronas_max, maxilares_ver, cuellos_max, anchuras_max, maxilares_etiquetados, True)
        proporciones_man = self.obtener_proporcion_corona_raiz(coronas_man, mandibulares_ver, cuellos_man, anchuras_man, mandibulares_etiquetados, False)

        largos_max = self.obtener_largo_raices(maxilares_ver, cuellos_max, anchuras_max, maxilares_etiquetados, True)
        largos_man = self.obtener_largo_raices(mandibulares_ver, cuellos_man, anchuras_man, mandibulares_etiquetados, False)


        distancias_max, ubicaciones_max = self.obtener_tamanio_diastemas(maxilares_ver, cuellos_max, puntos_maxilares, anchuras_max, maxilares_etiquetados)
        distancias_man, ubicaciones_man = self.obtener_tamanio_diastemas(mandibulares_ver, cuellos_man, puntos_mandibulares, anchuras_man, mandibulares_etiquetados)

        maxilares_datos = self.agrupar_id(inclinacion_max, proporciones_max, largos_max, distancias_max, ubicaciones_max)
        mandibulares_datos = self.agrupar_id(inclinacion_man, proporciones_man, largos_man, distancias_man, ubicaciones_man)

        resultados = mandibulares_datos + maxilares_datos




        return resultados


    def etiquetar_lista_dientes(self, dientes, w, centros, es_Maxilar = True):
        """
        1-8, 9-16       TOT = 16
        32-25, 24-17    TOT = 16
        :param dientes:
        :param es_Maxilar:
        :return:
        """
        dientes_etiquetados = []
        centros_ord = sorted(centros, key=lambda centro: centro[1])
        piezas_completas = list(zip(dientes, centros_ord))
        media = w //2
        img_izquierda = [p for p in piezas_completas if p[1][1] >= media]
        img_derecha = [p for p in piezas_completas if p[1][1] < media]

        if es_Maxilar:
            ini_der,  fin_der = 8, 1
            ini_izq, fin_izq  = 9, 16
            dx = 1
        else:
            ini_der, fin_der = 25, 32
            ini_izq, fin_izq = 24, 17
            dx = -1

        for diente, centro in img_izquierda:
            tupla = (ini_izq, diente)
            dientes_etiquetados.append(tupla)
            ini_izq = ini_izq  + dx

        dif_dientes = (fin_izq - ini_izq) * dx

        for i in range(0, dif_dientes):
            tupla = (ini_izq, [])
            dientes_etiquetados.append(tupla)
            ini_izq = ini_izq + dx


        for diente, centro in reversed(img_derecha):
            tupla = (ini_der, diente)
            dientes_etiquetados.append(tupla)
            ini_der = ini_der - dx

        dif_dientes = (fin_der - ini_der) * (-dx)

        for i in range(0, dif_dientes):
            tupla = (ini_der, [])
            dientes_etiquetados.append(tupla)
            ini_der = ini_der - dx
        return dientes_etiquetados


    def obtener_angulo_inclinacion(self, cuellos, verticales, anchuras, dientes):
        inclinaciones = []
        for anchura in anchuras:
            izq, der = self.anchura.obtener_bordes_verticales_conectados(anchura, verticales, cuellos)
            set_izq = set(izq)
            set_der = set(der)
            puntos_medios = self.calcular_puntos_medios(izq, der)
            ids = [id_ for id_, brd in dientes if set_izq.union(set_der).issubset(brd)]
            inclinacion = self.calcular_angulo_inclinacion(puntos_medios)
            tupla = (ids, inclinacion)
            inclinaciones.append(tupla)
        return inclinaciones

    def obtener_proporcion_corona_raiz(self, corona, verticales, cuellos, anchuras, dientes, es_Maxilar = True):
        proporciones = []
        for anchura in anchuras:
            #medio>mas bajo

            #medio
            anchura_sorted = sorted(anchura, key=lambda anchura: anchura[1])
            centro = anchura_sorted[len(anchura_sorted) // 2]

            #punto corona
            izq, der = self.anchura.obtener_bordes_verticales_conectados(anchura, verticales, cuellos)
            set_izq = set(izq)
            set_der = set(der)
            corona_acotada = self.anchura.corona_conectada(izq, der, corona, es_Maxilar)


            id = [id_ for id_, brd in dientes if set_izq.union(set_der).issubset(brd)]

            pto_corona = (
                max(corona_acotada, key=lambda p: p[0]) if es_Maxilar
                else min(corona_acotada, key=lambda p: p[0])
            )
            puntos_diente_actual = [
                punto for id_, puntos_diente in dientes
                if id_ in id
                for punto in puntos_diente
            ]

            if puntos_diente_actual:
                pto_raiz = (
                    min(puntos_diente_actual, key=lambda p: p[0]) if es_Maxilar
                    else max(puntos_diente_actual, key=lambda p: p[0])
                )
            else:
                pto_raiz = (0, 0)


            distancia_corona_centro = abs(centro[0] - pto_corona[0])
            distancia_centro_raiz = abs(centro[0] - pto_raiz[0])
            proporcion = distancia_centro_raiz / distancia_corona_centro

            proporciones.append((id, proporcion))

        return proporciones


    def obtener_largo_raices(self, verticales, cuellos, anchuras, dientes, es_Maxilar = True):
        largo_raices = []
        for anchura in anchuras:
            #medio>mas bajo
            #medio
            anchura_sorted = sorted(anchura, key=lambda anchura: anchura[1])
            centro = anchura_sorted[len(anchura_sorted) // 2]

            #punto corona
            izq, der = self.anchura.obtener_bordes_verticales_conectados(anchura, verticales, cuellos)
            set_izq = set(izq)
            set_der = set(der)


            id = [id_ for id_, brd in dientes if set_izq.union(set_der).issubset(brd)]
            puntos_diente_actual = [
                punto for id_, puntos_diente in dientes
                if id_ in id
                for punto in puntos_diente
            ]

            if puntos_diente_actual:
                pto_raiz = (
                    min(puntos_diente_actual, key=lambda p: p[0]) if es_Maxilar
                    else max(puntos_diente_actual, key=lambda p: p[0])
                )
            else:
                pto_raiz = (0, 0)

            largo = abs(centro[0] - pto_raiz[0])

            largo_raices.append((id, largo))
        return largo_raices


    def obtener_tamanio_diastemas(self, verticales, cuellos, puntos, anchuras, dientes):
        diastemas = self.anchura.obtener_diastemas(puntos)
        distancias = []
        ubicaciones = []
        temp = []
        for anchura in anchuras:
            izq, der = self.anchura.obtener_bordes_verticales_conectados(anchura, verticales, cuellos)
            set_izq = set(izq)
            set_der = set(der)
            id = [id_ for id_, brd in dientes if set_izq.union(set_der).issubset(brd)]
            set_l1 = set(der)
            sublista_encontrada = next((sub for sub in diastemas if not set_l1.isdisjoint(sub)), None)
            if sublista_encontrada:
                sub_ordenada = sorted(sublista_encontrada, key=lambda sub: sub[1])
                p1 = sub_ordenada[0]
                p2 = sub_ordenada[-1]
                distancia = abs(p1[1]-p2[1])
                ubicacion = sub_ordenada [len(sub_ordenada)// 2]
                if distancia == 0: ubicacion = p1
                tupla_dist = (id, distancia)
                temp.append(ubicacion)
            else:
                tupla_dist = (id, 0)
                ubicacion = 0

            ubicaciones.append((id, ubicacion))
            distancias.append(tupla_dist)

        return distancias, ubicaciones

    def agrupar_id(self, l1, l2, l3, l4, l5):
        d1 = {tuple(k): v for k, v in l1}
        d2 = {tuple(k): v for k, v in l2}
        d3 = {tuple(k): v for k, v in l3}
        d4 = {tuple(k): v for k, v in l4}
        d5 = {tuple(k): v for k, v in l5}

        resultado = [
            (list(id_), d1[id_], d2[id_], d3[id_], d4[id_], d5[id_])
            for id_ in d1.keys()
        ]
        return resultado



    def calcular_puntos_medios(self, lista1, lista2):
        if len(lista1) <= len(lista2):
            lista_corta = lista1
            lista_larga = lista2
        else:
            lista_corta = lista2
            lista_larga = lista1
        dict_larga = {y: x for y, x in lista_larga}
        puntos_medios = []

        for y, x_corta in lista_corta:
            if y in dict_larga:
                x_larga = dict_larga[y]
                x_medio = (x_corta + x_larga) // 2
                puntos_medios.append((y, x_medio))

        return puntos_medios

    def calcular_angulo_inclinacion(self, puntos_medios):
        if len(puntos_medios) < 2:
            return 0.0
        Y = np.array([p[0] for p in puntos_medios])
        X = np.array([p[1] for p in puntos_medios])

        m, b = np.polyfit(Y, X, 1)
        angulo_rad = math.atan2(1, m)

        angulo_deg = math.degrees(angulo_rad)
        angulo_final = angulo_deg % 180

        return angulo_final