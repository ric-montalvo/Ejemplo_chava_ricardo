# utils/helpers.py
import re
from datetime import datetime

def sanitizar_nombre(nombre: str) -> str:
    """Limpia el nombre del paciente para usar en nombres de carpeta."""
    return re.sub(r'[^a-zA-Z0-9áéíóúüñÁÉÍÓÚÜÑ ._-]', '', nombre)

def formatear_fecha(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%d de %B de %Y, %H:%M")