from datetime import date

import pytest

from app.core.scoring import PESOS_DEFAULT, evaluar, rankear, validar_pesos

from .conftest import FECHA, hacer_item, hacer_lote, hacer_proveedor


def test_proveedor_que_cumple_todo_saca_100_y_es_apto():
    lote = hacer_lote(hacer_item("I1", "MET-FAB", 30, certificaciones_excluyentes=["ISO-9001"],
                                 maquinaria_requerida=["grua"], dotacion_minima=10,
                                 experiencia_minima_anios=3))
    p = hacer_proveedor("A", {"MET-FAB": 40}, {"ISO-9001": None}, ["grua"], dotacion=12, experiencia=5)
    ev = evaluar(p, lote, FECHA)
    assert ev.apto
    assert ev.puntaje_total == pytest.approx(100.0)
    assert ev.motivos_no_apto == []


def test_el_puntaje_es_la_suma_de_los_aportes_de_cada_criterio():
    lote = hacer_lote(hacer_item("I1", "MET-FAB", 30, certificaciones_excluyentes=["ISO-9001"]))
    ev = evaluar(hacer_proveedor("A", {"MET-FAB": 15}), lote, FECHA)
    assert ev.puntaje_total == pytest.approx(sum(c.aporte for c in ev.criterios), abs=0.05)
    assert {c.criterio for c in ev.criterios} == set(PESOS_DEFAULT)


def test_certificacion_excluyente_vencida_lo_vuelve_no_apto_y_lo_explica():
    lote = hacer_lote(hacer_item("I1", "MET-FAB", 10, certificaciones_excluyentes=["ISO-9001"]))
    p = hacer_proveedor("A", {"MET-FAB": 40}, {"ISO-9001": date(2026, 1, 1)})
    ev = evaluar(p, lote, FECHA)
    assert not ev.apto
    certs = next(c for c in ev.criterios if c.criterio == "certificaciones")
    assert any("vencida" in f for f in certs.faltantes)


def test_capacidad_insuficiente_baja_el_puntaje_proporcionalmente():
    lote = hacer_lote(hacer_item("I1", "MET-FAB", 40))
    ev = evaluar(hacer_proveedor("A", {"MET-FAB": 10}), lote, FECHA)
    cap = next(c for c in ev.criterios if c.criterio == "capacidad")
    assert cap.puntaje == pytest.approx(0.25)
    assert not ev.apto


def test_desempate_prefiere_apto_luego_puntaje_luego_local():
    lote = hacer_lote(hacer_item("I1", "MET-FAB", 10))
    no_local = hacer_proveedor("A", {"MET-FAB": 10}, local=False)
    local = hacer_proveedor("B", {"MET-FAB": 10}, local=True)
    ranking = rankear([no_local, local], lote, FECHA)
    assert [e.proveedor_id for e in ranking] == ["B", "A"]


def test_pesos_invalidos_se_rechazan():
    with pytest.raises(ValueError):
        validar_pesos({**PESOS_DEFAULT, "capacidad": 0.5})
    with pytest.raises(ValueError):
        validar_pesos({"capacidad": 1.0})
