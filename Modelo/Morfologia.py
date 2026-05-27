import numpy as np

class Morfologia:

    def dilatar_puntos(self, lista_puntos, kernel_size):
        h, w = kernel_size
        dx_min, dx_max = -(w // 2), (w - 1) // 2 + 1
        dy_min, dy_max = -(h // 2), (h - 1) // 2 + 1
        dx_grid, dy_grid = np.meshgrid(
            np.arange(dx_min, dx_max),
            np.arange(dy_min, dy_max),
            indexing='xy'
        )
        offsets = np.column_stack((dy_grid.ravel(), dx_grid.ravel()))
        resultados = []
        for borde in lista_puntos:
            if not borde:
                resultados.append([])
                continue
            borde_np = np.array(borde)
            puntos_dilatados = borde_np[:, None, :] + offsets
            puntos_dilatados = puntos_dilatados.reshape(-1, 2)
            puntos_unicos = np.unique(puntos_dilatados, axis=0)
            resultados.append(puntos_unicos.tolist())

        return resultados

    def erosionar_puntos(self, bordes, kernel_size):
        h, w = kernel_size
        dx_min, dx_max = -(w // 2), (w - 1) // 2 + 1
        dy_min, dy_max = -(h // 2), (h - 1) // 2 + 1

        dx_grid, dy_grid = np.meshgrid(
            np.arange(dx_min, dx_max),
            np.arange(dy_min, dy_max),
            indexing='xy'
        )
        offsets = np.column_stack((dy_grid.ravel(), dx_grid.ravel()))

        resultados = []
        for borde in bordes:
            if not borde:
                resultados.append([])
                continue

            borde_np = np.array(borde)
            vecinos = borde_np[:, None, :] + offsets

            borde_complex = borde_np[:, 0] + 1j * borde_np[:, 1]
            vecinos_complex = vecinos[:, :, 0] + 1j * vecinos[:, :, 1]

            mask = np.isin(vecinos_complex, borde_complex).all(axis=1)
            puntos_erosionados = borde_np[mask]

            resultados.append(puntos_erosionados.tolist())

        return resultados


    def cierre_puntos(self, bordes, kernel_size):
        h, w = kernel_size
        dx_min, dx_max = -(w // 2), (w - 1) // 2 + 1
        dy_min, dy_max = -(h // 2), (h - 1) // 2 + 1

        dx_grid, dy_grid = np.meshgrid(
            np.arange(dx_min, dx_max),
            np.arange(dy_min, dy_max),
            indexing='xy'
        )
        offsets = np.column_stack((dy_grid.ravel(), dx_grid.ravel()))
        todos_los_puntos = []
        for borde in bordes:
            if borde:
                todos_los_puntos.extend(borde)

        if not todos_los_puntos:
            return []

        puntos_np = np.array(todos_los_puntos)

        puntos_dilatados = puntos_np[:, None, :] + offsets
        puntos_dilatados = puntos_dilatados.reshape(-1, 2)
        borde_dilatado_unico = np.unique(puntos_dilatados, axis=0)
        vecinos = borde_dilatado_unico[:, None, :] + offsets

        borde_complex = borde_dilatado_unico[:, 0] + 1j * borde_dilatado_unico[:, 1]
        vecinos_complex = vecinos[:, :, 0] + 1j * vecinos[:, :, 1]
        mask = np.isin(vecinos_complex, borde_complex).all(axis=1)
        puntos_cerrados = borde_dilatado_unico[mask]
        return [tuple(p) for p in puntos_cerrados]