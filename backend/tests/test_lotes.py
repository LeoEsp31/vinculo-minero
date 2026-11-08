import pytest

from app.core.lotes import paquetes_originales, percentil, sugerir_lotes

from .conftest import hacer_item, hacer_pliego, hacer_proveedor


def test_percentil_interpola_linealmente():
    assert percentil([15, 20, 25, 30, 40], 0.75) == 30
    assert percentil([2000, 2500, 3500], 0.75) == 3000
    assert percentil([7], 0.75) == 7


def test_item_con_volumen_mayor_a_cualquier_pyme_local_se_divide():
    pliego = hacer_pliego(hacer_item("I1", "MET-FAB", 120, monto=1200, paquete="P"))
    provs = [hacer_proveedor(i, {"MET-FAB": c}) for i, c in [("A", 15), ("B", 20), ("C", 25), ("D", 30), ("E", 40)]]
    lotes = sugerir_lotes(pliego, provs)
    assert len(lotes) == 4
    assert all(lote.items[0].cantidad_mensual == 30 for lote in lotes)
    assert sum(lote.monto_usd for lote in lotes) == pytest.approx(1200)
    assert "percentil 75" in lotes[0].motivo


def test_item_sin_oferta_local_se_separa_y_no_bloquea_el_paquete():
    pliego = hacer_pliego(
        hacer_item("I1", "CIV-MOV", 100, paquete="Obra"),
        hacer_item("I2", "AMB-RES", 5, paquete="Obra", certificaciones_excluyentes=["REG-RES"]),
    )
    provs = [
        hacer_proveedor("A", {"CIV-MOV": 500}),
        hacer_proveedor("B", {"AMB-RES": 50}),  # local pero sin REG-RES
        hacer_proveedor("Z", {"AMB-RES": 50}, {"REG-RES": None}, local=False),
    ]
    lotes = sugerir_lotes(pliego, provs)
    assert len(lotes) == 2
    separado = next(lote for lote in lotes if lote.items[0].id == "I2")
    assert "ninguna PyME local" in separado.motivo
    resto = next(lote for lote in lotes if lote.items[0].id == "I1")
    assert resto.nombre == "Obra"


def test_paquete_abordable_se_mantiene_igual():
    pliego = hacer_pliego(hacer_item("I1", "ELE-MT", 100, paquete="Elec"), hacer_item("I2", "ELE-INS", 10, paquete="Elec"))
    provs = [hacer_proveedor("A", {"ELE-MT": 200}), hacer_proveedor("B", {"ELE-INS": 50})]
    lotes = sugerir_lotes(pliego, provs)
    assert len(lotes) == 1 and len(lotes[0].items) == 2
    assert "UTE" in lotes[0].motivo
    assert len(paquetes_originales(pliego)) == 1
