import numpy as np
import collections
from Modelo.Operador_Sobel import Operador_Sobel
from Modelo.Visualizador_operaciones import Visualizador_operaciones


class Seguidor_de_contorno:

    sobel = Operador_Sobel()
    visualizador = Visualizador_operaciones()




    def aplicar_seguimiento_vertical(self, maxilar, mandibular, largos_maxilar, largos_mandibular, imagen):
        set_maxilar, ponderaciones1 = self.seguimiento_vertical(maxilar, imagen, largos_maxilar, -1)
        set_maxilar_corona, ponderaciones1 = self.seguimiento_vertical(maxilar, imagen, largos_maxilar//4, 1)
        set_mandibular, ponderaciones = self.seguimiento_vertical(mandibular, imagen, largos_mandibular, 1)
        set_mandibular_corona, ponderaciones = self.seguimiento_vertical(mandibular, imagen, largos_mandibular//4, -1)
        set_general = set_maxilar | set_maxilar_corona | set_mandibular
        img_maxilar = self.visualizador.set_sobre_imagen(imagen, set_maxilar)
        img_maxilar = self.visualizador.set_sobre_imagen(img_maxilar, set_maxilar_corona)
        img_final = self.visualizador.set_sobre_imagen(img_maxilar, set_mandibular)
        img_final = self.visualizador.set_sobre_imagen(img_final, set_mandibular_corona)
        return img_final, ponderaciones, list(set_general)


    def seguimiento_vertical(self, lista_puntos, imagen, largos_raices, direccion=-1):
        puntos_recorrer = list(lista_puntos)
        puntos_visitados = set()
        imagen_magnitud = self.sobel.magnitud_sobel(imagen)

        imagen_orientacion = self.sobel.orientacion_sobel(imagen)
        #imagen_magnitud = self.canny.supresion_no_maximos_canny(imagen_m, imagen_orientacion)
        h, w = imagen.shape

        #Constantes para el criterio de similitud
        ponderaciones = [0.70, 0.15, 0.15]                             #Peso a la similitud en magnitud
        radio = 1                                       #Radio de la ventana horizontal


        #Constantes de castigo si el pixel se aleja de la inercia (inicial y / o dinamica)
        inercia_inicial = collections.deque(maxlen=10)   # Pixeles en cuenta para direccion inicial
        inercia_dinamica = collections.deque(maxlen=10)  # Historial de pixeles para inercia dinamica
        inercia_inicial_peso = 1
        inercia_dinamica_peso = 1
        penalizacion_base = 0.6
        penalizacion_dinamica = 0.8                       #Castigo aplicado cuando la magnitud es pequeña
        historial_magnitud = collections.deque(maxlen=5)
        prom_global = np.mean(imagen_magnitud)


        for punto_inicial, largo in zip(puntos_recorrer, largos_raices):

            punto_actual = punto_inicial

            if punto_actual in puntos_visitados:
                continue

            for paso in range(largo):
                if punto_actual not in puntos_visitados:
                    puntos_visitados.add(punto_actual)
                y, x = punto_actual
                if y < 1 or y > h - 2: continue
                if x < radio or x > w - radio - 1: continue
                inercia_dinamica.append(punto_actual)

                if len(inercia_inicial) < inercia_inicial.maxlen:
                    inercia_inicial.append(punto_actual)
                #no se te olvide agregar una funcion que pase del set a blanco en la image
                magnitud = imagen_magnitud[punto_actual]
                orientacion = imagen_orientacion[punto_actual]
                intensidad = imagen[punto_actual]
                historial_magnitud.append(magnitud)
                #promedio_historial_magnitud = np.mean(historial_magnitud)
                vecinos_magnitud = imagen_magnitud[y + direccion, x - radio:x + radio + 1]
                vecinos_intensidad = imagen[y + direccion, x - radio:x + radio + 1]
                vecinos_orientacion = imagen_orientacion[y + direccion, x - radio:x + radio + 1]
                diferencias = self.obtener_diferencias(vecinos_magnitud, vecinos_orientacion, vecinos_intensidad, magnitud, orientacion, intensidad, ponderaciones)

                penalizacion_acumulada = np.ones(2 * radio + 1)

                if len(inercia_inicial) == inercia_inicial.maxlen and 0 == 1:
                    desviaciones = self.calcular_desviacion_angular(punto_actual, radio, inercia_inicial, direccion)
                    penalizacion_magnitud = self.penalizacion_confianza_gradiente(prom_global, magnitud)
                    pen_inicial = self.calcular_penalizaciones_totales(desviaciones, penalizacion_magnitud,
                                                                       penalizacion_base, penalizacion_dinamica)
                    penalizacion_acumulada += (pen_inicial - 1) * inercia_inicial_peso



                if len(inercia_dinamica) == inercia_dinamica.maxlen:
                    if np.mean(historial_magnitud) <= (prom_global * 0.3):
                        desviaciones = self.calcular_desviacion_angular(punto_actual, radio, inercia_dinamica, direccion)
                        penalizacion_magnitud = self.penalizacion_confianza_gradiente(prom_global, magnitud)
                        pen_dinamica = self.calcular_penalizaciones_totales(desviaciones, penalizacion_magnitud,
                                                                            penalizacion_base, penalizacion_dinamica)
                        penalizacion_acumulada += (pen_dinamica - 1) * inercia_dinamica_peso


                diferencias = diferencias * penalizacion_acumulada

                idx = np.argmin(diferencias) - radio
                mejor_candidato = (y + direccion, x + idx)
                punto_actual = mejor_candidato

            #a esta altura limpieza
            historial_magnitud.clear()
            inercia_inicial.clear()
            inercia_dinamica.clear()

        return puntos_visitados, ponderaciones

    #-------------------SEGUIDOR EXPERIMENTAL-------------------------


    def aplicar_seguimiento_vertical_exp(self, maxilar, mandibular, largos_maxilar, largos_mandibular, imagen, bordes_tst):
        set_maxilar = self.seguimiento_vertical_exp(maxilar, imagen, largos_maxilar, bordes_tst, -1)
        set_maxilar_corona = self.seguimiento_vertical_exp(maxilar, imagen, largos_maxilar//4, bordes_tst,1)
        set_mandibular = self.seguimiento_vertical_exp(mandibular, imagen, largos_mandibular, bordes_tst,1)
        set_mandibular_corona = self.seguimiento_vertical_exp(mandibular, imagen, largos_mandibular//4, bordes_tst,-1)
        set_general = set_maxilar | set_maxilar_corona | set_mandibular | set_mandibular_corona
        return list(set_general)


    def seguimiento_vertical_exp(self, lista_puntos, imagen, largos_raices, bordes_tst, direccion=-1):
        puntos_recorrer = list(lista_puntos)
        puntos_visitados = set()
        imagen_magnitud = self.sobel.magnitud_sobel(imagen)
        imagen_orientacion = self.sobel.orientacion_sobel(imagen)
        h, w = imagen.shape
        ponderaciones = [0.80, 0.10, 0.10]                             #Peso a la similitud en magnitud
        radio = 1                                                      #Radio de la ventana horizontal
        bordes_tst = set(bordes_tst)


        #Constantes de castigo si el pixel se aleja de la inercia (inicial y / o dinamica)
        inercia_inicial = collections.deque(maxlen=10)   # Pixeles en cuenta para direccion inicial
        inercia_dinamica = collections.deque(maxlen=10)  # Historial de pixeles para inercia dinamica
        inercia_inicial_peso = 2.4
        inercia_dinamica_peso = 0.5
        penalizacion_base = 0.6
        penalizacion_dinamica = 0.8                       #Castigo aplicado cuando la magnitud es pequeña
        historial_magnitud = collections.deque(maxlen=5)
        prom_global = np.mean(imagen_magnitud)


        for punto_inicial, largo in zip(puntos_recorrer, largos_raices):

            punto_actual = punto_inicial

            if punto_actual in puntos_visitados:
                continue



            for paso in range(largo):



                if punto_actual not in puntos_visitados:
                    puntos_visitados.add(punto_actual)
                y, x = punto_actual
                if y < 1 or y > h - 2: continue
                if x < radio or x > w - radio - 1: continue
                inercia_dinamica.append(punto_actual)

                y_s = y + direccion

                candidatos_tst = [(y_s, x - 1), (y_s, x), (y_s, x + 1)]
                encontrado = False
                for pt in candidatos_tst:
                    if pt in bordes_tst:
                        punto_actual = pt
                        encontrado = True
                        break
                if encontrado:
                    continue

                if len(inercia_inicial) < inercia_inicial.maxlen:
                    inercia_inicial.append(punto_actual)
                #no se te olvide agregar una funcion que pase del set a blanco en la image
                magnitud = imagen_magnitud[punto_actual]
                orientacion = imagen_orientacion[punto_actual]
                intensidad = imagen[punto_actual]
                historial_magnitud.append(magnitud)
                #promedio_historial_magnitud = np.mean(historial_magnitud)
                vecinos_magnitud = imagen_magnitud[y + direccion, x - radio:x + radio + 1]
                vecinos_intensidad = imagen[y + direccion, x - radio:x + radio + 1]
                vecinos_orientacion = imagen_orientacion[y + direccion, x - radio:x + radio + 1]
                diferencias = self.obtener_diferencias(vecinos_magnitud, vecinos_orientacion, vecinos_intensidad, magnitud, orientacion, intensidad, ponderaciones)

                penalizacion_acumulada = np.ones(2 * radio + 1)


                if len(inercia_inicial) == inercia_inicial.maxlen:
                    desviaciones = self.calcular_desviacion_angular(punto_actual, radio, inercia_inicial, direccion)
                    penalizacion_magnitud = self.penalizacion_confianza_gradiente(prom_global, magnitud)
                    pen_inicial = self.calcular_penalizaciones_totales(desviaciones, penalizacion_magnitud,
                                                                       penalizacion_base, penalizacion_dinamica)
                    penalizacion_acumulada += (pen_inicial - 1) * inercia_inicial_peso

                if len(inercia_dinamica) == inercia_dinamica.maxlen:
                    if np.mean(historial_magnitud) <= (prom_global * 0.3):
                        desviaciones = self.calcular_desviacion_angular(punto_actual, radio, inercia_dinamica, direccion)
                        penalizacion_magnitud = self.penalizacion_confianza_gradiente(prom_global, magnitud)
                        pen_dinamica = self.calcular_penalizaciones_totales(desviaciones, penalizacion_magnitud,
                                                                            penalizacion_base, penalizacion_dinamica)
                        penalizacion_acumulada += (pen_dinamica - 1) * inercia_dinamica_peso


                diferencias = diferencias * penalizacion_acumulada

                idx = np.argmin(diferencias) - radio
                mejor_candidato = (y + direccion, x + idx)
                punto_actual = mejor_candidato

            #a esta altura limpieza
            historial_magnitud.clear()
            inercia_inicial.clear()
            inercia_dinamica.clear()

        return puntos_visitados






    def calcular_desviacion_angular(self, punto_actual, radio, historial_puntos, direccion):
        angulo_inercia = np.arctan2(historial_puntos[-1][0] - historial_puntos[0][0],
                                    historial_puntos[-1][1] - historial_puntos[0][1])
        cy, cx = punto_actual
        vecinos_x = np.arange(cx - radio, cx + radio + 1)
        vecinos_y = cy + direccion
        angulos_vecinos = np.arctan2(vecinos_y - cy, vecinos_x - cx)
        delta_theta = angulos_vecinos - angulo_inercia
        delta_theta = (delta_theta + np.pi) % (2 * np.pi) - np.pi   #Normalizcion del angulo a 180
        return delta_theta

    def penalizacion_confianza_gradiente(self, promedio_historial, magnitud):
        ratio_gradiente = magnitud / (promedio_historial + 1e-6)
        penalizacion = 1.0 - np.clip(ratio_gradiente, 0, 1)
        return penalizacion

    def calcular_penalizaciones_totales(self, desviaciones, penalizacion_magnitud, penalizacion_base, penalizacion_variable):
        k = penalizacion_base + (penalizacion_variable * penalizacion_magnitud)
        penalizaciones = 1.0 + k * np.abs(desviaciones)
        return penalizaciones




    def calcular_diferencia_escalar(self, valor, candidatos, tipo="m"):
        diferencias = np.abs(candidatos - valor)
        if tipo == "m":
            diferencias = diferencias * (100 / 1443.0)  #Diferencia en la magnitud de 0-100%
        if tipo == "o":
            diferencias = np.where(diferencias > 180, 360 - diferencias, diferencias)
            diferencias = diferencias * (100 / 180.0)   #Diferencia en la orientacion de 0-100%
        if tipo == "i":
            diferencias = diferencias * (100 / 255)  # Diferencia en la intensidad de 0-100%
        return diferencias

    def combinar_diferencias(self, magnitud, orientacion, intensidad, ponderaciones):
        return (magnitud * ponderaciones[0]) + (orientacion * ponderaciones[1]) + (intensidad * ponderaciones[2])

    def obtener_diferencias(self, vecinos_m, vecinos_o, vecinos_i, valor_m, valor_o, valor_i, ponderaciones):
        diferencias_m = self.calcular_diferencia_escalar(valor_m, vecinos_m, "m")
        diferencias_o = self.calcular_diferencia_escalar(valor_o, vecinos_o, "o")
        diferencias_i = self.calcular_diferencia_escalar(valor_i, vecinos_i, "i")
        diferencias = self.combinar_diferencias(diferencias_m, diferencias_o, diferencias_i, ponderaciones)
        return diferencias