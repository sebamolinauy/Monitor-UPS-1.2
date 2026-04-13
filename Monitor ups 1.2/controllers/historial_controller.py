import os
from models.historial_model import (
    listar_historiales,
    leer_historial,
    HISTORIAL_DIR,
)

def get_lista_historiales() -> list[str]:
    """Devuelve los archivos Excel disponibles ordenados por semana."""
    return listar_historiales()

def get_datos_historial(archivo: str) -> dict:
    """Lee y devuelve el contenido de un Excel de historial."""
    return leer_historial(archivo)

def get_ruta_descarga(archivo: str) -> str | None:
    """Devuelve la ruta absoluta del archivo si existe, None si no."""
    if not archivo:
        return None
    ruta = os.path.join(HISTORIAL_DIR, archivo)
    return ruta if os.path.exists(ruta) else None