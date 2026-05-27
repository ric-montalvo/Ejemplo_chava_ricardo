import numpy as np


class Utilidades_npListas:

    def aplanar_lista_de_tuplas(self, lista_de_listas):
        listas_filtradas = [sub for sub in lista_de_listas if len(sub) > 0]
        if not listas_filtradas:
            return []
        arreglo_completo = np.vstack(listas_filtradas)
        return [tuple(fila) for fila in arreglo_completo]

