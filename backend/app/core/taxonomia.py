"""Taxonomía de rubros, certificaciones y maquinaria.

Es el "idioma común" entre la demanda (pliegos) y la oferta (perfiles de PyMEs).
Todo el matching se hace sobre estos códigos, nunca sobre texto libre: así el
resultado es reproducible y explicable.

Para agregar un rubro: sumarlo a RUBROS con su familia, unidad y palabras clave
(las palabras clave alimentan el sugeridor de rubros, ver `sugeridor.py`).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Rubro:
    codigo: str
    nombre: str
    familia: str
    unidad: str
    palabras_clave: tuple[str, ...] = field(default_factory=tuple)


FAMILIAS: dict[str, str] = {
    "MET": "Metalmecánica",
    "ELE": "Eléctrica e instrumentación",
    "CIV": "Obra civil",
    "LOG": "Logística y transporte",
    "SRV": "Servicios generales",
    "AMB": "Ambiente y residuos",
    "SEG": "Seguridad e insumos",
}

_RUBROS: list[Rubro] = [
    Rubro("MET-FAB", "Fabricación y montaje de estructuras metálicas", "MET", "t/mes",
          ("estructura", "estructuras metalicas", "soldadura", "acero", "caldereria",
           "montaje estructural", "nave", "galpon")),
    Rubro("MET-MEC", "Mantenimiento mecánico de equipos", "MET", "HH/mes",
          ("mantenimiento mecanico", "bombas", "reductores", "overhaul", "chancador",
           "molino", "cintas transportadoras")),
    Rubro("MET-TOR", "Mecanizado y tornería", "MET", "HH/mes",
          ("torno", "torneria", "mecanizado", "cnc", "piezas", "repuestos")),
    Rubro("ELE-MT", "Montaje eléctrico de media y baja tensión", "ELE", "HH/mes",
          ("electrico", "electrica", "tableros", "media tension", "baja tension",
           "cableado", "subestacion", "iluminacion")),
    Rubro("ELE-INS", "Instrumentación y control", "ELE", "HH/mes",
          ("instrumentacion", "plc", "sensores", "calibracion", "automatizacion",
           "scada", "control")),
    Rubro("CIV-MOV", "Movimiento de suelos", "CIV", "m3/mes",
          ("movimiento de suelos", "excavacion", "terraplen", "nivelacion", "aridos",
           "plataformas", "caminos")),
    Rubro("CIV-HOR", "Obras de hormigón", "CIV", "m3/mes",
          ("hormigon", "fundaciones", "encofrado", "bases", "losas", "obra civil")),
    Rubro("LOG-CAR", "Transporte de carga general", "LOG", "viajes/mes",
          ("transporte de carga", "flete", "camion", "logistica", "carga general")),
    Rubro("LOG-PEL", "Transporte de mercancías peligrosas", "LOG", "viajes/mes",
          ("mercancias peligrosas", "combustible", "reactivos", "carga peligrosa")),
    Rubro("LOG-PER", "Transporte de personal", "LOG", "servicios/mes",
          ("transporte de personal", "traslado", "colectivo", "minibus", "pasajeros")),
    Rubro("SRV-CAT", "Catering y comedor", "SRV", "raciones/mes",
          ("catering", "comida", "raciones", "comedor", "vianda", "alimentacion")),
    Rubro("SRV-LIM", "Limpieza industrial", "SRV", "HH/mes",
          ("limpieza", "limpieza industrial", "higiene", "mantenimiento de campamento")),
    Rubro("AMB-RES", "Gestión de residuos", "AMB", "t/mes",
          ("residuos", "reciclaje", "disposicion final", "residuos peligrosos")),
    Rubro("AMB-LAB", "Análisis de laboratorio (agua y suelos)", "AMB", "muestras/mes",
          ("laboratorio", "muestras", "analisis", "calidad de agua", "suelos")),
    Rubro("AMB-MON", "Monitoreo ambiental", "AMB", "campañas/mes",
          ("monitoreo", "ambiental", "material particulado", "ruido", "polvo", "aire")),
    Rubro("SEG-EPP", "Provisión de elementos de protección personal", "SEG", "unidades/mes",
          ("epp", "cascos", "guantes", "ropa de trabajo", "calzado de seguridad")),
]

RUBROS: dict[str, Rubro] = {r.codigo: r for r in _RUBROS}

CERTIFICACIONES: dict[str, str] = {
    "ISO-9001": "Sistema de gestión de calidad (ISO 9001)",
    "ISO-14001": "Sistema de gestión ambiental (ISO 14001)",
    "ISO-45001": "Sistema de gestión de seguridad y salud en el trabajo (ISO 45001)",
    "ISO-17025": "Competencia de laboratorios de ensayo (ISO/IEC 17025)",
    "HAB-PEL": "Habilitación para transporte de mercancías peligrosas",
    "HAB-BROM": "Habilitación bromatológica",
    "REG-RES": "Inscripción como operador/transportista de residuos peligrosos",
    "SEG-ALT": "Personal capacitado en trabajos en altura",
}

MAQUINARIA: dict[str, str] = {
    "grua": "Grúa",
    "equipo_soldadura": "Equipos de soldadura",
    "torno_cnc": "Torno CNC",
    "retroexcavadora": "Retroexcavadora",
    "camion_volcador": "Camión volcador",
    "hormigonera": "Motohormigonera",
    "camion_cisterna": "Camión cisterna",
    "minibus": "Minibús",
    "camioneta_4x4": "Camioneta 4x4",
    "laboratorio_movil": "Laboratorio móvil",
}


def nombre_familia(codigo_rubro: str) -> str:
    return FAMILIAS[RUBROS[codigo_rubro].familia]


def validar_rubro(codigo: str) -> str:
    if codigo not in RUBROS:
        raise ValueError(f"Rubro desconocido: {codigo!r}")
    return codigo


def validar_certificacion(codigo: str) -> str:
    if codigo not in CERTIFICACIONES:
        raise ValueError(f"Certificación desconocida: {codigo!r}")
    return codigo


def validar_maquinaria(codigo: str) -> str:
    if codigo not in MAQUINARIA:
        raise ValueError(f"Maquinaria desconocida: {codigo!r}")
    return codigo
