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


# --- Altas de pliego y proveedor (issue #6) ----------------------------------------------
# Usan un servicio propio para no ensuciar los datos que ven los demás tests.

from app.api.servicio import Servicio, obtener_servicio  # noqa: E402


@pytest.fixture
def cliente_aislado():
    svc = Servicio()
    app.dependency_overrides[obtener_servicio] = lambda: svc
    yield TestClient(app)
    app.dependency_overrides.clear()


def pliego_minimo(id_: str = "PT1", **item_extra) -> dict:
    item = {
        "id": "I1",
        "paquete": "Campamento",
        "descripcion": "Comedor",
        "rubro": "SRV-CAT",
        "cantidad_mensual": 5000,
        "monto_estimado_usd": 100000,
        **item_extra,
    }
    return {
        "id": id_,
        "titulo": "Pliego de prueba",
        "comprador": "Minera de prueba",
        "fecha_referencia": "2026-11-15",
        "items": [item],
    }


def proveedor_minimo(id_: str = "ST1", **extra) -> dict:
    return {
        "id": id_,
        "razon_social": "Catering de prueba",
        "departamento": "Capital",
        "capacidades": [{"rubro": "SRV-CAT", "capacidad_mensual": 8000}],
        "dotacion": 25,
        "anios_experiencia_minera": 4,
        "arraigo": {
            "domicilio_operativo_sj": True,
            "tributa_en_sj": True,
            "porcentaje_personal_sanjuanino": 90,
        },
        **extra,
    }


def test_alta_de_pliego_queda_rotulada_y_se_puede_analizar(cliente_aislado):
    r = cliente_aislado.post("/api/pliegos", json=pliego_minimo() | {"ficticio": False})
    assert r.status_code == 201
    creado = r.json()
    assert creado["ficticio"] is True and creado["titulo"].endswith("[FICTICIO]")
    r = cliente_aislado.get("/api/pliegos/PT1/analisis")
    assert r.status_code == 200 and r.json()["lotes"]


def test_alta_de_pliego_con_id_duplicado_da_409(cliente_aislado):
    assert cliente_aislado.post("/api/pliegos", json=pliego_minimo()).status_code == 201
    assert cliente_aislado.post("/api/pliegos", json=pliego_minimo()).status_code == 409


def test_alta_de_pliego_con_rubro_inexistente_da_422(cliente_aislado):
    r = cliente_aislado.post("/api/pliegos", json=pliego_minimo(rubro="NO-EXISTE"))
    assert r.status_code == 422


def test_alta_de_pliego_con_certificacion_inexistente_da_422(cliente_aislado):
    r = cliente_aislado.post(
        "/api/pliegos", json=pliego_minimo(certificaciones_excluyentes=["ISO-0000"])
    )
    assert r.status_code == 422


def test_alta_de_proveedor_queda_rotulada_y_entra_al_analisis(cliente_aislado):
    assert cliente_aislado.post("/api/pliegos", json=pliego_minimo()).status_code == 201
    r = cliente_aislado.post("/api/proveedores", json=proveedor_minimo(ficticio=False))
    assert r.status_code == 201
    creado = r.json()
    assert creado["ficticio"] is True and creado["razon_social"].endswith("[DEMO]")
    analisis = cliente_aislado.get("/api/pliegos/PT1/analisis").json()
    ids = {e["proveedor_id"] for lote in analisis["lotes"] for e in lote["ranking"]}
    assert "ST1" in ids


def test_alta_de_proveedor_duplicado_da_409(cliente_aislado):
    assert cliente_aislado.post("/api/proveedores", json=proveedor_minimo()).status_code == 201
    assert cliente_aislado.post("/api/proveedores", json=proveedor_minimo()).status_code == 409


def test_alta_de_proveedor_con_maquinaria_inexistente_da_422(cliente_aislado):
    r = cliente_aislado.post("/api/proveedores", json=proveedor_minimo(maquinaria=["nave_espacial"]))
    assert r.status_code == 422
