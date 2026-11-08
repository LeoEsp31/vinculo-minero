from app.core.alianzas import perfil_combinado, sugerir_utes

from .conftest import FECHA, hacer_item, hacer_lote, hacer_proveedor


def lote_electrico():
    return hacer_lote(
        hacer_item("I1", "ELE-MT", 3000, monto=600, certificaciones_excluyentes=["ISO-45001"]),
        hacer_item("I2", "ELE-INS", 800, monto=250, certificaciones_excluyentes=["ISO-9001"]),
    )


def test_encuentra_la_ute_complementaria_y_explica_que_aporta_cada_socio():
    electrica = hacer_proveedor("E", {"ELE-MT": 3500}, {"ISO-45001": None})
    instrumentacion = hacer_proveedor("I", {"ELE-INS": 1000}, {"ISO-9001": None})
    utes = sugerir_utes(lote_electrico(), [electrica, instrumentacion], FECHA)
    assert len(utes) == 1
    ute = utes[0]
    assert ute.evaluacion.apto
    assert {s.proveedor_id for s in ute.socios} == {"E", "I"}
    aportes = {s.proveedor_id: s.aporte_unico for s in ute.socios}
    assert any("ELE-MT" in a for a in aportes["E"])
    assert any("ELE-INS" in a for a in aportes["I"])


def test_descarta_socios_redundantes():
    e = hacer_proveedor("E", {"ELE-MT": 3500}, {"ISO-45001": None})
    i = hacer_proveedor("I", {"ELE-INS": 1000}, {"ISO-9001": None})
    sobra = hacer_proveedor("X", {"ELE-MT": 100})
    utes = sugerir_utes(lote_electrico(), [e, i, sobra], FECHA)
    assert all(len(u.socios) == 2 for u in utes if u.evaluacion.apto)


def test_por_defecto_solo_arma_utes_con_pymes_locales():
    e = hacer_proveedor("E", {"ELE-MT": 3500}, {"ISO-45001": None}, local=False)
    i = hacer_proveedor("I", {"ELE-INS": 1000}, {"ISO-9001": None})
    assert sugerir_utes(lote_electrico(), [e, i], FECHA) == []


def test_perfil_combinado_suma_capacidades_y_une_certificaciones():
    a = hacer_proveedor("A", {"MET-FAB": 10}, {"ISO-9001": None}, ["grua"], dotacion=5, experiencia=2)
    b = hacer_proveedor("B", {"MET-FAB": 15}, {"SEG-ALT": None}, dotacion=7, experiencia=6)
    combo = perfil_combinado([a, b], FECHA)
    assert combo.capacidad("MET-FAB") == 25
    assert combo.certificaciones_vigentes(FECHA) == {"ISO-9001", "SEG-ALT"}
    assert combo.dotacion == 12 and combo.anios_experiencia_minera == 6
