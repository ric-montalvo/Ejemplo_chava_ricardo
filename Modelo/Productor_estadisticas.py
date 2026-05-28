import random

class ProductorEstadisticas:
    """
    Genera métricas dentales (32 dientes, nomenclatura Palmer).
    Cuando Montoya tenga datos reales, llamará a generar_metricas(datos_reales)
    con una lista de 32 objetos en el formato acordado.
    """

    def generar_metricas(self, datos_reales=None):
        """
        Retorna una lista de 32 listas, una por cada diente.
        Cada sublista: [diente, inclinacion, corona_raiz, longitud_raiz, diastema, ubicacion]
        """
        dientes = [11,12,13,14,15,16,17,18,
                   21,22,23,24,25,26,27,28,
                   31,32,33,34,35,36,37,38,
                   41,42,43,44,45,46,47,48]

        if datos_reales is not None:
            metricas = []
            for i, diente in enumerate(dientes):
                dato = datos_reales[
                    i]  # dato es una lista [inclinacion, corona_raiz, longitud_raiz, diastema, ubicacion]
                metricas.append([
                    diente,
                    dato[0],  # inclinacion
                    dato[1],  # corona_raiz
                    dato[2],  # longitud_raiz
                    dato[3],  # diastema
                    dato[4]  # ubicacion
                ])
            return metricas

        # --- Datos mock (aleatorios) ---
        metricas = []
        for diente in dientes:
            inclinacion = round(random.uniform(0, 45), 1)
            corona_raiz = round(random.uniform(0.5, 2.0), 2)
            longitud_raiz = random.randint(30, 60)
            diastema = round(random.uniform(0, 5), 1)
            if 11 <= diente <= 18:
                ubicacion = "Superior Derecho"
            elif 21 <= diente <= 28:
                ubicacion = "Superior Izquierdo"
            elif 31 <= diente <= 38:
                ubicacion = "Inferior Izquierdo"
            else:
                ubicacion = "Inferior Derecho"
            metricas.append([diente, inclinacion, corona_raiz, longitud_raiz, diastema, ubicacion])
        return metricas