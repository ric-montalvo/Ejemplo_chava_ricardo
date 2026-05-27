import os

import cv2
import numpy as np
import traceback
from PIL import Image, ImageOps
from Modelo.Gestor_almacenamiento import Gestor_almacenamiento
from Modelo.Cargador_puntos import Cargador_puntos
from Modelo.Operador_Sobel import Operador_Sobel
from Modelo.Visualizador_operaciones import Visualizador_operaciones
from Modelo.Validador_puntos import Validador_puntos
from Modelo.Seguidor_de_contorno import Seguidor_de_contorno
from Modelo.Filtros_espaciales import Filtros_espaciales
from Modelo.Bordes_ventana import bordes_ventana
from Modelo.Utilidades_npListas import Utilidades_npListas
from Modelo.Morfologia import Morfologia
from Modelo.Bordes_coronarios import Bordes_coronarios
from Modelo.Seguimiento import Seguimiento
from Modelo.Filtrador_bordes_cuello_corona import Filtrador_bordes_cuello_corona
from Modelo.Seguidor_basado_vertices import Seguidor_basado_vertices



#Esta clase esta hecha para hacer que el codigo sea una lectura secuencial e intuitiva
#ejecutara paso a paso como una receta

class Orquestador:
    almacenar = Gestor_almacenamiento()
    cargador = Cargador_puntos()
    sobel = Operador_Sobel()
    visualizador = Visualizador_operaciones()
    validador = Validador_puntos()
    seguidor = Seguidor_de_contorno()
    filtros = Filtros_espaciales()
    brd = bordes_ventana()
    utl = Utilidades_npListas()
    mf = Morfologia()
    cor = Bordes_coronarios()
    seg = Seguimiento()
    ft = Filtrador_bordes_cuello_corona()
    brd_vert = Seguidor_basado_vertices()






    def procesar_pipeline(self, path):
        _, ext = os.path.splitext(path)
        if ext.lower() not in ['.jpg', '.jpeg', '.bmp']:
            raise ValueError("Restricción de entrada: El archivo debe ser un JPG o BMP.")

        try:
            #Lectura
            img_original = Image.open(path)

            #Preparacion
            img_gris = ImageOps.grayscale(img_original)
            np_original = np.array(img_gris)
            np_grises = np.array(img_gris)

            #Imagenes utiles
            np_grises = self.filtros.filtro_mediana(np_grises, 2)
            np_sobel = self.sobel.magnitud_sobel(np_grises)
            np_orientacion = self.sobel.orientacion_sobel(np_grises)

# ==============================================================================================
# ============================PUNTOS ORIGINALES=================================================

            maxilar, mandibular = self.cargador.obtener_puntos_por_arcada()
            puntos_originales = maxilar + mandibular
            np_puntos_originales = self.cargador.obtener_puntos_visualizables(puntos_originales, np_grises, 0)
            np_iniciales = self.visualizador.listas_sobre_imagen_color(np_grises, np_puntos_originales, "verde")
            img_iniciales = Image.fromarray(np_iniciales)

            img_sobel = Image.fromarray(self.visualizador.mapear_a_visualizable(np.abs(self.sobel.gx_sobel(np_grises))))

# ==============================================================================================
# ==============================================================================================

            largo_mandibulares = self.cargador.obtener_largo_raices(mandibular, 105)
            largo_maxilares = self.cargador.obtener_largo_raices(maxilar, 105)


#==============================================================================================
#============================ALGORITMO EXPERIMENTAL=============================================
            lista_brds, pts = self.brd.obtener_bordes(np_sobel**1.3, np_orientacion, puntos_originales, (70, 20))
            np_brds_estadisticos = self.visualizador.listas_sobre_imagen(np_grises, lista_brds)
            img_brds_estadisticos = Image.fromarray(np_brds_estadisticos)
            lista_brdss = self.mf.cierre_puntos(lista_brds, (1, 1))
            max_exp, man_exp = self.cargador.separar_maxilar_mandibular(pts)

            lista_experimental = self.seguidor.aplicar_seguimiento_vertical_exp(max_exp, man_exp, largo_maxilares,largo_mandibulares, np_grises, lista_brdss)

            np_experimental = self.visualizador.listas_sobre_imagen(np_grises, lista_experimental)

            pts = self.cargador.obtener_puntos_visualizables(pts, np_grises)
            np_experimental = self.visualizador.listas_sobre_imagen_color(np_experimental, pts, "verde")

            img_exp = Image.fromarray(np_experimental)
            #self.almacenar.guardar_resultado(path, np_experimental, "tst")

#==============================================================================================
#==============================================================================================




#==============================================================================================
#===============================BORDES CORONARIOS==============================================

            grad = self.sobel.magnitud_sobel(np_grises)
            bordes, bordes_maxilar, bordes_mandibular = self.cor.extraer_contornos_dentales(grad, maxilar, mandibular)

            bordes_coronarios = bordes_maxilar + bordes_mandibular



            bordes = self.ft.filtrar_bordes_verticales_longitud_conexion(bordes, bordes_coronarios, -1.5)
            brds_recortados = self.ft.cortar_bordes_verticales(bordes, bordes_maxilar, bordes_mandibular)
            vertices = self.ft.obtener_puntos_vertice(brds_recortados)
            vert_max, vert_man = self.ft.clasificar_vertices_por_hueso(vertices, bordes_maxilar, bordes_mandibular)



            np_bordes_coronarios = self.visualizador.listas_sobre_imagen(np_grises, bordes)
            np_general = self.visualizador.lista_sobre_imagen(np_bordes_coronarios, bordes_coronarios)
            np_bordes_filtrados = self.visualizador.lista_sobre_imagen(np_grises, bordes_coronarios)
            np_bordes_recortados = self.visualizador.listas_sobre_imagen(np_grises, brds_recortados)
            np_vert_max = self.visualizador.listas_sobre_imagen(np_grises, vert_man)




            np_all = self.visualizador.listas_sobre_imagen(np_general, lista_experimental)






            img_cor = Image.fromarray(np_bordes_coronarios)
            img_filtrado = Image.fromarray(np_bordes_filtrados)
            img_grl = Image.fromarray(np_general)
            img_recortados = Image.fromarray(np_bordes_recortados)
            img_vert_max = Image.fromarray(np_vert_max)

#==============================================================================================
            lista = self.utl.aplanar_lista_de_tuplas(bordes_coronarios) + self.utl.aplanar_lista_de_tuplas(lista_experimental)
            np_general = self.visualizador.lista_sobre_imagen(np_grises, lista)
            img_general = Image.fromarray(np_general)
#==============================================================================================








            #Guardado

            #self.almacenar.guardar_resultado(path, np_sobel, "Bordes de sobel")
            self.almacenar.guardar_resultado(path, np_iniciales, "Puntos iniciales")
            """self.almacenar.guardar_resultado(path, np_experimental, "Seguimiento heuristico hacia raiz")
            self.almacenar.guardar_resultado(path, np_brds_estadisticos, "Bordes en ROI estadistico")
            self.almacenar.guardar_resultado(path, np_bordes_coronarios, "Bordes cuello dental")
            self.almacenar.guardar_resultado(path, np_bordes_filtrados, "Bordes Coronarios")
            self.almacenar.guardar_resultado(path, np_general, "Cuello y Corona")
            self.almacenar.guardar_resultado(path, np_all, "Cuello corona y raiz")
            """


            bordes_cuello = self.seg.seguimiento_hacia_oclusion(np_grises, maxilar, mandibular, self.utl.aplanar_lista_de_tuplas(lista_brds) ,self.utl.aplanar_lista_de_tuplas(bordes), bordes_coronarios)
            brd_generales = bordes_coronarios + brds_recortados


            np_bordes_cuello = self.visualizador.listas_sobre_imagen(np_grises, bordes_cuello)
            np_generales = self.visualizador.listas_sobre_imagen(np_grises, brd_generales)


            img_brds_cuello = Image.fromarray(np_bordes_cuello)
            img_generales = Image.fromarray(np_generales)

            brd_ver_max, brd_ver_man = self.brd_vert.orquestador(np_grises, maxilar, mandibular)
            np_brd_vert = self.visualizador.listas_sobre_imagen(np_grises, brd_ver_max)
            np_brd_vert = self.visualizador.listas_sobre_imagen(np_brd_vert, brd_ver_man)
            img_brd_ver = Image.fromarray(np_brd_vert)

            # ==============================================================================================
            cuello_corona = self.utl.aplanar_lista_de_tuplas(brd_generales)
            vertices_man_planos = self.utl.aplanar_lista_de_tuplas(brd_ver_man)
            vertices_max_planos = self.utl.aplanar_lista_de_tuplas(brd_ver_max)

            lista_final = cuello_corona + vertices_man_planos + vertices_max_planos
            np_img_final = self.visualizador.lista_sobre_imagen(np_original, lista_final)
            img_final = Image.fromarray(np_img_final)
            # ==============================================================================================

            #Guardado final en BMP
            ruta_base = self.almacenar.obtener_ruta_guardar(path, "_Renderizada")
            ruta_bmp = os.path.splitext(ruta_base)[0] + ".bmp"
            cv2.imwrite(ruta_bmp, np_img_final)
            img_sobel_ori = Image.fromarray(self.visualizador.mapear_a_visualizable(np_sobel))

            return [
                (img_original, "0. Original sin procesar"),
                (img_iniciales, "1. Puntos iniciales"),
                (img_final, "FINAL")

            ]
        except Exception as e:
            traceback.print_exc()
            raise RuntimeError(f"No se pudo procesar la imagen: {e}")
