import numpy as np

class Metodos_numericos:

    def minimos_cuadrados(self, lista_puntos):
        puntos = np.array(lista_puntos)
        puntos_y = puntos[:, 0]
        puntos_x = puntos[:, 1]
        elementos = len(puntos_y)
        sum_y = np.sum(puntos_y)
        sum_x = np.sum(puntos_x)
        prod_yx = puntos_y * puntos_x
        sum_yx = np.sum(prod_yx)
        sum_xx = np.sum(puntos_x ** 2)

        denominador = sum_xx - ((sum_x ** 2) / elementos)

        if denominador == 0:
            return [np.nan, np.nan]

        m = (sum_yx - ((sum_y * sum_x) / elementos)) / denominador
        b = np.mean(puntos_y) - (m * np.mean(puntos_x))

        return [m, b]

    def algoritmo_Bresenham(self, punto0, punto1):
        y0, x0 = punto0
        y1, x1 = punto1
        puntos = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            puntos.append((y0, x0))
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
        return puntos


    def extrapolar_borde(self, puntos, n_pasos, direccion_y=1, tamaño_paso_y=1.0, conectar_exacto=True):
        if len(puntos) < 2:
            return puntos
        y = np.array([p[0] for p in puntos])
        x = np.array([p[1] for p in puntos])

        coeficientes = np.polyfit(y, x, 1)
        pendiente_m = coeficientes[0]
        intercepto_b = coeficientes[1]

        if direccion_y > 0:
            indice_extremo = np.argmax(y)
        else:
            indice_extremo = np.argmin(y)

        y_ancla = y[indice_extremo]
        x_ancla = x[indice_extremo]

        if conectar_exacto:
            intercepto_b = x_ancla - (pendiente_m * y_ancla)

        funcion_recta_x = np.poly1d([pendiente_m, intercepto_b])
        direccion_limpia = np.sign(direccion_y)

        nuevos_y = [y_ancla + (i * tamaño_paso_y * direccion_limpia) for i in range(1, n_pasos + 1)]
        nuevos_x = funcion_recta_x(nuevos_y)

        puntos_proyectados = [(int(round(ny)), int(round(nx))) for ny, nx in zip(nuevos_y, nuevos_x)]

        return puntos_proyectados