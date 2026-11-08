"""Generador de UTEs sugeridas.

Problema: dado un lote que ninguna PyME local cubre sola, encontrar grupos de
2 o 3 PyMEs locales que JUNTAS lo cubran. Es una variante del problema de
cobertura de conjuntos (set cover): los "elementos" son los requisitos del
lote (rubros con su volumen, certificaciones, equipos, experiencia, dotación)
y cada PyME cubre un subconjunto.

Set cover en general es NP-difícil, pero acá el tamaño es chico: tomamos los
TOP_CANDIDATOS mejores perfiles y probamos todas las combinaciones de 2 y 3
(con 12 candidatos son 66 + 220 = 286 combinaciones). Eso da la solución
óptima dentro de los candidatos y es fácil de explicar.

Cómo se evalúa un grupo: se arma un "perfil combinado" (capacidades sumadas,
certificaciones y equipos unidos, dotación sumada, experiencia máxima) y se lo
pasa por el MISMO scoring que a una PyME individual. Así la UTE se explica con
los mismos criterios.

Además se descartan grupos con socios redundantes: cada socio tiene que
aportar algo que sin él faltaría. Simplificaciones conocidas (ver docs/adr):
- Las capacidades de un mismo rubro se suman entre socios.
- Una certificación se considera cubierta si la tiene al menos un socio. El
  checklist de brechas marca a cada socio que no la tenga.
"""

from __future__ import annotations

from datetime import date
from itertools import combinations
from operator import attrgetter, methodcaller

from .modelos import (
    AporteSocio,
    Arraigo,
    CapacidadRubro,
    Certificacion,
    EvaluacionProveedor,
    Lote,
    PropuestaUTE,
    Proveedor,
)
from .scoring import clave_orden, evaluar
from .taxonomia import MAQUINARIA, RUBROS

TOP_CANDIDATOS = 12
MAX_SOCIOS = 3
MAX_PROPUESTAS = 3


def perfil_combinado(socios: list[Proveedor], fecha: date) -> Proveedor:
    caps: dict[str, float] = {}
    for s in socios:
        for c in s.capacidades:
            caps[c.rubro] = caps.get(c.rubro, 0.0) + c.capacidad_mensual
    certs = sorted(set().union(*(s.certificaciones_vigentes(fecha) for s in socios)))
    return Proveedor(
        id="+".join(s.id for s in socios),
        razon_social="UTE " + " + ".join(s.razon_social for s in socios),
        ficticio=all(s.ficticio for s in socios),
        departamento=", ".join(sorted({s.departamento for s in socios})),
        capacidades=[CapacidadRubro(rubro=r, capacidad_mensual=v) for r, v in caps.items()],
        certificaciones=[Certificacion(codigo=c) for c in certs],
        maquinaria=sorted(set().union(*(set(s.maquinaria) for s in socios))),
        dotacion=sum(s.dotacion for s in socios),
        anios_experiencia_minera=max(s.anios_experiencia_minera for s in socios),
        arraigo=Arraigo(
            domicilio_operativo_sj=all(s.arraigo.domicilio_operativo_sj for s in socios),
            tributa_en_sj=all(s.arraigo.tributa_en_sj for s in socios),
            porcentaje_personal_sanjuanino=min(
                s.arraigo.porcentaje_personal_sanjuanino for s in socios
            ),
            inscripto_repromin=all(s.arraigo.inscripto_repromin for s in socios),
        ),
    )


def _aportes(socio: Proveedor, lote: Lote, fecha: date) -> set[str]:
    """Qué requisitos concretos del lote aporta este socio."""
    out: set[str] = set()
    for r in lote.demanda_por_rubro():
        if socio.capacidad(r) > 0:
            out.add(f"Rubro {r} ({socio.capacidad(r):g} {RUBROS[r].unidad})")
    req_cert = lote.certificaciones_excluyentes() | lote.certificaciones_deseables()
    out |= {f"Certificación {c}" for c in req_cert & socio.certificaciones_vigentes(fecha)}
    out |= {f"Equipo {MAQUINARIA[m]}" for m in lote.maquinaria_requerida() & set(socio.maquinaria)}
    return out


def _sin_redundancia(
    socios: list[Proveedor],
    lote: Lote,
    fecha: date,
    puntaje: float,
    pesos: dict[str, float] | None,
) -> bool:
    """True si quitar a cualquier socio empeora el puntaje del grupo."""
    for i in range(len(socios)):
        resto = socios[:i] + socios[i + 1 :]
        if len(resto) == 1:
            ev = evaluar(resto[0], lote, fecha, pesos)
        else:
            ev = evaluar(perfil_combinado(resto, fecha), lote, fecha, pesos)
        if ev.puntaje_total >= puntaje - 1e-9:
            return False
    return True


def _explicar(socios: list[AporteSocio], ev: EvaluacionProveedor) -> str:
    partes = [f"{s.razon_social} aporta {', '.join(s.aporte_unico) or 'capacidad adicional'}"
              for s in socios]
    estado = (
        "Juntas cumplen todos los requisitos excluyentes del lote."
        if ev.apto
        else "Juntas mejoran la cobertura, pero todavía falta: " + "; ".join(ev.motivos_no_apto)
    )
    return ". ".join(partes) + ". " + estado


def sugerir_utes(
    lote: Lote,
    proveedores: list[Proveedor],
    fecha: date,
    pesos: dict[str, float] | None = None,
    solo_locales: bool = True,
) -> list[PropuestaUTE]:
    demanda = lote.demanda_por_rubro()
    pool = [
        p
        for p in proveedores
        if (p.es_local or not solo_locales) and any(p.capacidad(r) > 0 for r in demanda)
    ]
    if len(pool) < 2:
        return []

    individuales = sorted((evaluar(p, lote, fecha, pesos) for p in pool), key=clave_orden)
    mejor_individual = individuales[0].puntaje_total
    por_id = {p.id: p for p in pool}

    # Candidatos: los mejores puntajes + el mejor de cada rubro (para no perder
    # a un especialista con puntaje global bajo pero imprescindible).
    candidatos_ids = [e.proveedor_id for e in individuales[:TOP_CANDIDATOS]]
    for r in demanda:
        # el de mayor capacidad en el rubro; ante empate, el de menor id
        mejor_rubro = max(sorted(pool, key=attrgetter("id")), key=methodcaller("capacidad", r))
        if mejor_rubro.capacidad(r) > 0 and mejor_rubro.id not in candidatos_ids:
            candidatos_ids.append(mejor_rubro.id)
    candidatos = [por_id[i] for i in candidatos_ids]

    propuestas: list[tuple[tuple, PropuestaUTE]] = []
    for n in range(2, MAX_SOCIOS + 1):
        for grupo in combinations(candidatos, n):
            socios = sorted(grupo, key=lambda p: p.id)
            ev = evaluar(perfil_combinado(socios, fecha), lote, fecha, pesos)
            if ev.puntaje_total <= mejor_individual and not ev.apto:
                continue  # no mejora nada respecto de presentarse solo
            if not _sin_redundancia(socios, lote, fecha, ev.puntaje_total, pesos):
                continue

            aportes = {s.id: _aportes(s, lote, fecha) for s in socios}
            aportes_socios = []
            for s in socios:
                otros = set().union(*(aportes[o.id] for o in socios if o.id != s.id))
                aportes_socios.append(
                    AporteSocio(
                        proveedor_id=s.id,
                        razon_social=s.razon_social,
                        es_local=s.es_local,
                        aporta=sorted(aportes[s.id]),
                        aporte_unico=sorted(aportes[s.id] - otros),
                    )
                )
            propuesta = PropuestaUTE(
                socios=aportes_socios, evaluacion=ev, explicacion=_explicar(aportes_socios, ev)
            )
            # Orden: aptas primero, mayor puntaje, menos socios, más socios locales, ids.
            clave = (
                not ev.apto,
                -ev.puntaje_total,
                len(socios),
                -sum(s.es_local for s in socios),
                ev.proveedor_id,
            )
            propuestas.append((clave, propuesta))

    propuestas.sort(key=lambda x: x[0])
    return [p for _, p in propuestas[:MAX_PROPUESTAS]]
