"""Genera los datos de DEMOSTRACIÓN en app/data/.

TODOS los proveedores y pliegos son FICTICIOS (rotulados [DEMO] y con
`ficticio: true`). Cualquier parecido con empresas reales es casual. No se
usan datos de empresas reales para no exponer información privada y para
respetar la consigna de no inventar datos presentados como reales.

El escenario está diseñado para que la demo muestre los cuatro resultados
posibles: PyME local directa, UTE local, proveedor no local y lote dividido.

Uso:  python scripts/generar_datos_demo.py
"""

from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "app" / "data"

SJ = "San Juan"


def prov(id, nombre, depto, caps, certs, maq, dot, exp, dom=True, trib=True, pct=90,
         repromin=False, provincia=SJ, desc=""):
    return {
        "id": id,
        "razon_social": f"{nombre} [DEMO]",
        "ficticio": True,
        "pais": "Argentina",
        "provincia": provincia,
        "departamento": depto,
        "descripcion": desc,
        "capacidades": [{"rubro": r, "capacidad_mensual": c} for r, c in caps.items()],
        "certificaciones": [{"codigo": c, "vence": v} for c, v in certs.items()],
        "maquinaria": maq,
        "dotacion": dot,
        "anios_experiencia_minera": exp,
        "arraigo": {
            "domicilio_operativo_sj": dom,
            "tributa_en_sj": trib,
            "porcentaje_personal_sanjuanino": pct,
            "inscripto_repromin": repromin,
        },
    }


NO_LOCAL = {"dom": False, "trib": False, "pct": 5}

PROVEEDORES = [
    # --- Metalmecánica ---------------------------------------------------------
    prov("S01", "Talleres Retamo SRL", "Rawson", {"MET-FAB": 40},
         {"ISO-9001": "2027-06-30", "SEG-ALT": "2027-01-31", "ISO-45001": "2026-08-31"},
         ["grua", "equipo_soldadura"], 35, 8, pct=92, repromin=True,
         desc="Fabricación y montaje de estructuras metálicas para naves industriales."),
    prov("S02", "Metalúrgica Jarilla SA", "Chimbas", {"MET-FAB": 30, "MET-TOR": 1200},
         {"ISO-9001": "2027-03-31", "SEG-ALT": "2026-12-31"},
         ["equipo_soldadura", "grua", "torno_cnc"], 24, 5, pct=85,
         desc="Estructuras metálicas y mecanizado de piezas."),
    prov("S03", "Estructuras Pichana SRL", "Pocito", {"MET-FAB": 20},
         {"ISO-9001": "2026-10-01"}, ["equipo_soldadura"], 14, 3, pct=95,
         desc="Estructuras livianas y soldadura."),
    prov("S04", "Soldaduras Algarrobo", "Santa Lucía", {"MET-FAB": 15},
         {"SEG-ALT": None}, ["equipo_soldadura"], 9, 2, pct=100,
         desc="Soldadura y montaje en altura."),
    prov("S05", "Calderería Tusca SRL", "Albardón", {"MET-FAB": 25, "MET-MEC": 2000},
         {"ISO-9001": "2027-02-28", "SEG-ALT": "2027-02-28"},
         ["equipo_soldadura", "grua"], 22, 6, pct=88,
         desc="Calderería, estructuras y mantenimiento mecánico."),
    prov("S06", "Mantenimiento Chañar SRL", "San Martín", {"MET-MEC": 3500},
         {"ISO-9001": "2027-09-30", "ISO-45001": "2027-09-30"}, ["camioneta_4x4"], 28, 6,
         pct=90, repromin=True, desc="Mantenimiento mecánico de equipos de planta."),
    prov("S07", "Servicios Mecánicos Brea", "Caucete", {"MET-MEC": 2500, "MET-TOR": 800},
         {"ISO-45001": "2027-04-30"}, ["torno_cnc"], 18, 4, pct=82,
         desc="Mantenimiento de bombas, reductores y tornería."),
    prov("S24", "Tornería de Precisión Chilca", "Capital", {"MET-TOR": 900},
         {"ISO-9001": "2027-08-31"}, ["torno_cnc"], 7, 4, pct=100,
         desc="Mecanizado CNC de repuestos."),
    # --- Obra civil --------------------------------------------------------------
    prov("S08", "Movimientos de Suelo Pircas SRL", "Ullum", {"CIV-MOV": 30000},
         {"ISO-45001": "2027-05-31"}, ["retroexcavadora", "camion_volcador"], 20, 7, pct=90,
         desc="Movimiento de suelos, plataformas y caminos."),
    prov("S09", "Hormigones Atalaya SA", "Rivadavia", {"CIV-HOR": 1500},
         {"ISO-9001": "2027-07-31"}, ["hormigonera"], 18, 4, pct=87,
         desc="Fundaciones y obras de hormigón."),
    prov("S10", "Construcciones Jume", "Sarmiento", {"CIV-MOV": 10000, "CIV-HOR": 600},
         {"ISO-9001": "2027-01-31"}, ["retroexcavadora", "hormigonera"], 16, 3, pct=70,
         desc="Obras civiles menores. Parte del personal reside fuera de la provincia."),
    # --- Eléctrica ---------------------------------------------------------------
    prov("S11", "Electromontajes Altavista SRL", "Capital", {"ELE-MT": 3500},
         {"ISO-45001": "2027-03-31"}, ["camioneta_4x4"], 26, 6, pct=91, repromin=True,
         desc="Montajes eléctricos de media y baja tensión."),
    prov("S12", "Control y Automatización Molle SRL", "Capital", {"ELE-INS": 1000},
         {"ISO-9001": "2027-06-30"}, [], 8, 4, pct=100,
         desc="Instrumentación, PLC y calibración."),
    prov("S13", "Eléctrica Cardón", "Rawson", {"ELE-MT": 1500, "ELE-INS": 300},
         {"ISO-9001": "2027-02-28", "ISO-45001": "2027-02-28"}, [], 10, 3, pct=86,
         desc="Instalaciones eléctricas industriales."),
    # --- Logística y servicios -----------------------------------------------------
    prov("S14", "Transportes Quebrada Linda", "Iglesia", {"LOG-PER": 60, "LOG-CAR": 50},
         {"ISO-45001": "2027-10-31"}, ["minibus", "camioneta_4x4"], 22, 9, pct=95,
         repromin=True, desc="Transporte de personal y cargas livianas a campamentos."),
    prov("S15", "Catering Huerta Andina", "Jáchal", {"SRV-CAT": 18000},
         {"HAB-BROM": "2027-04-30", "ISO-9001": "2027-04-30"}, [], 30, 5, pct=97,
         desc="Catering y comedores para campamentos."),
    prov("S16", "Viandas del Valle", "9 de Julio", {"SRV-CAT": 6000},
         {"HAB-BROM": "2027-01-31"}, [], 10, 1, trib=False, pct=100,
         desc="Viandas. Tributa en otra jurisdicción."),
    prov("S17", "Recuperadora Tamarisco", "Chimbas", {"AMB-RES": 20},
         {"ISO-14001": "2027-06-30"}, ["camion_volcador"], 8, 2, pct=88,
         desc="Recolección y reciclaje de residuos no peligrosos."),
    prov("S18", "Suministros Cactus SRL", "Pocito", {"SEG-EPP": 5000},
         {"ISO-9001": "2027-05-31"}, [], 6, 4, pct=90, desc="Provisión de EPP y ropa de trabajo."),
    prov("S23", "Limpiezas Industriales Totora", "Chimbas", {"SRV-LIM": 3000},
         {"ISO-45001": "2027-03-31"}, [], 40, 3, pct=94, desc="Limpieza industrial y de campamentos."),
    # --- Ambiente y laboratorio ------------------------------------------------------
    prov("S19", "Laboratorio Analítico Lagunas", "Capital", {"AMB-LAB": 400},
         {"ISO-17025": "2027-05-31", "ISO-9001": "2027-05-31"}, [], 12, 6, pct=92,
         desc="Análisis de aguas y suelos."),
    prov("S20", "Monitoreos Ambientales Jarillal", "Rivadavia", {"AMB-MON": 6},
         {"ISO-14001": "2027-08-31"}, ["laboratorio_movil", "camioneta_4x4"], 7, 4, pct=100,
         desc="Monitoreo de material particulado y ruido."),
    prov("S21", "Fletes Travesía SRL", "Caucete", {"LOG-CAR": 100},
         {"ISO-45001": "2027-02-28"}, ["camion_volcador"], 25, 7, pct=89,
         desc="Transporte de carga general."),
    prov("S22", "Combustibles y Logística Salitral", "25 de Mayo", {"LOG-PEL": 15},
         {"HAB-PEL": "2027-07-31", "ISO-45001": "2027-07-31"}, ["camion_cisterna"], 12, 5,
         pct=90, desc="Transporte de combustibles."),
    # --- No locales (otras provincias) ---------------------------------------------
    prov("N01", "Mantenimientos Industriales del Centro SA", "Capital", {"MET-MEC": 8000},
         {"ISO-9001": "2027-12-31", "ISO-45001": "2027-12-31"}, ["camioneta_4x4"], 60, 15,
         provincia="Córdoba", **NO_LOCAL, desc="Mantenimiento de molinos y chancadores."),
    prov("N02", "Obras Andinas SA", "Godoy Cruz", {"CIV-MOV": 60000, "CIV-HOR": 3000},
         {"ISO-9001": "2027-12-31", "ISO-45001": "2027-12-31"},
         ["retroexcavadora", "camion_volcador", "hormigonera"], 80, 12,
         provincia="Mendoza", **NO_LOCAL, desc="Constructora de obras civiles mineras."),
    prov("N03", "Gestión Ambiental Cuyana SA", "Luján de Cuyo", {"AMB-RES": 50},
         {"REG-RES": "2027-06-30", "ISO-14001": "2027-06-30"}, ["camion_volcador"], 25, 10,
         provincia="Mendoza", **NO_LOCAL, desc="Transporte y tratamiento de residuos peligrosos."),
    prov("N04", "Transportes Pampeanos SA", "Campana", {"LOG-PEL": 100, "LOG-CAR": 300},
         {"HAB-PEL": "2027-12-31", "ISO-45001": "2027-12-31"}, ["camion_cisterna"], 150, 20,
         provincia="Buenos Aires", **NO_LOCAL, desc="Logística de cargas peligrosas."),
]


def item(id, paquete, desc, rubro, cant, monto, excl=(), des=(), maq=(), dot=0, exp=0):
    return {
        "id": id, "paquete": paquete, "descripcion": desc, "rubro": rubro,
        "cantidad_mensual": cant, "monto_estimado_usd": monto,
        "certificaciones_excluyentes": list(excl), "certificaciones_deseables": list(des),
        "maquinaria_requerida": list(maq), "dotacion_minima": dot, "experiencia_minima_anios": exp,
    }


A = "Nave de mantenimiento: obra civil y estructura"
B = "Electricidad e instrumentación de planta"
C = "Servicios al campamento"
D = "Mantenimiento de molinos"
E = "Provisión de EPP"

PLIEGOS = [
    {
        "id": "P001",
        "titulo": "Ampliación de planta — Proyecto Demo Quebrada Norte [FICTICIO]",
        "comprador": "Minera Demo Quebrada Norte SA [FICTICIA]",
        "ficticio": True,
        "descripcion": "Pliego ficticio armado para la demostración. Los paquetes imitan la "
                       "práctica de publicar lotes grandes que dejan afuera a las PyMEs.",
        "fecha_referencia": "2026-11-15",
        "items": [
            item("I1", A, "Movimiento de suelos para plataformas", "CIV-MOV", 25000, 900_000,
                 excl=["ISO-45001"], maq=["retroexcavadora", "camion_volcador"], dot=12, exp=2),
            item("I2", A, "Fundaciones de hormigón", "CIV-HOR", 1200, 700_000,
                 excl=["ISO-9001"], maq=["hormigonera"], dot=15, exp=3),
            item("I3", A, "Fabricación y montaje de estructura metálica", "MET-FAB", 120, 1_800_000,
                 excl=["ISO-9001", "SEG-ALT"], des=["ISO-45001"],
                 maq=["grua", "equipo_soldadura"], dot=20, exp=3),
            item("I4", B, "Montaje eléctrico de tableros y cableado", "ELE-MT", 3000, 600_000,
                 excl=["ISO-45001"], dot=15, exp=2),
            item("I5", B, "Instrumentación y calibración", "ELE-INS", 800, 250_000,
                 excl=["ISO-9001"], dot=5, exp=2),
            item("I6", C, "Transporte de personal al campamento", "LOG-PER", 50, 300_000,
                 excl=["ISO-45001"], maq=["minibus"], dot=10, exp=2),
            item("I7", C, "Catering del campamento", "SRV-CAT", 15000, 450_000,
                 excl=["HAB-BROM"], dot=12, exp=1),
            item("I8", C, "Gestión de residuos peligrosos", "AMB-RES", 15, 150_000,
                 excl=["REG-RES"], maq=["camion_volcador"], dot=4, exp=2),
            item("I9", D, "Mantenimiento de molinos y chancadores", "MET-MEC", 6000, 1_400_000,
                 excl=["ISO-9001", "ISO-45001"], dot=30, exp=8),
            item("I10", E, "Provisión de EPP", "SEG-EPP", 2000, 120_000, excl=["ISO-9001"]),
        ],
    },
    {
        "id": "P002",
        "titulo": "Servicios ambientales y logísticos — Operación Demo Valle Alto [FICTICIO]",
        "comprador": "Minera Demo Valle Alto SA [FICTICIA]",
        "ficticio": True,
        "descripcion": "Segundo pliego ficticio, más chico, para probar la plataforma.",
        "fecha_referencia": "2026-11-15",
        "items": [
            item("I1", "Monitoreo ambiental integral", "Análisis de agua y suelos", "AMB-LAB",
                 300, 180_000, excl=["ISO-17025"], dot=4, exp=3),
            item("I2", "Monitoreo ambiental integral", "Campañas de monitoreo de aire y ruido",
                 "AMB-MON", 4, 120_000, excl=["ISO-14001"],
                 maq=["laboratorio_movil", "camioneta_4x4"], dot=3, exp=2),
            item("I3", "Logística de insumos", "Transporte de carga general", "LOG-CAR", 80,
                 400_000, excl=["ISO-45001"], dot=10, exp=3),
            item("I4", "Logística de insumos", "Transporte de combustibles", "LOG-PEL", 30,
                 350_000, excl=["HAB-PEL", "ISO-45001"], maq=["camion_cisterna"], dot=6, exp=3),
        ],
    },
]


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    for nombre, datos in (("proveedores.json", PROVEEDORES), ("pliegos.json", PLIEGOS)):
        (DATA / nombre).write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", "utf-8")
        print(f"✔ {nombre}: {len(datos)} registros")


if __name__ == "__main__":
    main()
