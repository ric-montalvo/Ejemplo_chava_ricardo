import numpy as np
from Modelo.Filtrador_bordes_cuello_corona import Filtrador_bordes_cuello_corona
from Modelo.Bordes_coronarios import Bordes_coronarios
from Modelo.Bordes_ventana import bordes_ventana
from Modelo.Operador_Sobel import Operador_Sobel
from Modelo.Visualizador_operaciones import Visualizador_operaciones
from Modelo.Ajustador_inercia import Ajustador_inercia

class Seguidor_basado_vertices:

    filtrador = Filtrador_bordes_cuello_corona()
    brd_corona = Bordes_coronarios()
    brd_ventana = bordes_ventana()
    sobel = Operador_Sobel()
    visualizador = Visualizador_operaciones()
    ajustador = Ajustador_inercia()


    def orquestador(self, imagen, maxilar, mandibular):
        vert_max, vert_man = self.obtener_vertices(imagen, maxilar, mandibular)
        brd_ver_max, brd_ver_man = self.aplicar_seguimiento_magnitud_gradiente(imagen, maxilar, mandibular)

        return brd_ver_max, brd_ver_man


    def obtener_vertices(self, imagen, maxilar, mandibular):
        bordes_cuello, bordes_maxilar, bordes_mandibular, p = self.brd_corona.extraer_contornos_dentales(imagen, maxilar,
                                                                                                      mandibular)
        bordes_coronarios = bordes_maxilar + bordes_mandibular
        bordes_filtrados_tamanio = self.filtrador.filtrar_bordes_verticales_longitud_conexion(bordes_cuello, bordes_coronarios, -1.5)
        bordes_cuello_recortados = self.filtrador.cortar_bordes_verticales(bordes_filtrados_tamanio, bordes_maxilar, bordes_mandibular)
        vertices_cuello = self.filtrador.obtener_puntos_vertice(bordes_cuello_recortados)
        vertices_maxilares, vertices_mandibulares = self.filtrador.clasificar_vertices_por_hueso(vertices_cuello, bordes_maxilar, bordes_mandibular)
        return vertices_maxilares, vertices_mandibulares




    def aplicar_seguimiento_magnitud_gradiente(self, imagen, vertices_maxilares, vertices_mandibulares):
        """Vertices es lista de listas, puede contener tuplas"""
        bordes_vertices_max = []
        bordes_vertices_man = []

        sobel = np.abs(self.sobel.gx_sobel(imagen)) ** 1.3
        sobel = self.visualizador.mapear_a_visualizable(sobel)
        for punto in vertices_maxilares:
            borde = self.seguimiento_magnitud_gradiente(sobel, punto, 1, True)
            bordes_vertices_max.append(borde)

        for punto in vertices_mandibulares:
            borde = self.seguimiento_magnitud_gradiente(sobel, punto, 1, False)
            bordes_vertices_man.append(borde)

        max_extrapolada = self.aplicar_extrapolacion(bordes_vertices_max, 100, True)
        man_extrapolada = self.aplicar_extrapolacion(bordes_vertices_man, 100, False)
        #tmax = self.aplicar_contorno_activo(bordes_vertices_max, imagen)
        #tman = self.aplicar_contorno_activo(bordes_vertices_man, imagen)

        grlmax = max_extrapolada + bordes_vertices_max
        grlman = man_extrapolada + bordes_vertices_man


        return bordes_vertices_max, bordes_vertices_man


    def seguimiento_magnitud_gradiente(self, sobel_gx, punto, radio=1, es_maxilar=True):
        """Vertices es lista de tuplas (y, x). Retorna lista de tuplas."""
        h, w = sobel_gx.shape
        puntos_visitados = set()
        punto = tuple(punto)
        max_len = 5                 # máximo de puntos de visión a futuro
        tolerancia = 0.40          # qué tan pequeño puede ser la magnitud respecto al actual
        dy = -1 if es_maxilar else 1


        while True:
            puntos_visitados.add(punto)
            y, x = punto
            magnitud_actual = sobel_gx[punto]
            magnitud_minima = sobel_gx[punto] * tolerancia
            y_siguiente = y + dy
            if y_siguiente < 0 or y_siguiente >= h:
                break
            x_ini = max(0, x - radio)
            x_fin = min(w, x + radio + 1)

            vecinos = [(y_siguiente, nx) for nx in range(x_ini, x_fin)]
            if not vecinos:
                break
            valores_y_coords = [(sobel_gx[vy, vx], (vy, vx)) for vy, vx in vecinos]
            valor_maximo, coordenada_maxima = max(valores_y_coords)
            if valor_maximo > magnitud_minima:
                punto = coordenada_maxima
            else:
                if es_maxilar:  # Hacia arriba (Y disminuye)
                    y_ini_ventana = max(0, y_siguiente - max_len + 1)
                    y_fin_ventana = y_siguiente + 1
                else:
                    y_ini_ventana = y_siguiente
                    y_fin_ventana = min(h, y_siguiente + max_len)

                vecinos_interpolar = sobel_gx[y_ini_ventana:y_fin_ventana, x_ini:x_fin]

                if vecinos_interpolar.size == 0:
                    break

                valor_max_interpolar = np.max(vecinos_interpolar)
                if valor_max_interpolar < magnitud_minima:
                    break

                idx_max_flat = np.argmax(vecinos_interpolar)
                local_y, local_x = np.unravel_index(idx_max_flat, vecinos_interpolar.shape)
                abs_y = y_ini_ventana + local_y
                abs_x = x_ini + local_x
                cc_max_interpolar = (abs_y, abs_x)

                puntos_interpolados = self.brd_corona.interpolar_puntos(punto, cc_max_interpolar)
                puntos_visitados.update(tuple(p) for p in puntos_interpolados)
                punto = cc_max_interpolar

        return list(puntos_visitados)

    def aplicar_extrapolacion(self, rectas, pasos = 100, es_maxilar = True, ):
        rectas_extrapoladas = []
        for recta in rectas:
            if es_maxilar:
                dy = -1
            else:
                dy = 1

            extrapolacion = self.extrapolar_borde(recta, pasos, dy, 1, True)
            rectas_extrapoladas.append(extrapolacion)


        return rectas_extrapoladas

    def extrapolar_borde(self, puntos, n_pasos, direccion_y=1, tamaño_paso_y=1.0, conectar_exacto=True):
        """
        Extrapola un borde confiable (ej. Sobel) hacia una dirección específica.

        :param puntos: Lista de píxeles/puntos en formato [(y, x)]. No necesitan estar ordenados.
        :param n_pasos: Cantidad de píxeles/puntos a proyectar.
        :param direccion_y: 1 para proyectar hacia valores Y positivos (abajo en la imagen),
                            -1 para proyectar hacia valores Y negativos (arriba en la imagen).
        :param tamaño_paso_y: Distancia entre puntos (usualmente 1.0 para píxeles continuos).
        :param conectar_exacto: Si es True, fuerza a que la recta nazca exactamente del
                                último píxel real para evitar "saltos" en el dibujo.
        :return: Lista de puntos proyectados [(y, x)].
        """
        if len(puntos) < 2:
            return puntos
        # 1. Separar coordenadas
        y = np.array([p[0] for p in puntos])
        x = np.array([p[1] for p in puntos])

        # 2. Ajuste lineal general (sigue funcionando perfecto aunque estén desordenados)
        coeficientes = np.polyfit(y, x, 1)
        pendiente_m = coeficientes[0]
        intercepto_b = coeficientes[1]

        # 3. Encontrar el punto de ancla (el extremo desde donde proyectaremos)
        # Si vamos hacia Y positivos, partimos del Y más grande que tengamos.
        # Si vamos hacia Y negativos, partimos del Y más pequeño.
        if direccion_y > 0:
            indice_extremo = np.argmax(y)
        else:
            indice_extremo = np.argmin(y)

        y_ancla = y[indice_extremo]
        x_ancla = x[indice_extremo]

        # 4. Forzar la conexión exacta con el borde de Sobel (Opcional pero recomendado)
        if conectar_exacto:
            # Recalculamos el intercepto para que pase por (y_ancla, x_ancla)
            intercepto_b = x_ancla - (pendiente_m * y_ancla)

        funcion_recta_x = np.poly1d([pendiente_m, intercepto_b])

        # 5. Generar la proyección
        # Usamos np.sign para asegurar que la dirección sea puramente +1 o -1
        direccion_limpia = np.sign(direccion_y)

        nuevos_y = [y_ancla + (i * tamaño_paso_y * direccion_limpia) for i in range(1, n_pasos + 1)]
        nuevos_x = funcion_recta_x(nuevos_y)

        # 6. Devolver en formato de imagen (Y, X)

        puntos_proyectados = [(int(round(ny)), int(round(nx))) for ny, nx in zip(nuevos_y, nuevos_x)]

        return puntos_proyectados