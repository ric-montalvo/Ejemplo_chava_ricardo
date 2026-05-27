import numpy as np


class Filtros_espaciales:

    def filtro_mediana(self, imagen: np.ndarray, rad: int) -> np.ndarray:
        if rad < 1: return imagen

        h, w = imagen.shape
        capas = []
        for di in range(-rad, rad + 1):
            for dj in range(-rad, rad + 1):
                i_start, i_end = rad + di, h - rad + di
                j_start, j_end = rad + dj, w - rad + dj
                capas.append(imagen[i_start:i_end, j_start:j_end])
        stack = np.stack(capas, axis=0)
        img_filtrada = np.median(stack, axis=0)
        img_final = imagen.copy()
        img_final[rad:h - rad, rad:w - rad] = img_filtrada

        return img_final