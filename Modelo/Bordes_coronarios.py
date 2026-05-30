import numpy as np
from collections import deque
from Modelo.Operador_Sobel import Operador_Sobel
from Modelo.Visualizador_operaciones import Visualizador_operaciones
from Modelo.Bordes_ventana import bordes_ventana
from Modelo.Cargador_puntos import Cargador_puntos
from Modelo.Utilidades_npListas import Utilidades_npListas


class Bordes_coronarios:
    sobel = Operador_Sobel()
    visualizador = Visualizador_operaciones()
    brd = bordes_ventana()
    puntos = Cargador_puntos()
    utilidades = Utilidades_npListas()

    def extraer_contornos_dentales(self, imagen, maxilares, mandibulares):
        radio, max_len, tolerancia_h, tolerancia_v = 2, 6, 0.20, 0.4
        r_y, r_x = self.calcular_limites_roi(maxilares + mandibulares)
        sobel_gy = np.abs(self.sobel.gy_sobel(imagen))
        sobel = self.sobel.magnitud_sobel(imagen)
        sobel_gy = self.atenuar_ruido_gradiente(sobel_gy, 1.1)
        sobel = self.atenuar_ruido_gradiente(sobel, 1.3)

        def procesar_arcada(puntos_iniciales, dir_vertical, es_maxilar):
            # 1. Seguimiento vertical
            bordes_vert = self.rastrear_borde_direccional(
                sobel, puntos_iniciales, dir_vertical, radio, max_len, tolerancia_v, es_horizontal=False
            )
            filtrados = self.eliminar_trazos_cortos(self.agrupar_pixeles_conectados_dfs(bordes_vert), 20)

            # 2. Puntos de oclusión y barrido horizontal (ambas direcciones)
            p_oclusion = self.obtener_extremos_oclusales(filtrados, es_maxilar)

            bh_der = self.rastrear_borde_direccional(sobel, p_oclusion, 1, radio + 2, max_len + 10, tolerancia_h,
                                                     es_horizontal=True)
            bh_izq = self.rastrear_borde_direccional(sobel, p_oclusion, -1, radio + 2, max_len + 10, tolerancia_h,
                                                     es_horizontal=True)

            # Bordes agrupados
            bh_der = self.agrupar_pixeles_conectados_dfs(bh_der)
            bh_izq = self.agrupar_pixeles_conectados_dfs(bh_izq)

            # 3. Limpieza de las coronas
            brd_ROI_der = self.recortar_fuera_del_roi(bh_der, r_y, r_x)
            brd_ROI_izq = self.recortar_fuera_del_roi(bh_izq, r_y, r_x)

            bfs_max_der = self.aplicar_bfs(brd_ROI_der)
            bfs_max_izq = self.aplicar_bfs(brd_ROI_izq)

            borde_final = brd_ROI_der + brd_ROI_izq

            return filtrados, borde_final, p_oclusion

        # Procesado limpio
        max_filtrados, borde_horizontal_maxilar, p = procesar_arcada(maxilares, 1, es_maxilar=True)
        man_filtrados, borde_horizontal_mandibular, pm = procesar_arcada(mandibulares, -1, es_maxilar=False)
        p = p + pm

        bhmax = self.utilidades.aplanar_lista_de_tuplas(borde_horizontal_maxilar)
        bhman = self.utilidades.aplanar_lista_de_tuplas(borde_horizontal_mandibular)

        borde_horizontal_maxilar = self.filtrar_cercania_oclusion(bhmax)
        borde_horizontal_mandibular = self.filtrar_cercania_oclusion(bhman, False)

        borde_horizontal_maxilar = self.unir_e_interpolar_por_x(borde_horizontal_maxilar)
        borde_horizontal_mandibular = self.unir_e_interpolar_por_x(borde_horizontal_mandibular)

        # borde_horizontal_maxilar = self.agrupar_pixeles_conectados_dfs(borde_horizontal_maxilar)
        # borde_horizontal_mandibular = self.agrupar_pixeles_conectados_dfs(borde_horizontal_mandibular)

        # Generalizar bordes a retornar
        bordes_cuello_filtrados = self.recortar_fuera_del_roi(max_filtrados + man_filtrados, r_y, r_x)

        return bordes_cuello_filtrados, borde_horizontal_maxilar, borde_horizontal_mandibular, sobel



    def rastrear_borde_direccional(self, sobel, puntos, direccion, radio, longitud_max, tolerancia,
                                   es_horizontal=False):
        h, w = sobel.shape
        puntos_visitados = set()

        for punto_inicial in puntos:
            punto_actual = punto_inicial
            if punto_actual in puntos_visitados:
                continue

            while True:
                puntos_visitados.add(punto_actual)
                y, x = punto_actual

                if (y < radio or y > h - radio - 1) or (x < radio or x > w - radio - 1): break

                tolerancia_magnitud = sobel[punto_actual] * tolerancia

                encontro_siguiente = False

                for i in range(1, longitud_max + 1):
                    if es_horizontal:
                        x_paso = int(x + (direccion * i))
                        if x_paso < 0 or x_paso >= w: break
                        candidatos = [(y + dy, x_paso) for dy in range(-radio, radio + 1)]
                    else:
                        y_paso = int(y + (direccion * i))
                        if y_paso < 0 or y_paso >= h: break
                        candidatos = [(y_paso, x + dx) for dx in range(-radio, radio + 1)]

                    siguiente_punto = max(candidatos, key=lambda coord: sobel[coord[0], coord[1]])

                    if sobel[siguiente_punto] > tolerancia_magnitud:
                        puntos_visitados.update(self.interpolar_puntos(punto_actual, siguiente_punto))
                        punto_actual = siguiente_punto
                        encontro_siguiente = True
                        break

                if not encontro_siguiente:
                    break

        return list(puntos_visitados)

    def agrupar_pixeles_conectados_dfs(self, lista_tuplas):
        tuplas_restantes = set(lista_tuplas)
        grupos = []
        movimientos = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        while tuplas_restantes:
            inicio = tuplas_restantes.pop()
            grupo_actual = [inicio]
            pila = [inicio]
            while pila:
                actual = pila.pop()
                y, x = actual
                for dy, dx in movimientos:
                    vecino = (y + dy, x + dx)
                    if vecino in tuplas_restantes:
                        tuplas_restantes.remove(vecino)
                        grupo_actual.append(vecino)
                        pila.append(vecino)
            grupos.append(grupo_actual)
        return grupos

    def eliminar_trazos_cortos(self, listas_tuplas, n):
        longitudes = [len(grupo) for grupo in listas_tuplas if len(grupo) > 0]
        if not longitudes:
            return []
        umbral = np.percentile(longitudes, n)
        return [grupo for grupo in listas_tuplas if len(grupo) >= umbral and len(grupo) > 0]

    def atenuar_ruido_gradiente(self, gradiente, potencia=1.3):
        gradiente_abs = abs(gradiente)
        dispersion_ruido = gradiente_abs ** potencia
        gradiente_reducido = self.visualizador.mapear_a_visualizable(dispersion_ruido)
        return gradiente_reducido

    def obtener_extremos_oclusales(self, listas_tuplas, es_maxilar):
        puntos_representativos = []
        for grupo in listas_tuplas:
            if not grupo:
                continue
            if es_maxilar:
                punto_extremo = max(grupo, key=lambda punto: punto[0])
            else:
                punto_extremo = min(grupo, key=lambda punto: punto[0])
            puntos_representativos.append(punto_extremo)
        return puntos_representativos

    def interpolar_puntos(self, p1, p2):
        y1, x1 = p1
        y2, x2 = p2
        distancia = max(abs(y2 - y1), abs(x2 - x1))
        if distancia == 0:
            return [p1]

        y_vals = np.round(np.linspace(y1, y2, distancia + 1)).astype(int)
        x_vals = np.round(np.linspace(x1, x2, distancia + 1)).astype(int)
        return list(zip(y_vals, x_vals))

    def recortar_fuera_del_roi(self, lista_bordes, rango_y, rango_x):
        min_y, max_y = rango_y
        min_x, max_x = rango_x
        listas_filtradas = []

        for borde in lista_bordes:
            if not borde:
                listas_filtradas.append([])
                continue
            arr = np.asarray(borde)
            mask = (arr[:, 0] >= min_y) & (arr[:, 0] <= max_y) & \
                   (arr[:, 1] >= min_x) & (arr[:, 1] <= max_x)
            listas_filtradas.append(arr[mask].tolist())
        return listas_filtradas

    def calcular_limites_roi(self, lista_puntos):
        if not lista_puntos:
            return (0, 0), (0, 0)
        arr = np.asarray(lista_puntos)
        rango_y = (int(arr[:, 0].min()), int(arr[:, 0].max()))
        rango_x = (int(arr[:, 1].min()), int(arr[:, 1].max()))
        return rango_y, rango_x

    def conservar_trazos_mas_largos(self, lista_bordes, n=2):
        listas_ordenadas = sorted(lista_bordes, key=len, reverse=True)
        return listas_ordenadas[:n]

    def obtener_extremos_horizontales(self, lista_puntos):
        if not lista_puntos:
            return None
        minimo = min(lista_puntos, key=lambda punto: punto[1])
        maximo = max(lista_puntos, key=lambda punto: punto[1])
        return minimo, maximo

    def extraer_camino_principal_bfs(self, lista_puntos):
        if not lista_puntos: return []

        lista_tuplas = sorted([tuple(p) for p in lista_puntos], key=lambda p: (p[1], p[0]))
        inicio, fin = lista_tuplas[0], lista_tuplas[-1]
        nodos_validos = set(lista_tuplas)

        cola = deque([inicio])
        visitados = {inicio}
        padres = {inicio: None}
        direcciones = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

        while cola:
            actual = cola.popleft()
            if actual == fin: break

            y, x = actual
            for dy, dx in direcciones:
                vecino = (y + dy, x + dx)
                if vecino in nodos_validos and vecino not in visitados:
                    visitados.add(vecino)
                    padres[vecino] = actual
                    cola.append(vecino)

        if fin not in padres: return []

        camino = []
        nodo = fin
        while nodo is not None:
            camino.append(nodo)
            nodo = padres[nodo]

        return camino[::-1]

    def aplicar_bfs(self, lista_bordes):
        bordes_limpios = []
        for brd in lista_bordes:
            borde = self.extraer_camino_principal_bfs(brd)
            bordes_limpios.extend(borde)
        return bordes_limpios

    def filtrar_cercania_oclusion(self, puntos, es_maxilar=True):
        # 1. Diccionario para guardar la mejor 'y' para cada 'x'
        mejor_y_por_x = {}

        # Como ahora es una lista plana, solo necesitamos un bucle
        for y, x in puntos:
            if x not in mejor_y_por_x:
                mejor_y_por_x[x] = y
            else:
                if es_maxilar:
                    mejor_y_por_x[x] = max(mejor_y_por_x[x], y)
                else:
                    mejor_y_por_x[x] = min(mejor_y_por_x[x], y)

        # 2. Reconstruir como una lista plana de puntos (y, x)
        # y ordenarlos de izquierda a derecha (por la coordenada x)
        puntos_filtrados = [(y, x) for x, y in mejor_y_por_x.items()]
        puntos_filtrados.sort(key=lambda punto: punto[1])

        return puntos_filtrados

    def unir_e_interpolar_por_x(self, puntos):
        puntos = np.array(puntos)
        if len(puntos) <= 1:
            return [tuple(p) for p in puntos]

        camino_final = []

        # 1. Encontrar el punto inicial (el más a la izquierda en el eje X)
        indice_inicial = np.argmin(puntos[:, 1])
        punto_actual = puntos[indice_inicial]

        # Agregamos el punto de inicio al camino
        camino_final.append(tuple(punto_actual))
        pendientes = np.delete(puntos, indice_inicial, axis=0)

        while len(pendientes) > 0:
            # 2. Buscar el más cercano en X
            distancias_x = np.abs(pendientes[:, 1] - punto_actual[1])
            min_dist_x = np.min(distancias_x)
            indices_candidatos = np.where(distancias_x == min_dist_x)[0]

            # Desempate en Y por si hay varios en la misma X
            if len(indices_candidatos) > 1:
                candidatos = pendientes[indices_candidatos]
                distancias_y = np.abs(candidatos[:, 0] - punto_actual[0])
                indice_elegido = indices_candidatos[np.argmin(distancias_y)]
            else:
                indice_elegido = indices_candidatos[0]

            siguiente_punto = pendientes[indice_elegido]

            # 3. AQUÍ ESTÁ EL RELLENO: Trazamos la recta entre el actual y el que acabamos de encontrar
            # Usamos tu propia función de interpolación
            segmento = self.interpolar_puntos(tuple(punto_actual), tuple(siguiente_punto))

            # Agregamos los puntos generados por la recta al camino final.
            # (Iniciamos desde [1:] para no volver a meter el 'punto_actual' que ya estaba en la lista)
            for p in segmento[1:]:
                camino_final.append(tuple(p))

            # 4. Actualizamos el punto actual para el siguiente salto y lo borramos de pendientes
            punto_actual = siguiente_punto
            pendientes = np.delete(pendientes, indice_elegido, axis=0)

        # Opcional: Eliminar duplicados continuos que a veces genera la interpolación
        # manteniendo el orden secuencial.
        camino_sin_duplicados = [camino_final[0]]
        for p in camino_final[1:]:
            if p != camino_sin_duplicados[-1]:
                camino_sin_duplicados.append(p)

        return camino_sin_duplicados