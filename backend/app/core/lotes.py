"""Sugerencia de lotificación de un pliego.

Punto de partida: los PAQUETES tal como los publica la minera (cada ítem del
pliego indica a qué paquete pertenece). Los paquetes grandes suelen dejar
afuera a las PyMEs locales. La plataforma sugiere desarmar SOLO lo que bloquea:

1. Ítem con más volumen que la capacidad de CUALQUIER PyME local individual:
   se saca del paquete y se divide en k lotes de tamaño cercano a la capacidad
   típica local (percentil 75), con un máximo de MAX_SUBLOTES.
2. Ítem con un requisito excluyente que NINGUNA PyME local tiene (el rubro, una
   certificación vigente o un equipo): se saca del paquete para que no bloquee
   al resto, y se informa como oportunidad de desarrollo de proveedores.
3. El resto del paquete se mantiene junto (la minera lo quiere así). Si combina
   varios rubros, es candidato a una UTE entre PyMEs complementarias.

Es una SUGERENCIA: la lotificación final es decisión de la minera.
"""

from __future__ import annotations

import math
from collections import OrderedDict
from datetime import date

from .modelos import ItemPliego, Lote, Pliego, Proveedor
from .taxonomia import CERTIFICACIONES, MAQUINARIA, RUBROS

MAX_SUBLOTES = 6


def percentil(valores: list[float], p: float) -> float:
    """Percentil con interpolación lineal (equivalente a numpy 'linear')."""
    if not valores:
        raise ValueError("lista vacía")
    xs = sorted(valores)
    pos = (len(xs) - 1) * p
    lo, hi = math.floor(pos), math.ceil(pos)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def capacidades_locales(proveedores: list[Proveedor], rubro: str) -> list[float]:
    return [p.capacidad(rubro) for p in proveedores if p.es_local and p.capacidad(rubro) > 0]


def bloqueos_locales(item: ItemPliego, proveedores: list[Proveedor], fecha: date) -> list[str]:
    """Requisitos excluyentes del ítem que ninguna PyME local cumple (ni sumando socios)."""
    locales = [p for p in proveedores if p.es_local]
    out: list[str] = []
    if not any(p.capacidad(item.rubro) > 0 for p in locales):
        out.append(f"rubro {RUBROS[item.rubro].nombre}")
    certs = set().union(*(p.certificaciones_vigentes(fecha) for p in locales)) if locales else set()
    out += [f"certificación {CERTIFICACIONES[c]}" for c in item.certificaciones_excluyentes if c not in certs]
    maq = {m for p in locales for m in p.maquinaria}
    out += [f"equipo {MAQUINARIA[m]}" for m in item.maquinaria_requerida if m not in maq]
    return out


def paquetes_originales(pliego: Pliego) -> list[Lote]:
    """Los lotes tal como los publicó la minera (sirve de línea base)."""
    grupos: OrderedDict[str, list[ItemPliego]] = OrderedDict()
    for item in pliego.items:
        grupos.setdefault(item.paquete or item.id, []).append(item)
    return [
        Lote(
            id=f"{pliego.id}-P{n:02d}",
            nombre=nombre,
            items=items,
            motivo="Paquete tal como lo publica la minera.",
        )
        for n, (nombre, items) in enumerate(grupos.items(), start=1)
    ]


def _dividir(item: ItemPliego, k: int) -> list[ItemPliego]:
    return [
        item.model_copy(
            update={
                "id": f"{item.id}-{n}",
                "descripcion": f"{item.descripcion} (parte {n}/{k})",
                "cantidad_mensual": round(item.cantidad_mensual / k, 2),
                "monto_estimado_usd": round(item.monto_estimado_usd / k, 2),
            }
        )
        for n in range(1, k + 1)
    ]


def sugerir_lotes(pliego: Pliego, proveedores: list[Proveedor]) -> list[Lote]:
    lotes: list[Lote] = []

    def nuevo(nombre: str, items: list[ItemPliego], motivo: str) -> None:
        lotes.append(
            Lote(id=f"{pliego.id}-L{len(lotes) + 1:02d}", nombre=nombre, items=items, motivo=motivo)
        )

    for paquete in paquetes_originales(pliego):
        quedan: list[ItemPliego] = []
        separados = 0
        for item in paquete.items:
            rubro = RUBROS[item.rubro]
            bloqueos = bloqueos_locales(item, proveedores, pliego.fecha_referencia)

            if bloqueos:
                separados += 1
                nuevo(
                    item.descripcion,
                    [item],
                    f"Separado del paquete «{paquete.nombre}»: ninguna PyME local registrada "
                    f"tiene {', '.join(bloqueos)}. Así no bloquea al resto del paquete, y se "
                    "informa como oportunidad de desarrollo de proveedores.",
                )
                continue

            caps = capacidades_locales(proveedores, item.rubro)

            maximo = max(caps)
            if item.cantidad_mensual <= maximo:
                quedan.append(item)
                continue

            separados += 1
            referencia = percentil(caps, 0.75)
            k = max(2, min(MAX_SUBLOTES, math.ceil(item.cantidad_mensual / referencia)))
            for n, parte in enumerate(_dividir(item, k), start=1):
                nuevo(
                    f"{item.descripcion} — parte {n}/{k}",
                    [parte],
                    f"Separado del paquete «{paquete.nombre}» y dividido: el volumen "
                    f"({item.cantidad_mensual:g} {rubro.unidad}) supera la capacidad de cualquier "
                    f"PyME local individual (máx. {maximo:g}). Se sugieren {k} lotes de "
                    f"~{parte.cantidad_mensual:g} {rubro.unidad}, cerca de la capacidad típica "
                    f"local (percentil 75: {referencia:g}).",
                )

        if quedan:
            rubros = {i.rubro for i in quedan}
            motivo = (
                "Se mantiene el paquete tal como lo publica la minera."
                if separados == 0
                else f"Resto del paquete «{paquete.nombre}» después de separar lo que bloqueaba "
                "a las PyMEs locales."
            )
            if len(rubros) > 1:
                motivo += " Combina varios rubros: candidato a una UTE entre PyMEs complementarias."
            nuevo(paquete.nombre, quedan, motivo)

    return lotes
