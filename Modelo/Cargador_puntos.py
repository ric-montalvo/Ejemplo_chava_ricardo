from Modelo.Validador_puntos import Validador_puntos
from Modelo.Utilidades_npListas import Utilidades_npListas
import numpy as np
import statistics

class Cargador_puntos:
    validador = Validador_puntos()
    utl = Utilidades_npListas()

    #Aca debe de ir la logica de lectura del csv externo
    def obtener_puntos_por_arcada(self):
        maxilar = [(450, 562), (448, 576), (446, 602), (460, 624), (462, 647), (466, 664), (463, 673), (469, 687),
                   (474, 702), (477, 715), (485, 752), (477, 762), (486, 816), (495, 826), (500, 878), (499, 891),
                   (500, 949), (509, 963), (480, 985), (482, 1005), (499, 1022), (500, 1037), (494, 1084), (483, 1098),
                   (460, 1115), (459, 1128), (480, 1148), (481, 1170), (475, 1192), (477, 1206), (461, 1244),
                   (463, 1260), (453, 1281), (453, 1308), (442, 1325), (461, 1339)]
        mandibular = [(571, 451), (571, 477), (618, 552), (602, 572), (644, 644), (638, 662), (659, 705), (651, 720),
                      (668, 765), (667, 781), (673, 831), (675, 841), (679, 886), (679, 897), (684, 940), (684, 953),
                      (679, 997), (679, 1009), (676, 1053), (676, 1066), (649, 1116), (668, 1132), (638, 1175),
                      (658, 1195), (628, 1234), (645, 1253), (620, 1264), (621, 1301), (610, 1320), (613, 1344),
                      (593, 1360), (594, 1391), (569, 1415), (570, 1435)]
        name = "LAURA CAROLINA HERNANDEZ"
        return maxilar, mandibular

    def obtener_ancho_entre_puntos(self):
        maxilar_ancho = 0

        mandibular_ancho = 0

        return maxilar_ancho, mandibular_ancho



    def separar_maxilar_mandibular(self, puntos):
        if len(puntos) < 2:
            return puntos, []
        puntos_ordenados = sorted(puntos, key=lambda punto: punto[0])
        max_salto = 0
        indice_de_corte = 0
        for i in range(len(puntos_ordenados) - 1):
            y_actual = puntos_ordenados[i][0]
            y_siguiente = puntos_ordenados[i + 1][0]
            salto = y_siguiente - y_actual

            if salto > max_salto:
                max_salto = salto
                indice_de_corte = i + 1
        maxilar = puntos_ordenados[:indice_de_corte]
        mandibular = puntos_ordenados[indice_de_corte:]

        return maxilar, mandibular

    def obtener_largo_raices(self, lista_puntos, valor):
        largo_raices = np.full(len(lista_puntos), valor)
        return largo_raices

    def obtener_puntos_validos(self, magnitud, radio=3):
        maxilar, mandibular = self.obtener_puntos_por_arcada()
        maxilar_validos = self.validador.obtener_puntos_validos(maxilar, magnitud, radio)
        mandibular_validos = self.validador.obtener_puntos_validos(mandibular, magnitud, radio)
        return maxilar_validos, mandibular_validos

    def obtener_puntos_visualizables(self, lista_puntos, imagen, radio=1):
        h, w = imagen.shape
        return [
            (i, j)
            for y, x in lista_puntos
            for i in range(max(0, y - radio), min(h, y + radio + 1))
            for j in range(max(0, x - radio), min(w, x + radio + 1))
        ]