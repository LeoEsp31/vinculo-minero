"""Sugerencia de rubros a partir de texto libre.

Sirve para dos cosas: que una PyME describa lo que hace con sus palabras y el
sistema le proponga rubros de la taxonomía, y que un ítem de pliego escrito en
texto libre se pueda clasificar.

IMPORTANTE (uso responsable de IA): el sugeridor SOLO SUGIERE. Una persona
confirma el rubro y el matching se hace siempre sobre códigos confirmados.

Dos implementaciones con la misma interfaz:
- `SugeridorPalabrasClave` (por defecto): sin dependencias, 100% explicable
  (devuelve qué palabras coincidieron).
- `SugeridorEmbeddings` (opcional): usa un modelo ABIERTO que corre local
  (sentence-transformers). Se activa con VM_SUGERIDOR=embeddings y el extra
  `pip install -e ".[ia]"`. Si no está instalado, se cae al de palabras clave.
"""

from __future__ import annotations

import os
import re
import unicodedata
from typing import Protocol

from pydantic import BaseModel

from .taxonomia import RUBROS

MODELO_EMBEDDINGS_DEFAULT = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class Sugerencia(BaseModel):
    rubro: str
    nombre: str
    confianza: float  # 0..1
    evidencia: str  # por qué se sugiere


class Sugeridor(Protocol):
    nombre: str

    def sugerir(self, texto: str, k: int = 3) -> list[Sugerencia]: ...


def normalizar(texto: str) -> str:
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", sin_tildes.lower())).strip()


class SugeridorPalabrasClave:
    nombre = "palabras_clave"

    def sugerir(self, texto: str, k: int = 3) -> list[Sugerencia]:
        t = f" {normalizar(texto)} "
        resultados: list[Sugerencia] = []
        for r in RUBROS.values():
            coincidencias = [kw for kw in r.palabras_clave if f" {normalizar(kw)} " in t]
            # Coincidencia por prefijo (soldadura ~ soldador, estructuras ~ estructural)
            if not coincidencias:
                coincidencias = [
                    kw for kw in r.palabras_clave
                    if len(normalizar(kw)) >= 6 and f" {normalizar(kw)[:6]}" in t
                ]
            if coincidencias:
                confianza = min(1.0, 0.4 + 0.2 * len(coincidencias))
                resultados.append(
                    Sugerencia(
                        rubro=r.codigo,
                        nombre=r.nombre,
                        confianza=round(confianza, 2),
                        evidencia="Coincide con: " + ", ".join(coincidencias),
                    )
                )
        resultados.sort(key=lambda s: (-s.confianza, s.rubro))
        return resultados[:k]


class SugeridorEmbeddings:
    nombre = "embeddings"

    def __init__(self, modelo: str = MODELO_EMBEDDINGS_DEFAULT) -> None:
        from sentence_transformers import SentenceTransformer  # import perezoso

        self._modelo = SentenceTransformer(modelo)
        self._codigos = list(RUBROS)
        descripciones = [
            f"{r.nombre}. {', '.join(r.palabras_clave)}" for r in RUBROS.values()
        ]
        self._vectores = self._modelo.encode(descripciones, normalize_embeddings=True)

    def sugerir(self, texto: str, k: int = 3) -> list[Sugerencia]:
        v = self._modelo.encode([texto], normalize_embeddings=True)[0]
        sims = self._vectores @ v
        orden = sims.argsort()[::-1][:k]
        return [
            Sugerencia(
                rubro=self._codigos[i],
                nombre=RUBROS[self._codigos[i]].nombre,
                confianza=round(float(max(0.0, sims[i])), 2),
                evidencia=f"Similitud semántica {float(sims[i]):.2f} con la descripción del rubro",
            )
            for i in orden
        ]


def crear_sugeridor() -> Sugeridor:
    if os.getenv("VM_SUGERIDOR", "palabras_clave") == "embeddings":
        try:
            return SugeridorEmbeddings(os.getenv("VM_MODELO_EMBEDDINGS", MODELO_EMBEDDINGS_DEFAULT))
        except ImportError:
            pass  # extra [ia] no instalado: seguimos con el sugeridor explicable
    return SugeridorPalabrasClave()
