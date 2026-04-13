from models.config_model import cargar_config, guardar_config
from models.ups_model import UPS

def listar_ups() -> list[dict]:
    """Devuelve la lista completa de UPS configurados."""
    return cargar_config()

def agregar_ups(datos: dict) -> list[dict]:
    """Agrega un UPS nuevo a la configuracion."""
    lista = cargar_config()
    lista.append(datos)
    guardar_config(lista)
    return lista

def editar_ups(indice: int, datos: dict) -> list[dict]:
    """Edita un UPS existente por su indice."""
    lista = cargar_config()
    if indice < 0 or indice >= len(lista):
        raise IndexError(f"Indice {indice} fuera de rango")
    lista[indice] = datos
    guardar_config(lista)
    return lista

def eliminar_ups(indice: int) -> list[dict]:
    """Elimina un UPS por su indice."""
    lista = cargar_config()
    if indice < 0 or indice >= len(lista):
        raise IndexError(f"Indice {indice} fuera de rango")
    lista.pop(indice)
    guardar_config(lista)
    return lista

def guardar_lista_completa(lista: list[dict]) -> list[dict]:
    """Guarda la lista completa de UPS (usada por el admin del dashboard)."""
    guardar_config(lista)
    return lista