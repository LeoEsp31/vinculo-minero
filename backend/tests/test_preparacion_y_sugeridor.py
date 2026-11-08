from app.core.alianzas import sugerir_utes
from app.core.modelos import AVISO_HOMOLOGACION
from app.core.preparacion import borrador_carta_intencion, checklist
from app.core.sugeridor import SugeridorPalabrasClave, normalizar

from .conftest import FECHA, hacer_item, hacer_lote, hacer_pliego, hacer_proveedor


def test_checklist_marca_pendientes_y_nunca_dice_que_homologa():
    lote = hacer_lote(hacer_item("I1", "MET-FAB", 30, certificaciones_excluyentes=["ISO-9001"],
                                 maquinaria_requerida=["grua"]))
    p = hacer_proveedor("A", {"MET-FAB": 20})
    c = checklist(p, lote, FECHA)
    pendientes = [i.requisito for i in c.items if not i.cumple]
    assert any("ISO 9001" in r for r in pendientes)
    assert any("Grúa" in r for r in pendientes)
    assert any("Repromin" in r for r in pendientes)
    assert c.pendientes == len(pendientes)
    assert c.aviso == AVISO_HOMOLOGACION and "no certifica" in c.aviso


def test_en_una_ute_lo_que_aporta_el_socio_figura_como_cubierto():
    lote = hacer_lote(
        hacer_item("I1", "CIV-MOV", 100, maquinaria_requerida=["retroexcavadora"]),
        hacer_item("I2", "CIV-HOR", 10, maquinaria_requerida=["hormigonera"]),
    )
    suelos = hacer_proveedor("S", {"CIV-MOV": 200}, maq=["retroexcavadora"])
    hormigon = hacer_proveedor("H", {"CIV-HOR": 20}, maq=["hormigonera"])
    solo = checklist(hormigon, lote, FECHA)
    en_ute = checklist(hormigon, lote, FECHA, socios=[suelos, hormigon])
    retro = next(i for i in en_ute.items if i.requisito == "Retroexcavadora")
    assert retro.cumple and retro.cubierto_por == "Proveedor S"
    assert en_ute.pendientes == solo.pendientes - 1


def test_borrador_de_carta_incluye_socios_y_aviso():
    item1 = hacer_item("I1", "ELE-MT", 100, certificaciones_excluyentes=["ISO-45001"])
    item2 = hacer_item("I2", "ELE-INS", 10)
    lote = hacer_lote(item1, item2)
    utes = sugerir_utes(lote, [hacer_proveedor("E", {"ELE-MT": 200}, {"ISO-45001": None}),
                               hacer_proveedor("I", {"ELE-INS": 20})], FECHA)
    texto = borrador_carta_intencion(utes[0], lote, hacer_pliego(item1, item2))
    assert "BORRADOR" in texto and "Proveedor E" in texto and "Proveedor I" in texto
    assert AVISO_HOMOLOGACION in texto


def test_normalizar_quita_tildes_y_signos():
    assert normalizar("Instrumentación, PLC y Calibración!") == "instrumentacion plc y calibracion"


def test_sugeridor_por_palabras_clave_es_explicable():
    s = SugeridorPalabrasClave().sugerir("Hacemos soldadura y montaje de estructuras de acero")
    assert s[0].rubro == "MET-FAB"
    assert "soldadura" in s[0].evidencia


def test_sugeridor_sin_coincidencias_devuelve_vacio():
    assert SugeridorPalabrasClave().sugerir("venta de flores") == []
