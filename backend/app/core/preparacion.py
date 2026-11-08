"""Preparación para homologación.

Respeta el límite del desafío: NO homologa ni certifica. Le muestra a la PyME
(o a cada socio de una UTE) qué le falta para presentarse a un lote y genera
un borrador de carta de intención para formalizar la alianza.
"""

from __future__ import annotations

from datetime import date

from .modelos import (
    AVISO_HOMOLOGACION,
    PORCENTAJE_PERSONAL_SJ_REQUERIDO,
    ChecklistPreparacion,
    ItemChecklist,
    Lote,
    Pliego,
    PropuestaUTE,
    Proveedor,
)
from .taxonomia import CERTIFICACIONES, MAQUINARIA, RUBROS


def _usd(monto: float) -> str:
    return f"USD {monto:,.0f}".replace(",", ".")


def checklist(
    proveedor: Proveedor,
    lote: Lote,
    fecha: date,
    socios: list[Proveedor] | None = None,
) -> ChecklistPreparacion:
    """Si se pasan `socios` (los demás integrantes de la UTE), los requisitos que
    aporta un socio se marcan como cubiertos e indican quién los aporta."""
    items: list[ItemChecklist] = []
    vigentes = proveedor.certificaciones_vigentes(fecha)
    otros = [s for s in (socios or []) if s.id != proveedor.id]

    for r, dem in lote.demanda_por_rubro().items():
        cap = proveedor.capacidad(r)
        if cap == 0:
            continue  # no es su rubro: en una UTE lo aporta otro socio
        items.append(
            ItemChecklist(
                categoria="Capacidad",
                requisito=f"{RUBROS[r].nombre}: {dem:g} {RUBROS[r].unidad}",
                cumple=cap >= dem,
                accion_sugerida="" if cap >= dem else
                f"Declara {cap:g}. Evaluar presentarse en UTE o a un lote de menor volumen.",
            )
        )

    for c in sorted(lote.certificaciones_excluyentes()):
        ok = c in vigentes
        items.append(
            ItemChecklist(
                categoria="Certificación (excluyente)",
                requisito=CERTIFICACIONES[c],
                cumple=ok,
                accion_sugerida="" if ok else "Obtener o renovar la certificación antes de ofertar.",
            )
        )

    for m in sorted(lote.maquinaria_requerida()):
        ok = m in proveedor.maquinaria
        items.append(
            ItemChecklist(
                categoria="Maquinaria",
                requisito=MAQUINARIA[m],
                cumple=ok,
                accion_sugerida="" if ok else "Alquilar, adquirir o sumarla mediante un socio.",
            )
        )

    exp_min, dot_min = lote.experiencia_minima(), lote.dotacion_minima()
    if exp_min:
        ok = proveedor.anios_experiencia_minera >= exp_min
        items.append(ItemChecklist(
            categoria="Experiencia",
            requisito=f"{exp_min} años en minería",
            cumple=ok,
            accion_sugerida="" if ok else "Documentar antecedentes o asociarse con un socio con trayectoria.",
        ))
    if dot_min:
        ok = proveedor.dotacion >= dot_min
        items.append(ItemChecklist(
            categoria="Dotación",
            requisito=f"{dot_min} personas",
            cumple=ok,
            accion_sugerida="" if ok else "Sumar personal o complementar con un socio.",
        ))

    a = proveedor.arraigo
    items += [
        ItemChecklist(categoria="Arraigo local", requisito="Domicilio operativo en San Juan",
                      cumple=a.domicilio_operativo_sj),
        ItemChecklist(categoria="Arraigo local", requisito="Tributación en San Juan",
                      cumple=a.tributa_en_sj),
        ItemChecklist(
            categoria="Arraigo local",
            requisito=f"Al menos {PORCENTAJE_PERSONAL_SJ_REQUERIDO:.0f}% de personal sanjuanino",
            cumple=a.porcentaje_personal_sanjuanino >= PORCENTAJE_PERSONAL_SJ_REQUERIDO,
            accion_sugerida=f"Declara {a.porcentaje_personal_sanjuanino:.0f}%.",
        ),
        ItemChecklist(
            categoria="Registro",
            requisito="Inscripción en el Repromin",
            cumple=a.inscripto_repromin,
            accion_sugerida="" if a.inscripto_repromin else
            "Iniciar la inscripción en el Registro de Proveedores Mineros de San Juan.",
        ),
    ]
    for it in items:
        if not it.cumple and it.categoria.startswith(("Certificación", "Maquinaria")):
            for s in otros:
                tiene = (
                    any(CERTIFICACIONES[c] == it.requisito for c in s.certificaciones_vigentes(fecha))
                    if it.categoria.startswith("Certificación")
                    else any(MAQUINARIA[m] == it.requisito for m in s.maquinaria)
                )
                if tiene:
                    it.cumple, it.cubierto_por = True, s.razon_social
                    break
        if it.cumple:
            it.accion_sugerida = ""

    return ChecklistPreparacion(
        proveedor_id=proveedor.id,
        razon_social=proveedor.razon_social,
        lote_id=lote.id,
        items=items,
        pendientes=sum(not i.cumple for i in items),
    )


def borrador_carta_intencion(propuesta: PropuestaUTE, lote: Lote, pliego: Pliego) -> str:
    """Borrador en Markdown. Es un punto de partida para la conversación entre
    las PyMEs, no un documento legal."""
    ev = propuesta.evaluacion
    cobertura = (
        "Juntas cumplen todos los requisitos excluyentes del lote."
        if ev.apto
        else "Todavía falta: " + "; ".join(ev.motivos_no_apto) + "."
    )
    socios = "\n".join(
        f"- **{s.razon_social}**: aporta {', '.join(s.aporta) or '—'}." for s in propuesta.socios
    )
    return f"""# Carta de intención para conformar una UTE (BORRADOR)

> {AVISO_HOMOLOGACION} Este borrador debe ser revisado por un profesional
> antes de firmarse.

**Convocatoria:** {pliego.titulo} — {pliego.comprador}
**Lote:** {lote.nombre} ({lote.id}) — monto estimado {_usd(lote.monto_usd)}

Las empresas abajo firmantes manifiestan su intención de presentarse en forma
conjunta al lote indicado, conformando una Unión Transitoria (UTE), con los
siguientes aportes:

{socios}

**Puntaje de compatibilidad del perfil conjunto:** {propuesta.evaluacion.puntaje_total:.1f}/100.
{cobertura}

Puntos a acordar entre las partes:
1. Empresa representante ante el comprador.
2. Porcentaje de participación de cada socio y reparto de resultados.
3. Responsabilidades técnicas por rubro y responsable de seguridad e higiene.
4. Plazo de vigencia de este acuerdo si el lote no es adjudicado.
"""
