import json
from pathlib import Path


class GestorJSON:
    """Centraliza el acceso a archivos JSON; ninguna otra capa abre archivos."""
    def __init__(self, nombre_archivo):
        self.ruta = Path(__file__).resolve().parent.parent / "data" / nombre_archivo
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        if not self.ruta.exists():
            self.guardar([])

    def leer(self):
        try:
            with self.ruta.open("r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                return datos if isinstance(datos, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def guardar(self, datos):
        with self.ruta.open("w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=2)
