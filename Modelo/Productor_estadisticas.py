import random

class ProductorEstadisticas:
    """
    Genera métricas dentales (32 dientes, nomenclatura Palmer).
    Cada métrica es una tupla:
    (id_palmer, grado_inclinacion, proporcion_corona, longitud_raiz, tamaño_diastemas, (y, x))
    Si un diente no es detectado, sus valores son 0 y (0,0).
    """

    def generar_metricas(self, detecciones=None):
        """
        Parámetro:
            detecciones: lista de tuplas con los dientes detectados, cada tupla con el formato
                         (id_palmer, grado_inclinacion, proporcion_corona, longitud_raiz, tamaño_diastemas, (y, x))
        Retorna:
            lista de 32 tuplas (una por cada diente Palmer) en el orden estándar.
        """
        dientes = [11,12,13,14,15,16,17,18,
                   21,22,23,24,25,26,27,28,
                   31,32,33,34,35,36,37,38,
                   41,42,43,44,45,46,47,48]

        if detecciones is not None:
            return self._completar_metricas(dientes, detecciones)
        else:
            # Datos mock completos (todos los dientes)
            return self._generar_mock(dientes)

    def _generar_mock(self, dientes):
        """Genera valores aleatorios para todos los dientes (incluye coordenadas (y,x) simuladas)"""
        metricas = []
        for diente in dientes:
            inclinacion = round(random.uniform(0, 45), 1)
            corona_raiz = round(random.uniform(0.5, 2.0), 2)
            longitud_raiz = random.randint(30, 60)
            diastema = round(random.uniform(0, 5), 1)
            # Simular coordenadas (y, x) dentro de una imagen típica (200-600 para y, 100-800 para x)
            y = random.randint(200, 600)
            x = random.randint(100, 800)
            metricas.append((diente, inclinacion, corona_raiz, longitud_raiz, diastema, (y, x)))
        return metricas

    def _completar_metricas(self, dientes, detecciones):
        """Rellena con ceros los dientes no presentes en detecciones"""
        # Convertir detecciones en un diccionario para acceso rápido
        detectados = {d[0]: d[1:] for d in detecciones}  # clave: id, valor: tupla sin el id
        resultado = []
        for diente in dientes:
            if diente in detectados:
                # La detección contiene (inclinacion, corona_raiz, longitud_raiz, diastema, (y,x))
                datos = detectados[diente]
                # Aseguramos que tenga 5 elementos (incluyendo la tupla de coordenadas)
                if len(datos) == 5:
                    resultado.append((diente, datos[0], datos[1], datos[2], datos[3], datos[4]))
                else:
                    # Fallback: si no tiene el formato esperado, poner ceros
                    resultado.append((diente, 0.0, 0.0, 0, 0.0, (0, 0)))
            else:
                # Diente no detectado: valores cero y coordenadas (0,0)
                resultado.append((diente, 0.0, 0.0, 0, 0.0, (0, 0)))
        return resultado