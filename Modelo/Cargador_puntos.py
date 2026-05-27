import csv
from pathlib import Path
import numpy as np
import sys

class Cargador_puntos:
    def __init__(self):
        self.nombre_archivo = None   # se asigna desde Orquestador

    def set_nombre_archivo(self, nombre):
        self.nombre_archivo = nombre

    def obtener_puntos_por_arcada(self):
        """Devuelve (maxilar, mandibular) como listas de tuplas (y, x)"""
        if self.nombre_archivo is not None:
            return self._leer_desde_csv(self.nombre_archivo)
        else:
            # Fallback: puntos fijos de Laura (para pruebas sin CSV)
            return self._puntos_fijos()


    #Metodo cuando esta en exe
    def _leer_desde_csv(self, nombre):
        import sys
        if getattr(sys, 'frozen', False):
            # Estamos dentro de un ejecutable (PyInstaller)
            base_dir = Path(sys._MEIPASS)
        else:
            base_dir = Path(__file__).parent.parent
        csv_path = base_dir / "diastemas.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"No se encuentra {csv_path}")

        maxilar = []
        mandibular = []

        # Usar utf-8-sig para eliminar posibles BOM
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            # Detectar delimitador automáticamente (puede ser ',' o '\t')
            primera_linea = f.readline()
            f.seek(0)
            if '\t' in primera_linea:
                delim = '\t'
            elif ',' in primera_linea:
                delim = ','
            else:
                delim = None  # fallback
            reader = csv.DictReader(f, delimiter=delim)
            # Limpiar nombres de columnas (quitar espacios)
            reader.fieldnames = [col.strip() for col in reader.fieldnames]

            # Verificar que la columna 'paciente' exista (caso insensible)
            col_paciente = None
            for col in reader.fieldnames:
                if col.lower() == 'paciente':
                    col_paciente = col
                    break
            if col_paciente is None:
                raise KeyError(f"No se encontró columna 'paciente'. Columnas disponibles: {reader.fieldnames}")

            for row in reader:
                if row[col_paciente].strip().upper() != nombre.upper():
                    continue
                pos = row['posicion'].strip().lower()
                izq = self._parsear_punto(row['inicioBordeIzquierdo'])
                der = self._parsear_punto(row['inicioBordeDerecho'])
                if pos == 'maxilar':
                    maxilar.append(izq)
                    maxilar.append(der)
                elif pos == 'mandibula':
                    mandibular.append(izq)
                    mandibular.append(der)

        if not maxilar and not mandibular:
            raise ValueError(f"No se encontraron puntos para '{nombre}' en el CSV")

        return maxilar, mandibular

    def _parsear_punto(self, cadena):
        """Convierte '[X Y]' en (Y, X)"""
        cadena = cadena.strip().strip('[]')
        x, y = map(int, cadena.split())
        return (y, x)   # (fila, columna)

    def _puntos_fijos(self):
        """Puntos de Laura (fallback)"""
        maxilar = [(450, 562), (448, 576), (446, 602), (460, 624), (462, 647),
                   (466, 664), (463, 673), (469, 687), (474, 702), (477, 715),
                   (485, 752), (477, 762), (486, 816), (495, 826), (500, 878),
                   (499, 891), (500, 949), (509, 963), (480, 985), (482, 1005),
                   (499, 1022), (500, 1037), (494, 1084), (483, 1098), (460, 1115),
                   (459, 1128), (480, 1148), (481, 1170), (475, 1192), (477, 1206),
                   (461, 1244), (463, 1260), (453, 1281), (453, 1308), (442, 1325),
                   (461, 1339)]
        mandibular = [(571, 451), (571, 477), (618, 552), (602, 572), (644, 644),
                      (638, 662), (659, 705), (651, 720), (668, 765), (667, 781),
                      (673, 831), (675, 841), (679, 886), (679, 897), (684, 940),
                      (684, 953), (679, 997), (679, 1009), (676, 1053), (676, 1066),
                      (649, 1116), (668, 1132), (638, 1175), (658, 1195), (628, 1234),
                      (645, 1253), (620, 1264), (621, 1301), (610, 1320), (613, 1344),
                      (593, 1360), (594, 1391), (569, 1415), (570, 1435)]
        return maxilar, mandibular

    # El resto de métodos originales se mantienen sin cambios
    def obtener_ancho_entre_puntos(self):
        return 0, 0

    def separar_maxilar_mandibular(self, puntos):
        if len(puntos) < 2:
            return puntos, []
        puntos_ordenados = sorted(puntos, key=lambda p: p[0])
        max_salto = 0
        indice = 0
        for i in range(len(puntos_ordenados)-1):
            salto = puntos_ordenados[i+1][0] - puntos_ordenados[i][0]
            if salto > max_salto:
                max_salto = salto
                indice = i+1
        return puntos_ordenados[:indice], puntos_ordenados[indice:]

    def obtener_largo_raices(self, lista_puntos, valor):
        return np.full(len(lista_puntos), valor)

    def obtener_puntos_validos(self, magnitud, radio=3):
        # Como este método no se usa en el pipeline actual, lo dejamos vacío o con pass
        # Si se necesita en el futuro, habrá que implementarlo correctamente.
        maxilar, mandibular = self.obtener_puntos_por_arcada()
        # Por ahora devolvemos los puntos sin validar (no recomendado, pero evita error)
        return maxilar, mandibular

    def obtener_puntos_visualizables(self, lista_puntos, imagen, radio=1):
        h, w = imagen.shape
        return [(i, j)
                for y, x in lista_puntos
                for i in range(max(0, y-radio), min(h, y+radio+1))
                for j in range(max(0, x-radio), min(w, x+radio+1))]