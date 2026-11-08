"""Motor de scoring explicable ("caja de cristal").

Cada proveedor recibe un puntaje 0-100 que es la suma de criterios con pesos
PÚBLICOS. Cada criterio devuelve su puntaje parcial, un detalle en lenguaje
claro y la lista de faltantes. No hay ningún paso que no se pueda explicar.

Además del puntaje (que ordena), se calcula `apto`: si cumple TODOS los
requisitos excluyentes. Un proveedor con 95 puntos pero sin una certificación
excluyente NO es apto; el ranking lo deja visible pero lo marca.

Regla de desempate (documentada a propósito, ver Práctico 2, punto 5):
  1. aptos antes que no aptos
  2. mayor puntaje
  3. proveedor local sanjuanino antes que no local
  4. orden alfabético del id (determinista)
"""

from __future__ import annotations

from datetime import date

from .modelos import (
    EvaluacionProveedor,
    Lote,
    Proveedor,
    ResultadoCriterio,
)
from .taxonomia import CERTIFICACIONES, MAQUINARIA, RUBROS

PESOS_DEFAULT: dict[str, float] = {
    "cobertura_rubros": 0.35,
    "capacidad": 0.20,
    "certificaciones": 0.20,
    "maquinaria": 0.10,
    "experiencia": 0.10,
    "dotacion": 0.05,
}

# Dentro del criterio certificaciones: cuánto pesan las excluyentes vs las deseables.
PESO_CERT_EXCLUYENTES = 0.8
PESO_CERT_DESEABLES = 0.2


def validar_pesos(pesos: dict[str, float]) -> None:
    faltan = set(PESOS_DEFAULT) - set(pesos)
    sobran = set(pesos) - set(PESOS_DEFAULT)
    if faltan or sobran:
        raise ValueError(f"Pesos inválidos. Faltan: {sorted(faltan)}; sobran: {sorted(sobran)}")
    if any(p < 0 for p in pesos.values()):
        raise ValueError("Los pesos no pueden ser negativos")
    if abs(sum(pesos.values()) - 1.0) > 1e-6:
        raise ValueError(f"Los pesos deben sumar 1 (suman {sum(pesos.values()):.3f})")


def _ponderadores(lote: Lote) -> dict[str, float]:
    """Peso de cada rubro dentro del lote: por monto; si no hay montos, uniforme."""
    montos = lote.monto_por_rubro()
    total = sum(montos.values())
    if total <= 0:
        n = len(montos)
        return {r: 1 / n for r in montos}
    return {r: m / total for r, m in montos.items()}


def _fraccion(cumplidos: int, total: int) -> float:
    return 1.0 if total == 0 else cumplidos / total


def evaluar(
    proveedor: Proveedor,
    lote: Lote,
    fecha: date,
    pesos: dict[str, float] | None = None,
) -> EvaluacionProveedor:
    pesos = pesos or PESOS_DEFAULT
    validar_pesos(pesos)

    demanda = lote.demanda_por_rubro()
    pond = _ponderadores(lote)
    criterios: list[ResultadoCriterio] = []
    motivos_no_apto: list[str] = []

    def agregar(criterio: str, puntaje: float, detalle: str, faltantes: list[str]) -> None:
        puntaje = max(0.0, min(1.0, puntaje))
        criterios.append(
            ResultadoCriterio(
                criterio=criterio,
                peso=pesos[criterio],
                puntaje=round(puntaje, 4),
                aporte=round(pesos[criterio] * puntaje * 100, 2),
                detalle=detalle,
                faltantes=faltantes,
            )
        )

    # 1. Cobertura de rubros -------------------------------------------------
    cubiertos = [r for r in demanda if proveedor.capacidad(r) > 0]
    no_cubiertos = [r for r in demanda if r not in cubiertos]
    agregar(
        "cobertura_rubros",
        sum(pond[r] for r in cubiertos),
        f"Ofrece {len(cubiertos)} de {len(demanda)} rubros del lote",
        [f"{r} · {RUBROS[r].nombre}" for r in no_cubiertos],
    )
    if no_cubiertos:
        motivos_no_apto.append(f"No ofrece: {', '.join(no_cubiertos)}")

    # 2. Capacidad -------------------------------------------------------------
    partes, falt_cap, puntaje_cap = [], [], 0.0
    for r, dem in demanda.items():
        cap = proveedor.capacidad(r)
        ratio = min(1.0, cap / dem)
        puntaje_cap += pond[r] * ratio
        unidad = RUBROS[r].unidad
        partes.append(f"{r}: {cap:g}/{dem:g} {unidad}")
        if 0 < cap < dem:
            falt_cap.append(f"{r}: le faltan {dem - cap:g} {unidad}")
    agregar("capacidad", puntaje_cap, "; ".join(partes), falt_cap)
    if falt_cap:
        motivos_no_apto.append("Capacidad insuficiente en " + ", ".join(f.split(":")[0] for f in falt_cap))

    # 3. Certificaciones -------------------------------------------------------
    vigentes = proveedor.certificaciones_vigentes(fecha)
    declaradas = {c.codigo: c for c in proveedor.certificaciones}
    excl = sorted(lote.certificaciones_excluyentes())
    des = sorted(lote.certificaciones_deseables() - set(excl))
    falt_cert: list[str] = []
    for c in excl + des:
        if c in vigentes:
            continue
        tipo = "excluyente" if c in excl else "deseable"
        vence = declaradas[c].vence if c in declaradas else None
        estado = f"vencida el {vence.isoformat()}" if vence else "no declarada"
        falt_cert.append(f"{c} ({tipo}, {estado}) · {CERTIFICACIONES[c]}")
    ok_excl = sum(c in vigentes for c in excl)
    ok_des = sum(c in vigentes for c in des)
    agregar(
        "certificaciones",
        PESO_CERT_EXCLUYENTES * _fraccion(ok_excl, len(excl))
        + PESO_CERT_DESEABLES * _fraccion(ok_des, len(des)),
        f"Excluyentes vigentes {ok_excl}/{len(excl)}; deseables {ok_des}/{len(des)}",
        falt_cert,
    )
    if ok_excl < len(excl):
        motivos_no_apto.append("Le faltan certificaciones excluyentes")

    # 4. Maquinaria ------------------------------------------------------------
    req_maq = sorted(lote.maquinaria_requerida())
    tiene = set(proveedor.maquinaria)
    falt_maq = [f"{m} · {MAQUINARIA[m]}" for m in req_maq if m not in tiene]
    agregar(
        "maquinaria",
        _fraccion(len(req_maq) - len(falt_maq), len(req_maq)),
        f"Dispone de {len(req_maq) - len(falt_maq)} de {len(req_maq)} equipos requeridos",
        falt_maq,
    )
    if falt_maq:
        motivos_no_apto.append("Le falta maquinaria requerida")

    # 5. Experiencia -----------------------------------------------------------
    exp_min = lote.experiencia_minima()
    exp = proveedor.anios_experiencia_minera
    agregar(
        "experiencia",
        1.0 if exp_min == 0 else exp / exp_min,
        f"{exp} años de experiencia minera (mínimo {exp_min})",
        [] if exp >= exp_min else [f"Faltan {exp_min - exp} años de experiencia"],
    )
    if exp < exp_min:
        motivos_no_apto.append("No alcanza la experiencia mínima")

    # 6. Dotación ----------------------------------------------------------------
    dot_min = lote.dotacion_minima()
    dot = proveedor.dotacion
    agregar(
        "dotacion",
        1.0 if dot_min == 0 else dot / dot_min,
        f"Dotación {dot} personas (mínimo {dot_min})",
        [] if dot >= dot_min else [f"Faltan {dot_min - dot} personas"],
    )
    if dot < dot_min:
        motivos_no_apto.append("No alcanza la dotación mínima")

    total = round(sum(c.aporte for c in criterios), 2)
    return EvaluacionProveedor(
        proveedor_id=proveedor.id,
        razon_social=proveedor.razon_social,
        es_local=proveedor.es_local,
        puntaje_total=total,
        apto=not motivos_no_apto,
        criterios=criterios,
        motivos_no_apto=motivos_no_apto,
    )


def clave_orden(ev: EvaluacionProveedor) -> tuple:
    """Implementa la regla de desempate documentada arriba."""
    return (not ev.apto, -ev.puntaje_total, not ev.es_local, ev.proveedor_id)


def rankear(
    proveedores: list[Proveedor],
    lote: Lote,
    fecha: date,
    pesos: dict[str, float] | None = None,
    solo_con_algun_rubro: bool = True,
) -> list[EvaluacionProveedor]:
    demanda = lote.demanda_por_rubro()
    evaluaciones = [
        evaluar(p, lote, fecha, pesos)
        for p in proveedores
        if not solo_con_algun_rubro or any(p.capacidad(r) > 0 for r in demanda)
    ]
    return sorted(evaluaciones, key=clave_orden)
