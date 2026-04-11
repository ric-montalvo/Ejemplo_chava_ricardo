import eel
import sys
import os
import base64
import re
from pathlib import Path
from datetime import datetime

# Agregar el directorio actual al path para poder importar los módulos de Ángel
sys.path.append(os.path.dirname(__file__))

from Model.Procesador_imagen import Procesador_imagen

eel.init('web')


@eel.expose
def test():
    return "Conexión establecida"


@eel.expose
def procesar_imagen_desde_js(data_url, nombre_paciente):
    """
    Recibe una imagen en formato data URL (base64) y el nombre del paciente.
    Guarda la imagen en una carpeta de expedientes, la procesa con el modelo de Ángel,
    y devuelve los resultados (rutas de las imágenes generadas).

    IMPORTANTE: Respeta el comportamiento de Ángel: la imagen invertida se guarda
    automáticamente en la MISMA carpeta que la imagen original.
    """
    try:
        # Decodificar data URL
        # Formato esperado: data:image/jpeg;base64,....
        match = re.match(r'data:image/(?P<ext>\w+);base64,(?P<data>.+)', data_url)
        if not match:
            return {"exito": False, "error": "Formato de imagen inválido"}

        ext = match.group('ext')
        data = match.group('data')
        img_bytes = base64.b64decode(data)

        # Normalizar extensión (jpeg -> jpg para compatibilidad)
        if ext.lower() == 'jpeg':
            ext = 'jpg'

        # Crear carpeta de expedientes (igual que en RF9)
        # Estructura: expedientes/NombrePaciente_fecha/
        fecha_actual = datetime.now().strftime("%Y%m%d_%H%M%S")
        paciente_slug = re.sub(r'[^a-zA-Z0-9]', '_', nombre_paciente)
        carpeta_paciente = Path(__file__).parent / "expedientes" / f"{paciente_slug}_{fecha_actual}"
        carpeta_paciente.mkdir(parents=True, exist_ok=True)

        # Guardar la imagen original en la carpeta del paciente
        nombre_imagen = f"{paciente_slug}_original.{ext}"
        ruta_original = carpeta_paciente / nombre_imagen

        with open(ruta_original, "wb") as f:
            f.write(img_bytes)

        print(f"📁 Imagen original guardada en: {ruta_original}")

        # === AHORA USAMOS EL MODELO DE ÁNGEL ===
        # El modelo procesará la imagen y guardará automáticamente la invertida
        # en la MISMA carpeta que la original (eso es lo que hace guardar_resultado)
        modelo = Procesador_imagen()
        resultados = modelo.procesar_pipeline(str(ruta_original))

        # resultados es una lista de tuplas (imagen_PIL, texto)
        # Ejemplo: [
        #   (img_original, "1. Imagen Original"),
        #   (img_gris, "2. Escala de Grises"),
        #   (img_invertida, "3. Inversión de grises")
        # ]

        # Guardar cada etapa como imagen para poder mostrarlas en la UI
        rutas_salida = []
        for i, (img_pil, texto) in enumerate(resultados):
            ruta_img = carpeta_paciente / f"{paciente_slug}_step_{i}.png"
            img_pil.save(ruta_img)
            rutas_salida.append({
                "texto": texto,
                "ruta": str(ruta_img)
            })

        # Buscar la imagen invertida que guardó Ángel (debería estar en la misma carpeta)
        invertida_angel = None
        for archivo in carpeta_paciente.glob("*_invertida.*"):
            invertida_angel = str(archivo)
            print(f"📸 Imagen invertida (guardada por Ángel): {invertida_angel}")

        return {
            "exito": True,
            "carpeta_paciente": str(carpeta_paciente),
            "imagenes": rutas_salida,
            "invertida_angel": invertida_angel,
            "mensaje": f"Procesado correctamente. Imagen invertida guardada en: {carpeta_paciente}"
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"exito": False, "error": str(e)}


@eel.expose
def listar_expedientes():
    """
    Lista todos los expedientes guardados en la carpeta 'expedientes/'
    """
    try:
        expedientes_dir = Path(__file__).parent / "expedientes"
        if not expedientes_dir.exists():
            return []

        expedientes = []
        for carpeta in expedientes_dir.iterdir():
            if carpeta.is_dir():
                # Buscar metadata (por ejemplo, la imagen original o el CSV)
                info = {
                    "nombre": carpeta.name,
                    "ruta": str(carpeta),
                    "fecha": datetime.fromtimestamp(carpeta.stat().st_ctime).strftime("%Y-%m-%d %H:%M:%S")
                }
                # Buscar cuántas imágenes hay
                imagenes = list(carpeta.glob("*.png")) + list(carpeta.glob("*.jpg")) + list(carpeta.glob("*.bmp"))
                info["num_archivos"] = len(imagenes)
                expedientes.append(info)

        # Ordenar por fecha descendente (más reciente primero)
        expedientes.sort(key=lambda x: x["fecha"], reverse=True)
        return expedientes

    except Exception as e:
        print(f"Error al listar expedientes: {e}")
        return []


@eel.expose
def eliminar_expediente(ruta_carpeta):
    """
    Elimina un expediente completo (carpeta y todo su contenido)
    """
    try:
        import shutil
        carpeta = Path(ruta_carpeta)
        if carpeta.exists() and carpeta.is_dir():
            shutil.rmtree(carpeta)
            return {"exito": True}
        return {"exito": False, "error": "Carpeta no encontrada"}
    except Exception as e:
        return {"exito": False, "error": str(e)}


# Iniciar la aplicación con Eel
eel.start('index.html', size=(1200, 800), port=0, mode='brave')