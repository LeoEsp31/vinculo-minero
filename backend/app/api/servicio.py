"""Capa de servicio: une repositorio y motor, y cachea análisis.

La API no llama al motor directamente: pasa por acá. Así, si mañana el
repositorio es una base de datos o el análisis se hace en segundo plano, los
endpoints no cambian.
"""

from __future__ import annotations

from functools import lru_cache

from ..core.analisis import analizar_pliego
from ..core.modelos import AnalisisLote, AnalisisPliego, Pliego, Proveedor
from ..core.repositorio import RepositorioMemoria
from ..core.scoring import PESOS_DEFAULT


class NoEncontrado(Exception):
    pass


class Servicio:
    def __init__(self, repo: RepositorioMemoria | None = None) -> None:
        self.repo = repo or RepositorioMemoria()
        self._cache: dict[str, AnalisisPliego] = {}

    # --- lectura ---------------------------------------------------------------
    def pliego(self, pliego_id: str) -> Pliego:
        p = self.repo.pliego(pliego_id)
        if p is None:
            raise NoEncontrado(f"Pliego {pliego_id} no existe")
        return p

    def proveedor(self, proveedor_id: str) -> Proveedor:
        p = self.repo.proveedor(proveedor_id)
        if p is None:
            raise NoEncontrado(f"Proveedor {proveedor_id} no existe")
        return p

    def analisis(self, pliego_id: str, pesos: dict[str, float] | None = None) -> AnalisisPliego:
        if pesos and pesos != PESOS_DEFAULT:  # pesos personalizados: no se cachea
            return analizar_pliego(self.pliego(pliego_id), self.repo.proveedores(), pesos)
        if pliego_id not in self._cache:
            self._cache[pliego_id] = analizar_pliego(self.pliego(pliego_id), self.repo.proveedores())
        return self._cache[pliego_id]

    def analisis_lote(self, pliego_id: str, lote_id: str) -> AnalisisLote:
        for a in self.analisis(pliego_id).lotes:
            if a.lote.id == lote_id:
                return a
        raise NoEncontrado(f"Lote {lote_id} no existe en el pliego {pliego_id}")

    # --- escritura -------------------------------------------------------------
    def guardar_pliego(self, pliego: Pliego) -> Pliego:
        self._cache.pop(pliego.id, None)
        return self.repo.guardar_pliego(pliego)

    def guardar_proveedor(self, proveedor: Proveedor) -> Proveedor:
        self._cache.clear()  # un proveedor nuevo puede cambiar todos los análisis
        return self.repo.guardar_proveedor(proveedor)


@lru_cache
def obtener_servicio() -> Servicio:
    return Servicio()
