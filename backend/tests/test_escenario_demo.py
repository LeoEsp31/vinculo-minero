"""Tests sobre los datos de demostración: protegen la demo del pitch.

Si alguien cambia el motor o los datos y la historia de la demo se rompe,
estos tests fallan en CI antes de que nos enteremos en vivo frente al jurado.
"""

import pytest

from app.core.analisis import analizar_pliego


@pytest.fixture(scope="module")
def p001(repo):
    return analizar_pliego(repo.pliego("P001"), repo.proveedores())


def test_todos_los_datos_demo_son_ficticios_y_estan_rotulados(repo):
    for p in repo.proveedores():
        assert p.ficticio and "[DEMO]" in p.razon_social
    for p in repo.pliegos():
        assert p.ficticio and "[FICTICIO]" in p.titulo


def test_la_plataforma_mejora_la_participacion_local(p001):
    r = p001.reporte
    assert r.linea_base_local_sj_pct < 10
    assert r.porcentaje_local_sj > r.meta_provincial_pct
    assert r.advertencias  # el reporte siempre aclara que es orientativo


def test_los_lotes_conservan_el_monto_total_del_pliego(repo, p001):
    total_pliego = sum(i.monto_estimado_usd for i in repo.pliego("P001").items)
    assert p001.reporte.monto_total_usd == pytest.approx(total_pliego, abs=1)


def test_muestra_los_cuatro_desenlaces(p001):
    tipos = {a.recomendada.tipo for a in p001.lotes}
    assert {"directa_local", "ute_local", "directa_no_local"} <= tipos


def test_la_ute_de_obra_civil_es_la_esperada(p001):
    obra = next(a for a in p001.lotes if a.lote.nombre.startswith("Nave de mantenimiento"))
    assert obra.recomendada.tipo == "ute_local"
    assert sorted(obra.recomendada.proveedor_ids) == ["S08", "S09"]


def test_no_se_asigna_mas_capacidad_de_la_que_cada_pyme_tiene(repo, p001):
    asignado: dict[tuple[str, str], float] = {}
    for a in p001.lotes:
        if a.recomendada.tipo in ("directa_local", "directa_no_local"):
            (pid,) = a.recomendada.proveedor_ids
            for rubro, dem in a.lote.demanda_por_rubro().items():
                asignado[(pid, rubro)] = asignado.get((pid, rubro), 0) + dem
    for (pid, rubro), total in asignado.items():
        assert total <= repo.proveedor(pid).capacidad(rubro) + 1e-6


def test_residuos_peligrosos_se_informa_como_oportunidad(p001):
    assert any("residuos peligrosos" in o for o in p001.reporte.oportunidades_desarrollo)
