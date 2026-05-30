import numpy as np
from Modelo.Metodos_numericos import Metodos_numericos
from Modelo.Operador_Sobel import Operador_Sobel
from Modelo.Visualizador_operaciones import Visualizador_operaciones

class Ajustador_inercia:
    metodos = Metodos_numericos()
    sobel = Operador_Sobel()
    visualizador = Visualizador_operaciones()



    def orquestador(self, cuellos, vertices_maxilares, vertices_mandibulares, maxilares, mandibulares, imagen):
        gx_sobel = np.abs(self.sobel.gx_sobel(imagen)) ** 1.3


        #inercia inicial
        maxilares_unidos = self.unificar_bordes(cuellos, vertices_maxilares, maxilares, True, 30, 15)
        mandibulares_unidos = self.unificar_bordes(cuellos, vertices_mandibulares, mandibulares, False, 30, 15)

        maxilares_limp = self.procesar_multiples_bordes(maxilares_unidos, True, 30, 10)
        mandibulares_limp = self.procesar_multiples_bordes(mandibulares_unidos, False, 30, 10)


        #primer ajuste
        maxilares_extrapolados = self.aplicar_extrapolacion(maxilares_limp, True, 30)
        mandibulares_extrapolados = self.aplicar_extrapolacion(mandibulares_limp, False, 30)

        maxilares_ajustados = self.aplicar_ajuste(maxilares_extrapolados, gx_sobel, 2)
        mandibulares_ajustados = self.aplicar_ajuste(mandibulares_extrapolados, gx_sobel, 2)

        maxilares_conectados = self.aplicar_conexion(maxilares_ajustados, True)
        mandibulares_conectados = self.aplicar_conexion(mandibulares_ajustados, False)


        max_ret = maxilares_unidos + maxilares_conectados
        man_ret = mandibulares_unidos + mandibulares_conectados



        return max_ret, man_ret

    def unificar_bordes(self, brds_cuello, brds_vertices, puntos_iniciales, es_maxilar, n = 15, n_v = 10):
        bordes_unidos = []

        for punto_inicial in puntos_iniciales:
            cuello_procesado = []
            vertice_procesado = []
            for sublista_c in brds_cuello:
                if punto_inicial in sublista_c:
                    sublista_c_ordenada = sorted(sublista_c, key=lambda punto: punto[0])
                    if es_maxilar:
                        cuello_procesado = sublista_c_ordenada[:n]
                    else:
                        cuello_procesado = sublista_c_ordenada[-n:]

                    break
            for sublista_v in brds_vertices:
                if punto_inicial in sublista_v:
                    sublista_v_ordenada = sorted(sublista_v, key=lambda punto: punto[0])
                    if not es_maxilar:
                        vertice_procesado = sublista_v_ordenada[:n_v]
                    else:
                        vertice_procesado = sublista_v_ordenada[-n_v:]
                    break
            lista_combinada = cuello_procesado + vertice_procesado
            bordes_unidos.append(lista_combinada)

        return bordes_unidos

    def aplicar_extrapolacion(self, bordes, es_Maxilar, pasos):
        bordes_extrapolados = []
        if es_Maxilar:
            dy = -1
        else:
            dy = 1

        for borde in bordes:
            brd_extrapolado = self.metodos.extrapolar_borde(borde, pasos, dy)
            bordes_extrapolados.append(brd_extrapolado)

        return bordes_extrapolados


    def aplicar_ajuste(self, bordes, sobel, radio = 2):
        bordes_ajustados = []
        for borde in bordes:
            ajustado = self.ajustar_borde_al_maximo(borde, sobel, radio)
            bordes_ajustados.append(ajustado)


        return bordes_ajustados

    def ajustar_borde_al_maximo(self, puntos, imagen_sobel, radio_n):
        """
        Desplaza cada punto de un borde hacia el píxel de mayor intensidad
        en la imagen Sobel, buscando a lo largo de su vector normal.

        :param puntos: Lista de coordenadas [(y1, x1), (y2, x2), ...]
        :param imagen_sobel: Matriz 2D de NumPy con las intensidades de los bordes.
        :param radio_n: Radio de búsqueda hacia ambos lados de la normal.
        :return: Lista de nuevas coordenadas [(y1', x1'), (y2', x2'), ...] ajustadas al máximo.
        """

        if len(puntos) < 2:
            # Si hay 0 o 1 punto, no hay línea, por lo tanto no hay vector normal.
            # Regresamos los puntos tal cual están para que el algoritmo pueda continuar.
            return puntos
        p = np.array(puntos, dtype=float)
        alto, ancho = imagen_sobel.shape
        N_puntos = len(p)

        # 1. Calcular el gradiente y el vector normal
        grad_y = np.gradient(p[:, 0])
        grad_x = np.gradient(p[:, 1])

        normal_y = grad_x
        normal_x = -grad_y

        magnitud = np.sqrt(normal_y ** 2 + normal_x ** 2)
        magnitud[magnitud == 0] = 1.0

        norm_y = normal_y / magnitud
        norm_x = normal_x / magnitud

        # Matriz de normales (N, 2)
        normales = np.column_stack((norm_y, norm_x))

        # 2. Crear el espacio de búsqueda vectorizado
        # Rango de valores desde -radio_n hasta +radio_n
        n_vals = np.arange(-radio_n, radio_n + 1)

        # Usamos broadcasting para generar todas las coordenadas de búsqueda de golpe.
        # Resultado: Una matriz de forma (N_puntos, cantidad_de_pasos, 2)
        desplazamientos = p[:, None, :] + n_vals[None, :, None] * normales[:, None, :]

        # Redondear a enteros para poder usarlos como índices en la imagen
        coords = np.round(desplazamientos).astype(int)

        # 3. Restringir los límites para no salirnos de la imagen (Clipping)
        y_coords = np.clip(coords[:, :, 0], 0, alto - 1)
        x_coords = np.clip(coords[:, :, 1], 0, ancho - 1)

        # 4. Extraer las intensidades de la imagen Sobel
        # intensidades tendrá forma (N_puntos, cantidad_de_pasos)
        intensidades = imagen_sobel[y_coords, x_coords]

        # 5. Encontrar el índice del valor máximo a lo largo de cada línea de búsqueda
        idx_maximos = np.argmax(intensidades, axis=1)

        # 6. Seleccionar las coordenadas ganadoras usando los índices encontrados
        mejores_y = y_coords[np.arange(N_puntos), idx_maximos]
        mejores_x = x_coords[np.arange(N_puntos), idx_maximos]

        # Ensamblar los nuevos puntos
        nuevos_puntos = np.column_stack((mejores_y, mejores_x))

        return nuevos_puntos.tolist()

    def rastrear_y_conectar_borde(self, puntos, es_Maxilar=True):
        """
        Rastrea un borde fragmentado moviéndose estrictamente en una dirección Y,
        saltando brechas hacia el punto con menor variación en X.

        :param puntos: Lista de coordenadas [(y1, x1), (y2, x2), ...]
        :param ir_hacia_arriba: Booleano. Si True, inicia en Y máximo y dy = -1.
                                Si False, inicia en Y mínimo y dy = 1.
        :return: Lista de coordenadas del borde continuo y conectado.
        """
        # Trabajamos con una copia de la lista para poder ir descartando los puntos visitados
        puntos_pendientes = list(puntos)
        if not puntos_pendientes:
            return []

        # 1. Definir el punto de partida y la dirección (dy)
        if es_Maxilar:
            dy_esperado = -1
            # Tomamos el punto con el Y máximo (el que está más abajo en la imagen)
            punto_actual = max(puntos_pendientes, key=lambda p: p[0])
        else:
            dy_esperado = 1
            # Tomamos el punto con el Y mínimo (el que está más arriba en la imagen)
            punto_actual = min(puntos_pendientes, key=lambda p: p[0])

        puntos_pendientes.remove(punto_actual)
        camino_final = [punto_actual]

        # 2. Búsqueda y conexión
        while puntos_pendientes:
            y_actual, x_actual = punto_actual

            # Filtramos SOLO los puntos que están "adelante" en nuestra dirección Y
            candidatos_validos = [
                p for p in puntos_pendientes
                if (p[0] - y_actual) * dy_esperado > 0
            ]

            # Si ya no hay puntos en esa dirección, terminamos el recorrido
            if not candidatos_validos:
                break

                # 3. Encontrar el punto más cercano en X
            # Si hay empate en X (misma columna), el criterio secundario es la distancia en Y
            mejor_candidato = min(
                candidatos_validos,
                key=lambda p: (abs(p[1] - x_actual), abs(p[0] - y_actual))
            )

            # 4. Conectar la brecha usando tu función Bresenham
            # Asumimos que Bresenham devuelve [(y_actual, x_actual), ..., (y_nuevo, x_nuevo)]
            puntos_conexion = self.metodos.algoritmo_Bresenham(punto_actual, mejor_candidato)

            if puntos_conexion:
                # Omitimos el primer punto de la conexión para no duplicar el 'punto_actual' en la lista final
                if puntos_conexion[0] == punto_actual:
                    camino_final.extend(puntos_conexion[1:])
                else:
                    camino_final.extend(puntos_conexion)
            else:
                # Por seguridad, si Bresenham falla, unimos el punto directamente
                camino_final.append(mejor_candidato)

            # 5. Actualizar el estado para el siguiente ciclo
            punto_actual = mejor_candidato
            puntos_pendientes.remove(mejor_candidato)

        return camino_final

    def aplicar_conexion(self, bordes, es_maxilar):
        bordes_conectados = []
        for borde in bordes:
            borde_conectado = self.rastrear_y_conectar_borde(borde, es_maxilar)
            bordes_conectados.append(borde_conectado)

        return bordes_conectados




    def obtener_puntos_representativos_vertical(self, borde, es_maxilar, n):
        borde = sorted(borde, key=lambda punto: punto[0])
        if es_maxilar:
            puntos = borde[:n]
        else:
            puntos = borde[-n:]
        return puntos


    def aplicar_algoritmo(self, bordes, sobel, es_maxilar, n, r = 2):
        h, w = sobel.shape
        bordes_all = []
        if es_maxilar:
            dy = -1
        else:
            dy = 1



        for borde in bordes:
            borde_actual = list(borde)
            while True:
                k_ptos = min(n, len(borde_actual))
                bordes_representativo = self.obtener_puntos_representativos_vertical(borde_actual, es_maxilar, k_ptos)
                borde_extrapolado = self.metodos.extrapolar_borde(bordes_representativo, k_ptos//2, dy)
                ban = any(y < 0 or x < 0 or y >= h or x >= w for y, x in borde_extrapolado)
                if ban:
                    break
                borde_ajustado = self.ajustar_borde_al_maximo(borde_extrapolado, sobel, r)
                #aquipuedo agregar el break de si el maximo es menor a n
                intensidades = [sobel[y, x] for y, x in borde_ajustado]
                intensidad_maxima = max(intensidades) if intensidades else 0
                if intensidad_maxima < 5:
                    break

                # Si la máxima intensidad encontrada es muy baja (ej. un umbral arbitrario o relativo)
                # significa que ya no estamos siguiendo un borde real, solo ruido.
                # (Sustituye '10' por el valor umbral que haga sentido para tus imágenes)

                # -----------------------------------------------

                # 5. Rastreo y conexión
                borde_conectado = self.rastrear_y_conectar_borde(borde_ajustado, es_maxilar)

                # Seguridad extra: si por alguna razón no regresó puntos, rompemos el ciclo
                #if not borde_conectado:
                #    break

                # 6. Agregamos los nuevos puntos y repetimos
                borde_actual.extend(borde_extrapolado)

            bordes_all.append(borde_actual)


        return bordes_all

    def extraer_primer_segmento(self, puntos, es_Maxilar=False, umbral_grados=35.0, ventana=10):
        P = np.array(puntos)
        if len(P) <= ventana * 2:
            return P

        # 1. CONSERVAR EL ORDEN TOPOLÓGICO (Reemplazo del argsort)
        # Validamos que el trazo empiece en la corona y vaya hacia la raíz
        Y_inicio = P[0, 0]
        Y_fin = P[-1, 0]

        if es_Maxilar:
            # Maxilar (dientes arriba): la corona tiene mayor Y (más abajo en la imagen)
            if Y_inicio < Y_fin:
                P = P[::-1]
        else:
            # Mandíbula (dientes abajo): la corona tiene menor Y (más arriba en la imagen)
            if Y_inicio > Y_fin:
                P = P[::-1]

        n_puntos = len(P)
        n_ventanas = n_puntos - ventana + 1
        angulos = np.zeros(n_ventanas)

        t = np.arange(ventana)
        t_mean = t.mean()
        t_det = np.sum((t - t_mean) ** 2)

        Y_all = P[:, 0]
        X_all = P[:, 1]

        for i in range(n_ventanas):
            Y_win = Y_all[i: i + ventana]
            X_win = X_all[i: i + ventana]

            m_Y = np.sum((t - t_mean) * (Y_win - Y_win.mean())) / t_det
            m_X = np.sum((t - t_mean) * (X_win - X_win.mean())) / t_det

            angulos[i] = np.arctan2(m_Y, m_X)

        if len(angulos) <= ventana:
            return P

        # 2. COMPARACIÓN GLOBAL VS BASE
        # Tomamos el promedio de las primeras 3 ventanas como la trayectoria "real"
        angulo_base = np.mean(angulos[:3])

        # Comparamos el resto de las ventanas contra la trayectoria inicial
        diferencias = angulos[ventana:] - angulo_base
        diferencias_norm = np.arctan2(np.sin(diferencias), np.cos(diferencias))

        umbral_rad = np.radians(umbral_grados)
        quiebres = np.where(np.abs(diferencias_norm) > umbral_rad)[0]

        if len(quiebres) > 0:
            primer_quiebre = quiebres[0]
            # Cortamos justo antes de la ventana que superó el umbral
            return P[:primer_quiebre + ventana]

        return P

    def procesar_multiples_bordes(self, lista_de_listas, es_Maxilar=True, umbral_grados=45.0, ventana=10):

        bordes_filtrados = [
            self.extraer_primer_segmento(bordes, es_Maxilar, umbral_grados, ventana)
            for bordes in lista_de_listas
        ]

        return bordes_filtrados