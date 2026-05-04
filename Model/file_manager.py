# model/file_manager.py
import shutil
from pathlib import Path
from datetime import datetime
from utils.helpers import sanitizar_nombre

class FileManager:
    def __init__(self, base_dir: Path):
        self.expedientes_dir = base_dir / "expedientes"
        self.expedientes_dir.mkdir(exist_ok=True)

    # ========== Métodos auxiliares (nuevos) ==========
    def sanitizar_nombre_carpeta(self, nombre: str) -> str:
        """Convierte el nombre a un formato válido para carpeta (sin espacios, minúsculas)"""
        return sanitizar_nombre(nombre).lower().replace(' ', '_')

    def existe_carpeta(self, nombre_limpio: str) -> bool:
        """Busca cualquier carpeta (en cualquier nivel) que coincida exactamente con el nombre (insensible)"""
        for carpeta in self.expedientes_dir.rglob("*"):
            if carpeta.is_dir() and carpeta.name.lower() == nombre_limpio:
                return True
        return False

    def obtener_carpeta_por_nombre(self, nombre_limpio: str) -> Path | None:
        """Devuelve la ruta de la primera carpeta que coincida (insensible)"""
        for carpeta in self.expedientes_dir.rglob("*"):
            if carpeta.is_dir() and carpeta.name.lower() == nombre_limpio:
                return carpeta
        return None

    def crear_carpeta_raiz(self, nombre_limpio: str) -> Path:
        """Crea una carpeta directamente en expedientes/ (sin fecha)"""
        carpeta = self.expedientes_dir / nombre_limpio
        carpeta.mkdir(parents=True, exist_ok=False)  # si existe, lanza error
        return carpeta

    def crear_subcarpeta(self, carpeta_base: Path) -> Path:
        """Crea una subcarpeta dentro de carpeta_base con nombre base_numero (ej: juan_1)"""
        base = carpeta_base.name
        contador = 1
        while True:
            subnombre = f"{base}_{contador}"
            subcarpeta = carpeta_base / subnombre
            if not subcarpeta.exists():
                subcarpeta.mkdir(parents=True)
                return subcarpeta
            contador += 1

    def copiar_imagen_a_carpeta(self, ruta_origen: str, carpeta_destino: Path, nombre_base: str) -> Path:
        """Copia (o sobrescribe) la imagen original en la carpeta destino"""
        ext = Path(ruta_origen).suffix
        destino = carpeta_destino / f"{nombre_base}_original{ext}"
        shutil.copy2(ruta_origen, destino)
        return destino

    # ========== Métodos originales (con nueva implementación) ==========
    def crear_carpeta_paciente(self, nombre_paciente: str) -> Path:
        """
        Crea una carpeta raíz sin fecha. Si el nombre ya existe (en cualquier nivel),
        se lanza una excepción para que el controlador decida qué hacer.
        """
        nombre_limpio = self.sanitizar_nombre_carpeta(nombre_paciente)
        if self.existe_carpeta(nombre_limpio):
            raise FileExistsError(f"Ya existe una carpeta con el nombre '{nombre_limpio}'")
        return self.crear_carpeta_raiz(nombre_limpio)

    def copiar_original(self, ruta_origen: str, carpeta_destino: Path, nombre_paciente: str) -> Path:
        """
        Copia la imagen original a la carpeta destino.
        El nombre_base se toma del nombre de la carpeta destino (para mantener consistencia).
        """
        nombre_base = carpeta_destino.name
        return self.copiar_imagen_a_carpeta(ruta_origen, carpeta_destino, nombre_base)

    def guardar_imagen_grises(self, img_pil, carpeta: Path, nombre_paciente: str) -> Path:
        """Guarda la imagen en grises dentro de la carpeta"""
        nombre_base = carpeta.name
        ruta = carpeta / f"{nombre_base}_grises.png"
        img_pil.save(ruta)
        return ruta

    def listar_expedientes(self) -> list[Path]:
        """Devuelve solo las carpetas raíz (no subcarpetas) que contengan una imagen original (cualquier extensión)."""
        expedientes = []
        for carpeta in self.expedientes_dir.iterdir():  # solo un nivel
            if carpeta.is_dir():
                # Buscar cualquier archivo que contenga "_original." en el nombre
                tiene_original = any("_original." in f.name for f in carpeta.glob("*"))
                if tiene_original:
                    expedientes.append(carpeta)
        return expedientes