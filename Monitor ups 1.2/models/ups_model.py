from dataclasses import dataclass
from typing import Optional

@dataclass
class UPS:
    """Representa la configuracion de un UPS."""
    nombre    : str
    ip        : str
    sala      : str
    ubicacion : str
    marca     : str
    modelo    : str
    community : str = 'public'

    def to_dict(self) -> dict:
        return self.__dict__

    @staticmethod
    def from_dict(d: dict) -> 'UPS':
        return UPS(**d)


@dataclass
class DatosUPS:
    """Resultado de una consulta SNMP a un UPS."""
    nombre          : str
    ip              : str
    sala            : str
    ubicacion       : str
    marca           : str
    modelo          : str
    estado          : str
    bateria_pct     : Optional[int]
    voltaje_entrada : Optional[float]
    voltaje_salida  : Optional[float]
    carga_w         : Optional[int]
    carga_pct       : Optional[float]
    temperatura     : Optional[int]
    autonomia_min   : Optional[int]

    def to_dict(self) -> dict:
        return self.__dict__


@dataclass
class Alerta:
    """Representa una alerta activa."""
    ups    : str
    sala   : str
    estado : str
    nivel  : str   # 'falla' o 'advertencia'
    hora   : str

    def to_dict(self) -> dict:
        return self.__dict__