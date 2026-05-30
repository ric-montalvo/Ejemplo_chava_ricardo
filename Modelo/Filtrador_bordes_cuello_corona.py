import numpy as np
class Filtrador_bordes_cuello_corona:


    def filtrar_bordes_verticales_longitud_conexion(self, lista_bordes, bordes_corona, umbral_sigmas = -1.5):
        """
        Elimina los bordes verticales con longitud pequenia y que no esta conectado
        a un borde coronario.
        lista_bordes  (lista de listas de tuplas (y, x))>
                       Cada lista representa a un borde tentativo en el cuello dental.
        bordes_corona (lista de tuplas (y, x))>
                        Representa a los bordes coronarios detectados (bordes horizontales en el maxilar
                        y mandibular), pueden o no estar conectados todos los puntos entre si
        umbral_sigmas (signed int)>
                        Parametro para eliminar de forma estadistica los bordes verticales en base a su longitud.
        """
        if not lista_bordes:
            return []

        if bordes_corona is None:
            bordes_guia = []

        set_guia = set(bordes_corona)
        tamanos = np.array([len(borde) for borde in lista_bordes])
        media = np.mean(tamanos)
        sigma = np.std(tamanos)
        limite_minimo = media + (umbral_sigmas * sigma)
        bordes_filtrados = []

        for borde, tamano in zip(lista_bordes, tamanos):
            tiene_punto_guia = any(tuple(punto) in set_guia for punto in borde)
            if tamano >= limite_minimo or tiene_punto_guia:
                bordes_filtrados.append(borde)
        return bordes_filtrados







    def cortar_bordes_verticales(self, lista_bordes_verticales, borde_maxilar, borde_mandibular):
        """
        Busca reducir el tamanio de los bordes verticales al momento de tocar uno de los
        bordes coronarios, para evitar doble borde vertical.
        lista_bordes  (lista de listas de tuplas (y, x))>
                       Cada lista representa a un borde tentativo en el cuello dental.
        bordes_maxilares (lista de tuplas (y, x))>
                        Representa a los bordes coronarios detectados en el maxilar,
                        pueden o no estar conectados todos los puntos entre si.
        bordes_mandibulares (lista de tuplas (y, x))>
                        Representa a los bordes coronarios detectados en el mandibular,
                        pueden o no estar conectados todos los puntos entre si
        """
        lista_vertices = [self.obtener_vertices_topologicos(borde) for borde in lista_bordes_verticales]
        set_maxilar = set([tuple(p) for p in borde_maxilar])
        set_mandibular = set([tuple(p) for p in borde_mandibular])
        muros_horizontales = set_maxilar.union(set_mandibular)
        dict_maxilar = {}
        for y, x in borde_maxilar:
            if x not in dict_maxilar or y < dict_maxilar[x]:
                dict_maxilar[x] = y

        dict_mandibular = {}
        for y, x in borde_mandibular:
            if x not in dict_mandibular or y > dict_mandibular[x]:
                dict_mandibular[x] = y

        def obtener_y_limite(diccionario, x_buscada, y_default):
            if x_buscada in diccionario:
                return diccionario[x_buscada]
            if not diccionario:
                return y_default
            x_cercana = min(diccionario.keys(), key=lambda k: abs(k - x_buscada))
            return diccionario[x_cercana]

        bordes_recortados = []
        direcciones_8 = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

        for i in range(len(lista_bordes_verticales)):
            borde_original_set = set([tuple(p) for p in lista_bordes_verticales[i]])
            vertices = [tuple(p) for p in lista_vertices[i]]

            semillas_validas = []

            for v in vertices:
                y, x = v
                y_lim_maxilar = obtener_y_limite(dict_maxilar, x, y)
                y_lim_mandibular = obtener_y_limite(dict_mandibular, x, y)

                if y < y_lim_mandibular:
                    if y < y_lim_maxilar:
                        semillas_validas.append(v)

                elif y > y_lim_maxilar:
                    if y > y_lim_mandibular:
                        semillas_validas.append(v)

            borde_limpio = []
            visitados = set()

            for semilla in semillas_validas:
                if semilla in visitados:
                    continue

                pila = [semilla]

                while pila:
                    actual = pila.pop()

                    if actual in visitados:
                        continue

                    visitados.add(actual)
                    borde_limpio.append(actual)
                    y, x = actual

                    if actual in muros_horizontales:
                        continue

                    for dy, dx in direcciones_8:
                        vecino = (y + dy, x + dx)
                        if vecino in borde_original_set and vecino not in visitados:
                            pila.append(vecino)

            bordes_recortados.append(borde_limpio)

        return bordes_recortados



    def obtener_puntos_vertice(self, lista_bordes):
        """Devuelve una lista de listas de los vertices en los bordes verticales"""
        vertices = []
        for borde in lista_bordes:
            if len(borde) > 0:
                ptos = self.obtener_vertices_topologicos(borde)
                vertices.append(ptos)
        return vertices

    def obtener_vertices_topologicos(self, borde):
        borde_tuplas = [tuple(p) for p in borde]
        borde_set = set(borde_tuplas)
        p_min = min(borde_tuplas, key=lambda p: p[0])
        p_max = max(borde_tuplas, key=lambda p: p[0])
        vertices_salida = {p_min, p_max}

        direcciones = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]
        for y, x in borde_set:
            vecinos_conectados = 0
            for dy, dx in direcciones:
                if (y + dy, x + dx) in borde_set:
                    vecinos_conectados += 1
            if vecinos_conectados == 1:
                vertices_salida.add((y, x))
        return list(vertices_salida)

    def clasificar_vertices_por_hueso(self, lista_de_listas_vertices, borde_maxilar, borde_mandibular):
        # 1. Sets para búsquedas instantáneas O(1)
        set_maxilar = set([tuple(p) for p in borde_maxilar])
        set_mandibular = set([tuple(p) for p in borde_mandibular])

        # 2. Diccionario para el mandibular (búsqueda rápida de Y dada una X)
        dict_mandibular = {}
        for y, x in borde_mandibular:
            # Tomamos el píxel más alto del mandibular para que la barrera sea estricta
            if x not in dict_mandibular or y < dict_mandibular[x]:
                dict_mandibular[x] = y

        # Función auxiliar para vacíos en la línea horizontal
        def obtener_y_limite(diccionario, x_buscada, y_default):
            if x_buscada in diccionario:
                return diccionario[x_buscada]
            if not diccionario:
                return y_default
            x_cercana = min(diccionario.keys(), key=lambda k: abs(k - x_buscada))
            return diccionario[x_cercana]

        # Vecindad: El punto exacto (0,0) y sus 8 vecinos alrededor
        vecindad = [
            (0, 0), (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]

        vertices_maxilar = []
        vertices_mandibular = []

        # Procesamos la lista de listas
        for sublista in lista_de_listas_vertices:
            for v in sublista:
                y, x = tuple(v)

                conectado_maxilar = False
                conectado_mandibular = False

                # --- EVALUACIÓN DE CONEXIÓN ---
                for dy, dx in vecindad:
                    vecino = (y + dy, x + dx)
                    if vecino in set_maxilar:
                        conectado_maxilar = True
                    if vecino in set_mandibular:
                        conectado_mandibular = True

                # --- LÓGICA DE CLASIFICACIÓN ---
                if conectado_maxilar:
                    vertices_maxilar.append((y, x))
                elif conectado_mandibular:
                    vertices_mandibular.append((y, x))
                else:
                    # Sin conexión directa, evaluamos espacialmente
                    y_lim_man = obtener_y_limite(dict_mandibular, x, y)

                    # 'y' menor significa que está más ARRIBA en la imagen (Maxilar)
                    if y < y_lim_man:
                        vertices_maxilar.append((y, x))
                    else:
                        vertices_mandibular.append((y, x))

        # Devuelve dos listas planas con todos los vértices separados
        return vertices_maxilar, vertices_mandibular