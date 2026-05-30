# Modelo/Productor_estadisticas.py
import random

class ProductorEstadisticas:
    """
    Genera métricas dentales para 32 dientes (numeración 1 a 32).
    Cada métrica es una tupla:
    (id, grado_inclinacion, proporcion_corona, longitud_raiz, tamaño_diastemas, (y, x))
    Si un diente no es detectado, sus valores son 0 y (0,0).
    """

    def generar_metricas(self, detecciones=None):
        """
        Parámetro:
            detecciones: lista de tuplas con los dientes detectados, cada tupla con el formato
                         ([id], grado_inclinacion, proporcion_corona, longitud_raiz, tamaño_diastemas, (y, x))
        Retorna:
            lista de 32 tuplas (una por cada diente) en orden 1..32.
        """
        dientes = list(range(1, 33))   # 1,2,3,...,32

        if detecciones is not None:
            return self._completar_metricas(dientes, detecciones)
        else:
            return self._generar_mock(dientes)

    def _generar_mock(self, dientes):
        """Genera valores aleatorios para todos los dientes (coordenadas (y,x) simuladas)"""
        metricas = []
        for diente in dientes:
            inclinacion = round(random.uniform(0, 45), 1)
            corona_raiz = round(random.uniform(0.5, 2.0), 2)
            longitud_raiz = random.randint(30, 60)
            diastema = round(random.uniform(0, 5), 1)
            y = random.randint(200, 600)
            x = random.randint(100, 800)
            metricas.append((diente, inclinacion, corona_raiz, longitud_raiz, diastema, (y, x)))
        return metricas

    def _completar_metricas(self, dientes, detecciones):
        """
        Rellena con ceros los dientes no presentes en detecciones.
        Se espera que detecciones sea una lista de tuplas de la forma:
        ([id], inclinacion, proporcion, longitud, diastema, (y,x))
        Donde id puede ser una lista de un entero o directamente un entero.
        """
        # Construir diccionario: id -> (inclinacion, proporcion, longitud, diastema, (y,x))
        detectados = {}
        for det in detecciones:
            # El primer elemento puede ser una lista de un elemento o un entero directo
            if isinstance(det[0], (list, tuple)) and len(det[0]) > 0:
                id_diente = det[0][0]
            else:
                id_diente = det[0]
            detectados[id_diente] = det[1:]  # el resto de la tupla

        resultado = []
        for diente in dientes:
            if diente in detectados:
                datos = detectados[diente]
                if len(datos) == 5:
                    resultado.append((
                        diente,
                        float(datos[0]),   # inclinacion
                        float(datos[1]),   # proporcion_corona
                        int(datos[2]),     # longitud_raiz
                        float(datos[3]),   # diastema
                        datos[4]           # (y, x)
                    ))
                else:
                    resultado.append((diente, 0.0, 0.0, 0, 0.0, (0, 0)))
            else:
                resultado.append((diente, 0.0, 0.0, 0, 0.0, (0, 0)))
        return resultado