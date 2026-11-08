"""Punto de entrada de la API.

Desarrollo:  uvicorn app.main:app --reload
Documentación interactiva: http://localhost:8000/docs
"""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.rutas import router

app = FastAPI(
    title="Vínculo Minero API",
    version="0.1.0",
    description=(
        "Vinculación explicable entre la demanda minera y las PyMEs proveedoras de San Juan. "
        "Prototipo de hackatón: todos los datos son ficticios. No reemplaza los procesos de "
        "homologación de las empresas mineras ni la inscripción en el Repromin."
    ),
    license_info={"name": "AGPL-3.0-or-later", "identifier": "AGPL-3.0-or-later"},
)

origenes = [o for o in os.getenv("VM_CORS_ORIGINS", "http://localhost:5173").split(",") if o]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(router)
