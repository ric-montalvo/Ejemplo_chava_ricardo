# model/file_manager.py
import shutil
from pathlib import Path
from datetime import datetime
from utils.helpers import sanitizar_nombre

class FileManager:
    def __init__(self, base_dir: Path):
        self.expedientes_dir = base_dir / "expedientes"
        self.expedientes_dir.mkdir(exist_ok=True)

    def crear_carpeta_paciente(self, nombre_paciente: str) -> Path:
        fecha_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_limpio = sanitizar_nombre(nombre_paciente)
        carpeta = self.expedientes_dir / f"{nombre_limpio}_{fecha_str}"
        carpeta.mkdir(parents=True, exist_ok=True)
        return carpeta

    def copiar_original(self, ruta_origen: str, carpeta_destino: Path, nombre_paciente: str) -> Path:
        ext = Path(ruta_origen).suffix
        nombre_limpio = sanitizar_nombre(nombre_paciente)
        destino = carpeta_destino / f"{nombre_limpio}_original{ext}"
        shutil.copy2(ruta_origen, destino)
        return destino

    def guardar_imagen_grises(self, img_pil, carpeta: Path, nombre_paciente: str) -> Path:
        nombre_limpio = sanitizar_nombre(nombre_paciente)
        ruta = carpeta / f"{nombre_limpio}_grises.png"
        img_pil.save(ruta)
        return ruta

    def listar_expedientes(self):
        return [c for c in self.expedientes_dir.iterdir() if c.is_dir()]