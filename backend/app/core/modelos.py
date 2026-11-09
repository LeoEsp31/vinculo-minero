"""Modelos de dominio (pydantic v2).

Convención: los nombres están en español porque el dominio (pliegos, UTE,
Repromin, homologación) es local y así lo hablan los usuarios.
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from .taxonomia import validar_certificacion, validar_maquinaria, validar_rubro

# Umbral de personal sanjuanino exigido por el Repromin (Ley de Desarrollo Local Minero).
# Es parámetro, no constante mágica: si la reglamentación lo cambia, se cambia acá.
PORCENTAJE_PERSONAL_SJ_REQUERIDO = 80.0


# ---------------------------------------------------------------------------
# Oferta: perfil de la PyME
# ---------------------------------------------------------------------------


class Certificacion(BaseModel):
    codigo: str
    vence: date | None = None  # None = sin vencimiento declarado

    @field_validator("codigo")
    @classmethod
    def _validar_codigo(cls, v: str) -> str:
        return validar_certificacion(v)

    def vigente(self, al: date) -> bool:
        return self.vence is None or self.vence >= al


class CapacidadRubro(BaseModel):
    rubro: str
    capacidad_mensual: float = Field(gt=0, description="En la unidad del rubro")

    @field_validator("rubro")
    @classmethod
    def _validar_rubro(cls, v: str) -> str:
        return validar_rubro(v)


class Arraigo(BaseModel):
    """Datos para estimar si la empresa califica como proveedor local sanjuanino.

    En el MVP son declarativos/simulados: la verificación real la hace el Repromin.
    """

    domicilio_operativo_sj: bool
    tributa_en_sj: bool
    porcentaje_personal_sanjuanino: float = Field(ge=0, le=100)
    inscripto_repromin: bool = False

    def es_local(self) -> bool:
        return (
            self.domicilio_operativo_sj
            and self.tributa_en_sj
            and self.porcentaje_personal_sanjuanino >= PORCENTAJE_PERSONAL_SJ_REQUERIDO
        )

    def faltantes(self) -> list[str]:
        out: list[str] = []
        if not self.domicilio_operativo_sj:
            out.append("Domicilio operativo en San Juan")
        if not self.tributa_en_sj:
            out.append("Tributación en San Juan")
        if self.porcentaje_personal_sanjuanino < PORCENTAJE_PERSONAL_SJ_REQUERIDO:
            out.append(
                f"Personal sanjuanino {self.porcentaje_personal_sanjuanino:.0f}% "
                f"(se requiere {PORCENTAJE_PERSONAL_SJ_REQUERIDO:.0f}%)"
            )
        return out


class Proveedor(BaseModel):
    id: str
    razon_social: str
    ficticio: bool = True
    pais: str = "Argentina"
    provincia: str = "San Juan"
    departamento: str
    descripcion: str = ""
    capacidades: list[CapacidadRubro]
    certificaciones: list[Certificacion] = []
    maquinaria: list[str] = []
    dotacion: int = Field(ge=0)
    anios_experiencia_minera: int = Field(ge=0)
    arraigo: Arraigo

    @field_validator("maquinaria")
    @classmethod
    def _validar_maquinaria(cls, v: list[str]) -> list[str]:
        return [validar_maquinaria(m) for m in v]

    @property
    def es_local(self) -> bool:
        return self.arraigo.es_local()

    def capacidad(self, rubro: str) -> float:
        return sum(c.capacidad_mensual for c in self.capacidades if c.rubro == rubro)

    def certificaciones_vigentes(self, al: date) -> set[str]:
        return {c.codigo for c in self.certificaciones if c.vigente(al)}


# ---------------------------------------------------------------------------
# Demanda: pliego y lotes
# ---------------------------------------------------------------------------


class ItemPliego(BaseModel):
    id: str
    paquete: str = Field(default="", description="Lote original en el que la minera publica el ítem")
    descripcion: str
    rubro: str
    cantidad_mensual: float = Field(gt=0)
    monto_estimado_usd: float = Field(ge=0)
    certificaciones_excluyentes: list[str] = []
    certificaciones_deseables: list[str] = []
    maquinaria_requerida: list[str] = []
    dotacion_minima: int = 0
    experiencia_minima_anios: int = 0

    @field_validator("rubro")
    @classmethod
    def _validar_rubro(cls, v: str) -> str:
        return validar_rubro(v)

    @field_validator("certificaciones_excluyentes", "certificaciones_deseables")
    @classmethod
    def _validar_certificaciones(cls, v: list[str]) -> list[str]:
        return [validar_certificacion(c) for c in v]

    @field_validator("maquinaria_requerida")
    @classmethod
    def _validar_maquinaria(cls, v: list[str]) -> list[str]:
        return [validar_maquinaria(m) for m in v]


class Pliego(BaseModel):
    id: str
    titulo: str
    comprador: str
    ficticio: bool = True
    descripcion: str = ""
    fecha_referencia: date = Field(
        description="Fecha contra la que se evalúa la vigencia de certificaciones"
    )
    items: list[ItemPliego] = Field(min_length=1)


class Lote(BaseModel):
    """Agrupación de ítems (o fracción de un ítem) que se ofrece como unidad."""

    id: str
    nombre: str
    items: list[ItemPliego]
    motivo: str  # explicación en lenguaje claro de por qué se armó así

    @property
    def monto_usd(self) -> float:
        return sum(i.monto_estimado_usd for i in self.items)

    def demanda_por_rubro(self) -> dict[str, float]:
        out: dict[str, float] = {}
        for i in self.items:
            out[i.rubro] = out.get(i.rubro, 0.0) + i.cantidad_mensual
        return out

    def monto_por_rubro(self) -> dict[str, float]:
        out: dict[str, float] = {}
        for i in self.items:
            out[i.rubro] = out.get(i.rubro, 0.0) + i.monto_estimado_usd
        return out

    def certificaciones_excluyentes(self) -> set[str]:
        return {c for i in self.items for c in i.certificaciones_excluyentes}

    def certificaciones_deseables(self) -> set[str]:
        return {c for i in self.items for c in i.certificaciones_deseables}

    def maquinaria_requerida(self) -> set[str]:
        return {m for i in self.items for m in i.maquinaria_requerida}

    def dotacion_minima(self) -> int:
        return max((i.dotacion_minima for i in self.items), default=0)

    def experiencia_minima(self) -> int:
        return max((i.experiencia_minima_anios for i in self.items), default=0)


# ---------------------------------------------------------------------------
# Resultados (lo que devuelve el motor; todo trae su explicación)
# ---------------------------------------------------------------------------


class ResultadoCriterio(BaseModel):
    criterio: str
    peso: float
    puntaje: float = Field(ge=0, le=1)
    aporte: float  # peso * puntaje * 100 → puntos sobre 100
    detalle: str
    faltantes: list[str] = []


class EvaluacionProveedor(BaseModel):
    proveedor_id: str
    razon_social: str
    es_local: bool
    puntaje_total: float  # 0..100
    apto: bool  # cumple todos los requisitos excluyentes y la capacidad
    criterios: list[ResultadoCriterio]
    motivos_no_apto: list[str] = []


class AporteSocio(BaseModel):
    proveedor_id: str
    razon_social: str
    es_local: bool
    aporta: list[str]  # qué pone en la UTE (rubros, certificaciones, equipos)
    aporte_unico: list[str]  # lo que sin este socio faltaría


TipoRequisito = Literal["rubro", "certificacion", "maquinaria", "experiencia", "dotacion"]


class CeldaCobertura(BaseModel):
    proveedor_id: str
    aporta: bool
    valor: str  # lo que pone este socio: "30000 m3/mes", "✓", "7 años", "—"


class FilaCobertura(BaseModel):
    """Una fila de la matriz requisitos × socios de una UTE."""

    tipo: TipoRequisito
    requisito: str
    exigido: str  # "25000 m3/mes", "excluyente", "deseable", "3 años"
    celdas: list[CeldaCobertura]
    cubierto: bool  # el grupo, en conjunto, cumple este requisito


class PropuestaUTE(BaseModel):
    socios: list[AporteSocio]
    evaluacion: EvaluacionProveedor  # evaluación del perfil combinado
    explicacion: str
    matriz: list[FilaCobertura] = []


TipoOpcion = Literal["directa_local", "ute_local", "directa_no_local", "sin_cobertura"]


class OpcionRecomendada(BaseModel):
    tipo: TipoOpcion
    proveedor_ids: list[str]
    puntaje: float
    explicacion: str
    notas: list[str] = []  # p. ej. capacidad ya comprometida en otros lotes


class AnalisisLote(BaseModel):
    lote: Lote
    monto_usd: float
    ranking: list[EvaluacionProveedor]
    utes: list[PropuestaUTE]
    recomendada: OpcionRecomendada


class ReporteCupo(BaseModel):
    monto_total_usd: float
    linea_base_local_sj_pct: float  # % alcanzable por PyMEs locales con los paquetes originales
    monto_local_sj_usd: float
    porcentaje_local_sj: float
    meta_provincial_pct: float
    monto_nacional_usd: float
    porcentaje_nacional: float
    meta_rigi_pct: float
    lotes_sin_cobertura_local: list[str]
    oportunidades_desarrollo: list[str]  # rubros/certificaciones que no tiene nadie local
    advertencias: list[str]


class AnalisisPliego(BaseModel):
    pliego_id: str
    titulo: str
    lotes: list[AnalisisLote]
    reporte: ReporteCupo
    pesos: dict[str, float]


# ---------------------------------------------------------------------------
# Preparación para homologación (NO homologa: orienta a la PyME)
# ---------------------------------------------------------------------------

AVISO_HOMOLOGACION = (
    "Información orientativa. Vínculo Minero no certifica ni reemplaza el proceso de "
    "homologación de la empresa minera ni la inscripción en el Repromin."
)


class ItemChecklist(BaseModel):
    categoria: str
    requisito: str
    cumple: bool
    accion_sugerida: str = ""
    cubierto_por: str = ""  # en una UTE: el socio que aporta este requisito


class ChecklistPreparacion(BaseModel):
    proveedor_id: str
    razon_social: str
    lote_id: str
    items: list[ItemChecklist]
    pendientes: int
    aviso: str = AVISO_HOMOLOGACION
