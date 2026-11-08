"""Tests de la API. Requieren fastapi + httpx (extra [dev])."""

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

cliente = TestClient(app)


def test_salud():
    r = cliente.get("/api/salud")
    assert r.status_code == 200 and r.json()["estado"] == "ok"


def test_pesos_son_publicos_y_suman_uno():
    pesos = cliente.get("/api/pesos").json()
    assert abs(sum(pesos.values()) - 1) < 1e-9


def test_analisis_de_pliego_demo():
    r = cliente.get("/api/pliegos/P001/analisis")
    assert r.status_code == 200
    data = r.json()
    assert data["reporte"]["porcentaje_local_sj"] > data["reporte"]["linea_base_local_sj_pct"]
    assert all("explicacion" in lote["recomendada"] for lote in data["lotes"])


def test_pliego_inexistente_da_404():
    assert cliente.get("/api/pliegos/NOPE/analisis").status_code == 404


def test_pesos_invalidos_dan_422():
    r = cliente.post("/api/pliegos/P001/analisis", json={"pesos": {"capacidad": 1.0}})
    assert r.status_code == 422


def test_preparacion_y_carta_ute():
    analisis = cliente.get("/api/pliegos/P001/analisis").json()
    lote = next(a for a in analisis["lotes"] if a["recomendada"]["tipo"] == "ute_local")
    socios = lote["recomendada"]["proveedor_ids"]
    r = cliente.get(f"/api/pliegos/P001/lotes/{lote['lote']['id']}/preparacion/{socios[0]}")
    assert r.status_code == 200 and "no certifica" in r.json()["aviso"]
    r = cliente.get(f"/api/pliegos/P001/lotes/{lote['lote']['id']}/carta-ute", params={"socios": ",".join(socios)})
    assert r.status_code == 200 and "BORRADOR" in r.text


def test_sugerir_rubros():
    r = cliente.post("/api/sugerir-rubros", json={"texto": "catering y viandas para campamentos"})
    assert r.status_code == 200 and r.json()[0]["rubro"] == "SRV-CAT"
