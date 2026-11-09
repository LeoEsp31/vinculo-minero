from app.core.alianzas import matriz_cobertura, perfil_combinado, sugerir_utes

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


def test_matriz_de_cobertura_muestra_que_aporta_cada_socio():
    e = hacer_proveedor("E", {"ELE-MT": 3500}, {"ISO-45001": None}, experiencia=6)
    i = hacer_proveedor("I", {"ELE-INS": 1000}, {"ISO-9001": None}, experiencia=4)
    lote = lote_electrico()
    matriz = matriz_cobertura([e, i], lote, FECHA)
    por_req = {f.requisito: f for f in matriz}
    mt = por_req["Montaje eléctrico de media y baja tensión"]
    assert mt.cubierto and [c.aporta for c in mt.celdas] == [True, False]
    assert all(f.cubierto for f in matriz)
    # viene incluida en cada propuesta
    (ute,) = sugerir_utes(lote, [e, i], FECHA)
    assert ute.matriz == matriz


def test_matriz_marca_requisito_no_cubierto_por_el_grupo():
    a = hacer_proveedor("A", {"MET-MEC": 2000}, experiencia=6)
    b = hacer_proveedor("B", {"MET-MEC": 2000}, experiencia=4)
    lote = hacer_lote(hacer_item("I1", "MET-MEC", 3000, experiencia_minima_anios=8))
    filas = {f.tipo: f for f in matriz_cobertura([a, b], lote, FECHA)}
    assert filas["rubro"].cubierto  # 2000 + 2000 >= 3000
    assert not filas["experiencia"].cubierto  # nadie llega a 8 años
