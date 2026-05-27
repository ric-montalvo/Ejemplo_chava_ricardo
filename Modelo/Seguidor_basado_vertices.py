import numpy as np
from Modelo.Filtrador_bordes_cuello_corona import Filtrador_bordes_cuello_corona
from Modelo.Bordes_coronarios import Bordes_coronarios
from Modelo.Bordes_ventana import bordes_ventana
from Modelo.Operador_Sobel import Operador_Sobel

class Seguidor_basado_vertices:

    filtrador = Filtrador_bordes_cuello_corona()
    brd_corona = Bordes_coronarios()
    brd_ventana = bordes_ventana()
    sobel = Operador_Sobel()


    def orquestador(self, imagen, maxilar, mandibular):
        vert_max, vert_man = self.obtener_vertices(imagen, maxilar, mandibular)
        brd_ver_max, brd_ver_man = self.aplicar_seguimiento_magnitud_gradiente(imagen, vert_max, vert_man)


        return brd_ver_max, brd_ver_man


    def obtener_vertices(self, imagen, maxilar, mandibular):
        grad = self.sobel.magnitud_sobel(imagen)
        bordes_cuello, bordes_maxilar, bordes_mandibular = self.brd_corona.extraer_contornos_dentales(grad, maxilar,
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
        sobel = np.abs(self.sobel.gx_sobel(imagen)) ** 10
        for punto in vertices_maxilares:
            borde = self.seguimiento_magnitud_gradiente(sobel, punto, 1, True)
            bordes_vertices_max.append(borde)
        for punto in vertices_mandibulares:
            borde = self.seguimiento_magnitud_gradiente(sobel, punto, 1, False)
            bordes_vertices_man.append(borde)
        return bordes_vertices_max, bordes_vertices_man


    def seguimiento_magnitud_gradiente(self, sobel_gy, punto, radio=1, es_maxilar=True):
        """Vertices es lista de tuplas (y, x). Retorna lista de tuplas."""
        h, w = sobel_gy.shape
        puntos_visitados = set()
        punto = tuple(punto)
        max_len = 2                 # máximo de puntos de visión a futuro
        tolerancia = 0.05          # qué tan pequeño puede ser la magnitud respecto al actual
        dy = -1 if es_maxilar else 1

        while True:
            puntos_visitados.add(punto)
            y, x = punto
            magnitud_actual = sobel_gy[punto]
            magnitud_minima = magnitud_actual * tolerancia
            y_siguiente = y + dy
            if y_siguiente < 0 or y_siguiente >= h:
                break
            x_ini = max(0, x - radio)
            x_fin = min(w, x + radio + 1)

            vecinos = [(y_siguiente, nx) for nx in range(x_ini, x_fin)]
            if not vecinos:
                break
            valores_y_coords = [(sobel_gy[vy, vx], (vy, vx)) for vy, vx in vecinos]
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

                vecinos_interpolar = sobel_gy[y_ini_ventana:y_fin_ventana, x_ini:x_fin]

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





