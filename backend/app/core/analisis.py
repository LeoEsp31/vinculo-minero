"""Orquesta el flujo completo sobre un pliego:

    pliego → lotes sugeridos → ranking por lote → UTEs (si hace falta)
           → opción recomendada por lote → reporte de compre local

Prioridad de la opción recomendada por lote (objetivo: maximizar compre local
sin bajar la calidad exigida, porque solo se recomiendan opciones APTAS):
    1. PyME local que cubre sola el lote
    2. UTE de PyMEs locales que cubre el lote
    3. Proveedor no local que cubre el lote
    4. Sin cobertura: se informa como oportunidad de desarrollo de proveedores
"""

from __future__ import annotations

from operator import attrgetter, methodcaller

from .alianzas import sugerir_utes
from .lotes import paquetes_originales, sugerir_lotes
from .modelos import (
    AnalisisLote,
    AnalisisPliego,
    Lote,
    OpcionRecomendada,
    Pliego,
    Proveedor,
    ReporteCupo,
)
from .scoring import PESOS_DEFAULT, rankear
from .taxonomia import CERTIFICACIONES, RUBROS

# Metas de referencia. Son parámetros: la reglamentación puede cambiarlas.
META_PROVINCIAL_PCT = 60.0  # Ley de Desarrollo Local Minero (San Juan): objetivo de compras locales
META_RIGI_PCT = 20.0  # Ley 27.742 (RIGI): plan de proveedores locales, mínimo del monto de inversión

ADVERTENCIAS_REPORTE = [
    "Estimación orientativa calculada sobre este pliego, no sobre el total de compras "
    "anuales ni sobre el monto de inversión del proyecto.",
    "La condición de proveedor local se estima con datos declarados (domicilio operativo, "
    "tributación y % de personal sanjuanino); la verificación real corresponde al Repromin.",
    "La Ley de Desarrollo Local Minero está en etapa de reglamentación: los criterios "
    "de cómputo pueden cambiar.",
    "Datos de demostración: todos los proveedores y pliegos son ficticios.",
]


def _recomendar(lote: Lote, ranking, utes) -> OpcionRecomendada:
    for ev in ranking:
        if ev.apto and ev.es_local:
            return OpcionRecomendada(
                tipo="directa_local",
                proveedor_ids=[ev.proveedor_id],
                puntaje=ev.puntaje_total,
                explicacion=f"{ev.razon_social} cubre sola todos los requisitos del lote.",
            )
    for ute in utes:
        if ute.evaluacion.apto and all(s.es_local for s in ute.socios):
            return OpcionRecomendada(
                tipo="ute_local",
                proveedor_ids=[s.proveedor_id for s in ute.socios],
                puntaje=ute.evaluacion.puntaje_total,
                explicacion="Ninguna PyME local cubre el lote sola. " + ute.explicacion,
            )
    for ev in ranking:
        if ev.apto:
            return OpcionRecomendada(
                tipo="directa_no_local",
                proveedor_ids=[ev.proveedor_id],
                puntaje=ev.puntaje_total,
                explicacion=(
                    f"Solo {ev.razon_social} (no local) cubre el lote. Hay espacio para "
                    "desarrollar proveedores locales en este rubro."
                ),
            )
    return OpcionRecomendada(
        tipo="sin_cobertura",
        proveedor_ids=[],
        puntaje=0.0,
        explicacion="Ningún proveedor ni alianza registrada cubre todos los requisitos excluyentes.",
    )


def _oportunidades(lotes: list[AnalisisLote], proveedores: list[Proveedor], fecha) -> list[str]:
    """Rubros y certificaciones pedidos que ninguna PyME local tiene."""
    locales = [p for p in proveedores if p.es_local]
    rubros_loc = {c.rubro for p in locales for c in p.capacidades}
    certs_loc = set().union(*(p.certificaciones_vigentes(fecha) for p in locales)) if locales else set()
    out: list[str] = []
    for a in lotes:
        if a.recomendada.tipo in ("directa_local", "ute_local"):
            continue
        for r in a.lote.demanda_por_rubro():
            if r not in rubros_loc:
                out.append(f"Rubro sin oferta local: {r} · {RUBROS[r].nombre}")
        for c in a.lote.certificaciones_excluyentes():
            if c not in certs_loc:
                out.append(f"Certificación que ninguna PyME local tiene vigente: {CERTIFICACIONES[c]}")
    return sorted(set(out))


def linea_base_local(
    pliego: Pliego, proveedores: list[Proveedor], pesos: dict[str, float] | None = None
) -> float:
    """Monto que PyMEs locales podrían ganar HOY, sin la plataforma: paquetes tal
    como los publica la minera y solo presentaciones individuales."""
    fecha = pliego.fecha_referencia
    monto = 0.0
    for paquete in paquetes_originales(pliego):
        ranking = rankear(proveedores, paquete, fecha, pesos)
        if any(e.apto and e.es_local for e in ranking):
            monto += paquete.monto_usd
    return monto


Uso = dict[tuple[str, str], float]  # (proveedor_id, rubro) -> capacidad ya asignada


def con_capacidad_restante(proveedores: list[Proveedor], uso: Uso) -> list[Proveedor]:
    """Copia de los proveedores con la capacidad que les queda libre."""
    out = []
    for p in proveedores:
        caps = [
            c.model_copy(update={"capacidad_mensual": c.capacidad_mensual - uso.get((p.id, c.rubro), 0.0)})
            for c in p.capacidades
        ]
        out.append(p.model_copy(update={"capacidades": [c for c in caps if c.capacidad_mensual > 1e-9]}))
    return out


def asignar_capacidad(rec: OpcionRecomendada, lote: Lote, disponibles: dict[str, Proveedor], uso: Uso) -> None:
    """Descuenta la capacidad usada por la opción recomendada (la de mayor
    capacidad libre aporta primero)."""
    for rubro, demanda in lote.demanda_por_rubro().items():
        socios = sorted((disponibles[i] for i in rec.proveedor_ids), key=attrgetter("id"))
        socios.sort(key=methodcaller("capacidad", rubro), reverse=True)  # sort estable: empate → id
        for socio in socios:
            if demanda <= 1e-9:
                break
            toma = min(socio.capacidad(rubro), demanda)
            if toma > 0:
                uso[(socio.id, rubro)] = uso.get((socio.id, rubro), 0.0) + toma
                demanda -= toma


def analizar_pliego(
    pliego: Pliego,
    proveedores: list[Proveedor],
    pesos: dict[str, float] | None = None,
) -> AnalisisPliego:
    """Los lotes se recorren en orden y la capacidad asignada a un lote deja de
    estar disponible para los siguientes (una PyME no puede comprometer dos
    veces las mismas toneladas)."""
    pesos = pesos or PESOS_DEFAULT
    fecha = pliego.fecha_referencia
    por_id = {p.id: p for p in proveedores}
    uso: Uso = {}

    resultados: list[AnalisisLote] = []
    for lote in sugerir_lotes(pliego, proveedores):
        # Ranking informativo con capacidad total (lo que cada PyME podría hacer).
        ranking = rankear(proveedores, lote, fecha, pesos)
        # Recomendación con capacidad libre (lo que queda después de lotes anteriores).
        disponibles = con_capacidad_restante(proveedores, uso)
        ranking_libre = rankear(disponibles, lote, fecha, pesos)
        hay_local_apto = any(e.apto and e.es_local for e in ranking_libre)
        utes = [] if hay_local_apto else sugerir_utes(lote, disponibles, fecha, pesos)
        recomendada = _recomendar(lote, ranking_libre, utes)

        aptos_libres = {e.proveedor_id for e in ranking_libre if e.apto}
        comprometidos = [e.razon_social for e in ranking if e.apto and e.proveedor_id not in aptos_libres]
        if comprometidos:
            recomendada.notas.append(
                "Capacidad ya comprometida en lotes anteriores: " + ", ".join(comprometidos)
            )
        if recomendada.tipo != "sin_cobertura":
            asignar_capacidad(recomendada, lote, {p.id: p for p in disponibles}, uso)

        resultados.append(
            AnalisisLote(
                lote=lote,
                monto_usd=lote.monto_usd,
                ranking=ranking,
                utes=utes,
                recomendada=recomendada,
            )
        )

    total = sum(a.monto_usd for a in resultados)
    linea_base = linea_base_local(pliego, proveedores, pesos)
    local = sum(a.monto_usd for a in resultados if a.recomendada.tipo in ("directa_local", "ute_local"))
    # Para el RIGI cuenta como "local" cualquier proveedor argentino (no solo sanjuanino).
    nacional = sum(
        a.monto_usd
        for a in resultados
        if a.recomendada.tipo != "sin_cobertura"
        and all(por_id[i].pais == "Argentina" for i in a.recomendada.proveedor_ids)
    )
    pct = lambda x: round(100 * x / total, 1) if total else 0.0  # noqa: E731

    reporte = ReporteCupo(
        monto_total_usd=round(total, 2),
        linea_base_local_sj_pct=pct(linea_base),
        monto_local_sj_usd=round(local, 2),
        porcentaje_local_sj=pct(local),
        meta_provincial_pct=META_PROVINCIAL_PCT,
        monto_nacional_usd=round(nacional, 2),
        porcentaje_nacional=pct(nacional),
        meta_rigi_pct=META_RIGI_PCT,
        lotes_sin_cobertura_local=[
            a.lote.id for a in resultados if a.recomendada.tipo not in ("directa_local", "ute_local")
        ],
        oportunidades_desarrollo=_oportunidades(resultados, proveedores, fecha),
        advertencias=ADVERTENCIAS_REPORTE,
    )
    return AnalisisPliego(
        pliego_id=pliego.id, titulo=pliego.titulo, lotes=resultados, reporte=reporte, pesos=pesos
    )
