from __future__ import annotations

from datetime import date

import pytest

from app.core.modelos import (
    Arraigo,
    CapacidadRubro,
    Certificacion,
    ItemPliego,
    Lote,
    Pliego,
    Proveedor,
)
from app.core.repositorio import RepositorioMemoria

FECHA = date(2026, 11, 15)


def hacer_proveedor(
    id: str,
    caps: dict[str, float],
    certs: dict[str, date | None] | None = None,
    maq: list[str] | None = None,
    dotacion: int = 10,
    experiencia: int = 5,
    local: bool = True,
) -> Proveedor:
    return Proveedor(
        id=id,
        razon_social=f"Proveedor {id}",
        departamento="Capital",
        capacidades=[CapacidadRubro(rubro=r, capacidad_mensual=c) for r, c in caps.items()],
        certificaciones=[Certificacion(codigo=c, vence=v) for c, v in (certs or {}).items()],
        maquinaria=maq or [],
        dotacion=dotacion,
        anios_experiencia_minera=experiencia,
        arraigo=Arraigo(
            domicilio_operativo_sj=local,
            tributa_en_sj=local,
            porcentaje_personal_sanjuanino=90 if local else 10,
        ),
    )


def hacer_item(id: str, rubro: str, cantidad: float, monto: float = 100.0, paquete: str = "", **kw) -> ItemPliego:
    return ItemPliego(
        id=id, paquete=paquete, descripcion=f"Ítem {id}", rubro=rubro,
        cantidad_mensual=cantidad, monto_estimado_usd=monto, **kw,
    )


def hacer_lote(*items: ItemPliego) -> Lote:
    return Lote(id="L1", nombre="Lote de prueba", items=list(items), motivo="test")


def hacer_pliego(*items: ItemPliego) -> Pliego:
    return Pliego(id="PX", titulo="Pliego de prueba", comprador="Test", fecha_referencia=FECHA, items=list(items))


@pytest.fixture(scope="session")
def repo() -> RepositorioMemoria:
    return RepositorioMemoria()
