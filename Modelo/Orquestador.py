import os
import numpy as np
import traceback
from PIL import Image, ImageOps
from Modelo.Gestor_almacenamiento import Gestor_almacenamiento
from Modelo.Cargador_puntos import Cargador_puntos
from Modelo.Visualizador_operaciones import Visualizador_operaciones
from Modelo.Seguidor_de_contorno import Seguidor_de_contorno
from Modelo.Filtros_espaciales import Filtros_espaciales
from Modelo.Bordes_ventana import bordes_ventana
from Modelo.Utilidades_npListas import Utilidades_npListas
from Modelo.Bordes_coronarios import Bordes_coronarios
from Modelo.Seguimiento import Seguimiento
from Modelo.Filtrador_bordes_cuello_corona import Filtrador_bordes_cuello_corona
from Modelo.Seguidor_basado_vertices import Seguidor_basado_vertices
from Modelo.Operaciones_anchura import Operaciones_anchura
from Modelo.Metricas import Metricas


class Orquestador:
    almacenar = Gestor_almacenamiento()
    cargador = Cargador_puntos()
    visualizador = Visualizador_operaciones()
    seguidor = Seguidor_de_contorno()
    filtros = Filtros_espaciales()
    brd = bordes_ventana()
    utl = Utilidades_npListas()
    cor = Bordes_coronarios()
    seg = Seguimiento()
    ft = Filtrador_bordes_cuello_corona()
    brd_vert = Seguidor_basado_vertices()
    operaciones = Operaciones_anchura()
    metricas = Metricas()

    # * NUEVO: atributo para almacenar las métricas calculadas
    def __init__(self):
        self.metricas_resultado = None

    def procesar_pipeline(self, path, nombre_archivo=None):
        """
        nombre_archivo: nombre base del archivo de imagen (sin extensión)
                        que se usará para buscar puntos en el CSV.
        """
        _, ext = os.path.splitext(path)
        if ext.lower() not in ['.jpg', '.jpeg', '.bmp']:
            raise ValueError("Restricción de entrada: El archivo debe ser JPG o BMP.")

        # Configurar el nombre en el cargador (si existe el método)
        if hasattr(self.cargador, 'set_nombre_archivo'):
            self.cargador.set_nombre_archivo(nombre_archivo)

        try:
            # Lectura y preparación
            img_original = Image.open(path)
            img_gris = ImageOps.grayscale(img_original)
            np_original = np.array(img_gris)
            np_grises = np.array(img_gris)

            # Imágenes útiles
            np_show = self.filtros.filtro_mediana(np_grises, 3)
            np_grises = self.filtros.filtro_mediana(np_grises, 2)

            # Puntos originales desde CSV (o fallback)
            maxilar, mandibular = self.cargador.obtener_puntos_por_arcada()
            puntos_originales = maxilar + mandibular
            np_puntos_originales = self.cargador.obtener_puntos_visualizables(puntos_originales, np_grises, 2)
            np_iniciales = self.visualizador.listas_sobre_imagen_color(np_grises, np_puntos_originales, "verde")
            img_iniciales = Image.fromarray(np_iniciales)

            # Bordes coronarios
            bordes, bordes_maxilar, bordes_mandibular, np_sob_cor = self.cor.extraer_contornos_dentales(np_grises, maxilar, mandibular)
            bordes_coronarios = bordes_maxilar + bordes_mandibular

            bordes = self.ft.filtrar_bordes_verticales_longitud_conexion(bordes, bordes_coronarios, -1.5)

            # Seguimiento hacia oclusión
            maxilar_cuello, mandibular_cuello = self.seg.seguimiento_hacia_oclusion(
                np_grises, maxilar, mandibular,
                bordes,  # bordes_cuello (sin aplanar)
                bordes_coronarios  # bordes_corona
            )

            # Vértices y segmentación
            brd_ver_max, brd_ver_man = self.brd_vert.orquestador(np_grises, maxilar, mandibular)

            # * CAMBIO: Obtener los dientes segmentados (reutilizamos la misma llamada)
            cone_max, cone_man = self.operaciones.orquestador(
                maxilar, mandibular, brd_ver_max, brd_ver_man,
                maxilar_cuello, mandibular_cuello,
                bordes_maxilar, bordes_mandibular
            )
            dientes_max, dientes_man = cone_max, cone_man   # son la misma salida

            # * NUEVO: Calcular anchuras, centros y luego métricas
            anchuras_max = self.operaciones.obtener_anchuras(maxilar)
            anchuras_man = self.operaciones.obtener_anchuras(mandibular)
            centros_max = self.operaciones.centros_anchuras(anchuras_max)
            centros_man = self.operaciones.centros_anchuras(anchuras_man)

            w = np_grises.shape[1]   # ancho de la imagen

            # * NUEVO: Obtener métricas reales usando la clase Metricas
            self.metricas_resultado = self.metricas.Orquestador(
                dientes_max, dientes_man, centros_max, centros_man,
                bordes_maxilar, bordes_mandibular, maxilar_cuello, mandibular_cuello,
                anchuras_max, anchuras_man, brd_ver_max, brd_ver_man,
                maxilar, mandibular, w
            )

            # Generar imágenes para el visor
            np_segmentados = self.visualizador.listas_sobre_imagen(np_show, cone_max)
            np_segmentados = self.visualizador.listas_sobre_imagen(np_segmentados, cone_man)
            img_segmentados = Image.fromarray(np_segmentados)

            # Guardado de imágenes (opcional)
            self.almacenar.guardar_resultado(path, np_show, "_original")
            self.almacenar.guardar_resultado(path, np_iniciales, "Puntos iniciales")
            self.almacenar.guardar_resultado(path, np_segmentados, "_Renderizada")

            # Retorno para el visor
            return [
                (Image.fromarray(np_show), "Imagen_inicial"),
                (img_iniciales, "1. Puntos iniciales"),
                (img_segmentados, "FINAL")
            ]

        except Exception as e:
            traceback.print_exc()
            raise RuntimeError(f"No se pudo procesar la imagen: {e}")

        finally:
            # Limpiar el nombre del cargador si existe
            if hasattr(self.cargador, 'set_nombre_archivo'):
                self.cargador.set_nombre_archivo(None)

    # * NUEVO MÉTODO: obtener las métricas reales después del procesamiento
    def obtener_metricas_reales(self):
        """Devuelve la lista de métricas calculadas en la última llamada a procesar_pipeline"""
        return self.metricas_resultado