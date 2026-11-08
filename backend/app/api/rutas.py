from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from ..core.alianzas import sugerir_utes
from ..core.lotes import sugerir_lotes
from ..core.modelos import (
    AnalisisLote,
    AnalisisPliego,
    ChecklistPreparacion,
    Lote,
    Pliego,
    Proveedor,
)
from ..core.preparacion import borrador_carta_intencion, checklist
from ..core.scoring import PESOS_DEFAULT, validar_pesos
from ..core.sugeridor import Sugerencia, crear_sugeridor
from ..core.taxonomia import CERTIFICACIONES, FAMILIAS, MAQUINARIA, RUBROS
from .servicio import NoEncontrado, Servicio, obtener_servicio

router = APIRouter(prefix="/api")
Svc = Annotated[Servicio, Depends(obtener_servicio)]
_sugeridor = crear_sugeridor()


def _404(e: NoEncontrado) -> HTTPException:
    return HTTPException(status_code=404, detail=str(e))


# --- Sistema y transparencia -------------------------------------------------------


@router.get("/salud", tags=["sistema"])
def salud() -> dict[str, str]:
    return {"estado": "ok", "sugeridor": _sugeridor.nombre}


@router.get("/taxonomia", tags=["transparencia"])
def taxonomia() -> dict:
    return {
        "familias": FAMILIAS,
        "rubros": [
            {"codigo": r.codigo, "nombre": r.nombre, "familia": r.familia, "unidad": r.unidad}
            for r in RUBROS.values()
        ],
        "certificaciones": CERTIFICACIONES,
        "maquinaria": MAQUINARIA,
    }


@router.get("/pesos", tags=["transparencia"])
def pesos() -> dict[str, float]:
    """Pesos públicos del scoring. Cualquiera puede ver cómo se calcula el puntaje."""
    return PESOS_DEFAULT


# --- Proveedores ---------------------------------------------------------------------


@router.get("/proveedores", response_model=list[Proveedor], tags=["proveedores"])
def listar_proveedores(
    svc: Svc,
    rubro: str | None = None,
    solo_locales: bool = False,
) -> list[Proveedor]:
    out = svc.repo.proveedores()
    if rubro:
        out = [p for p in out if p.capacidad(rubro) > 0]
    if solo_locales:
        out = [p for p in out if p.es_local]
    return out


@router.get("/proveedores/{proveedor_id}", response_model=Proveedor, tags=["proveedores"])
def ver_proveedor(proveedor_id: str, svc: Svc) -> Proveedor:
    try:
        return svc.proveedor(proveedor_id)
    except NoEncontrado as e:
        raise _404(e) from e


@router.post("/proveedores", response_model=Proveedor, status_code=201, tags=["proveedores"])
def crear_proveedor(proveedor: Proveedor, svc: Svc) -> Proveedor:
    if svc.repo.proveedor(proveedor.id):
        raise HTTPException(status_code=409, detail=f"Ya existe el proveedor {proveedor.id}")
    return svc.guardar_proveedor(proveedor)


# --- Pliegos y análisis ----------------------------------------------------------------


@router.get("/pliegos", response_model=list[Pliego], tags=["pliegos"])
def listar_pliegos(svc: Svc) -> list[Pliego]:
    return svc.repo.pliegos()


@router.get("/pliegos/{pliego_id}", response_model=Pliego, tags=["pliegos"])
def ver_pliego(pliego_id: str, svc: Svc) -> Pliego:
    try:
        return svc.pliego(pliego_id)
    except NoEncontrado as e:
        raise _404(e) from e


@router.post("/pliegos", response_model=Pliego, status_code=201, tags=["pliegos"])
def crear_pliego(pliego: Pliego, svc: Svc) -> Pliego:
    if svc.repo.pliego(pliego.id):
        raise HTTPException(status_code=409, detail=f"Ya existe el pliego {pliego.id}")
    return svc.guardar_pliego(pliego)


@router.get("/pliegos/{pliego_id}/lotes", response_model=list[Lote], tags=["análisis"])
def lotes_sugeridos(pliego_id: str, svc: Svc) -> list[Lote]:
    try:
        return sugerir_lotes(svc.pliego(pliego_id), svc.repo.proveedores())
    except NoEncontrado as e:
        raise _404(e) from e


@router.get("/pliegos/{pliego_id}/analisis", response_model=AnalisisPliego, tags=["análisis"])
def analisis(pliego_id: str, svc: Svc) -> AnalisisPliego:
    try:
        return svc.analisis(pliego_id)
    except NoEncontrado as e:
        raise _404(e) from e


class PedidoPesos(BaseModel):
    pesos: dict[str, float]


@router.post("/pliegos/{pliego_id}/analisis", response_model=AnalisisPliego, tags=["análisis"])
def analisis_con_pesos(pliego_id: str, pedido: PedidoPesos, svc: Svc) -> AnalisisPliego:
    """Permite a la minera probar otros pesos y ver cómo cambia el ranking."""
    try:
        validar_pesos(pedido.pesos)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    try:
        return svc.analisis(pliego_id, pedido.pesos)
    except NoEncontrado as e:
        raise _404(e) from e


@router.get(
    "/pliegos/{pliego_id}/lotes/{lote_id}",
    response_model=AnalisisLote,
    tags=["análisis"],
)
def analisis_lote(pliego_id: str, lote_id: str, svc: Svc) -> AnalisisLote:
    try:
        return svc.analisis_lote(pliego_id, lote_id)
    except NoEncontrado as e:
        raise _404(e) from e


@router.get(
    "/pliegos/{pliego_id}/lotes/{lote_id}/preparacion/{proveedor_id}",
    response_model=ChecklistPreparacion,
    tags=["preparación para homologación"],
)
def preparacion(pliego_id: str, lote_id: str, proveedor_id: str, svc: Svc) -> ChecklistPreparacion:
    """Si el proveedor integra la UTE recomendada, lo que aportan sus socios se marca cubierto."""
    try:
        a = svc.analisis_lote(pliego_id, lote_id)
        socios = (
            [svc.proveedor(i) for i in a.recomendada.proveedor_ids]
            if a.recomendada.tipo == "ute_local" and proveedor_id in a.recomendada.proveedor_ids
            else None
        )
        return checklist(
            svc.proveedor(proveedor_id), a.lote, svc.pliego(pliego_id).fecha_referencia, socios
        )
    except NoEncontrado as e:
        raise _404(e) from e


@router.get(
    "/pliegos/{pliego_id}/lotes/{lote_id}/carta-ute",
    response_class=PlainTextResponse,
    tags=["preparación para homologación"],
)
def carta_ute(
    pliego_id: str,
    lote_id: str,
    svc: Svc,
    socios: Annotated[str, Query(description="Ids separados por coma, p. ej. S08,S09")],
) -> str:
    """Borrador (Markdown) de carta de intención para una de las UTEs sugeridas."""
    try:
        pliego = svc.pliego(pliego_id)
        a = svc.analisis_lote(pliego_id, lote_id)
    except NoEncontrado as e:
        raise _404(e) from e
    pedidos = sorted(s.strip() for s in socios.split(",") if s.strip())
    for ute in a.utes:
        if sorted(s.proveedor_id for s in ute.socios) == pedidos:
            return borrador_carta_intencion(ute, a.lote, pliego)
    # También se puede pedir para una combinación que no estaba entre las sugeridas
    candidatos = [svc.repo.proveedor(i) for i in pedidos]
    if None in candidatos or len(pedidos) < 2:
        raise HTTPException(status_code=404, detail="Socios inválidos")
    utes = sugerir_utes(a.lote, [c for c in candidatos if c], pliego.fecha_referencia, solo_locales=False)
    for ute in utes:
        if sorted(s.proveedor_id for s in ute.socios) == pedidos:
            return borrador_carta_intencion(ute, a.lote, pliego)
    raise HTTPException(status_code=404, detail="Esa combinación no mejora la cobertura del lote")


# --- Sugeridor de rubros ---------------------------------------------------------------------


class PedidoSugerencia(BaseModel):
    texto: str = Field(min_length=3, max_length=2000)
    k: int = Field(default=3, ge=1, le=10)


@router.post("/sugerir-rubros", response_model=list[Sugerencia], tags=["IA asistiva"])
def sugerir_rubros(pedido: PedidoSugerencia) -> list[Sugerencia]:
    """Sugiere rubros a partir de texto libre. SOLO sugiere: una persona confirma."""
    return _sugeridor.sugerir(pedido.texto, pedido.k)
