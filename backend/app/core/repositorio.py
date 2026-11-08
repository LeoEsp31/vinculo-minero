"""Acceso a datos.

MVP: los datos se cargan de JSON (app/data) y viven en memoria. La interfaz
`Repositorio` permite cambiar a una base de datos (SQLite/PostgreSQL) sin tocar
el motor ni la API. Ver docs/adr/0003-datos-en-memoria.md.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from .modelos import Pliego, Proveedor

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


class Repositorio(Protocol):
    def proveedores(self) -> list[Proveedor]: ...
    def proveedor(self, id: str) -> Proveedor | None: ...
    def pliegos(self) -> list[Pliego]: ...
    def pliego(self, id: str) -> Pliego | None: ...
    def guardar_pliego(self, pliego: Pliego) -> Pliego: ...
    def guardar_proveedor(self, proveedor: Proveedor) -> Proveedor: ...


class RepositorioMemoria:
    def __init__(self, data_dir: Path = DATA_DIR) -> None:
        self._proveedores = {
            p.id: p
            for p in (
                Proveedor.model_validate(d)
                for d in json.loads((data_dir / "proveedores.json").read_text("utf-8"))
            )
        }
        self._pliegos = {
            p.id: p
            for p in (
                Pliego.model_validate(d)
                for d in json.loads((data_dir / "pliegos.json").read_text("utf-8"))
            )
        }

    def proveedores(self) -> list[Proveedor]:
        return list(self._proveedores.values())

    def proveedor(self, id: str) -> Proveedor | None:
        return self._proveedores.get(id)

    def pliegos(self) -> list[Pliego]:
        return list(self._pliegos.values())

    def pliego(self, id: str) -> Pliego | None:
        return self._pliegos.get(id)

    def guardar_pliego(self, pliego: Pliego) -> Pliego:
        self._pliegos[pliego.id] = pliego
        return pliego

    def guardar_proveedor(self, proveedor: Proveedor) -> Proveedor:
        self._proveedores[proveedor.id] = proveedor
        return proveedor
