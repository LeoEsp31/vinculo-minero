// Tipos espejo de los modelos de backend/app/core/modelos.py.
// Si cambian los modelos de pydantic, actualizar acá (ver /docs del backend).

export type TipoOpcion = "directa_local" | "ute_local" | "directa_no_local" | "sin_cobertura";

export interface ItemPliego {
  id: string;
  paquete: string;
  descripcion: string;
  rubro: string;
  cantidad_mensual: number;
  monto_estimado_usd: number;
  certificaciones_excluyentes: string[];
  certificaciones_deseables: string[];
  maquinaria_requerida: string[];
  dotacion_minima: number;
  experiencia_minima_anios: number;
}

export interface Pliego {
  id: string;
  titulo: string;
  comprador: string;
  ficticio: boolean;
  descripcion: string;
  fecha_referencia: string;
  items: ItemPliego[];
}

export interface Proveedor {
  id: string;
  razon_social: string;
  ficticio: boolean;
  pais: string;
  provincia: string;
  departamento: string;
  descripcion: string;
  capacidades: { rubro: string; capacidad_mensual: number }[];
  certificaciones: { codigo: string; vence: string | null }[];
  maquinaria: string[];
  dotacion: number;
  anios_experiencia_minera: number;
  arraigo: {
    domicilio_operativo_sj: boolean;
    tributa_en_sj: boolean;
    porcentaje_personal_sanjuanino: number;
    inscripto_repromin: boolean;
  };
}

export interface Lote {
  id: string;
  nombre: string;
  items: ItemPliego[];
  motivo: string;
}

export interface ResultadoCriterio {
  criterio: string;
  peso: number;
  puntaje: number;
  aporte: number;
  detalle: string;
  faltantes: string[];
}

export interface EvaluacionProveedor {
  proveedor_id: string;
  razon_social: string;
  es_local: boolean;
  puntaje_total: number;
  apto: boolean;
  criterios: ResultadoCriterio[];
  motivos_no_apto: string[];
}

export interface AporteSocio {
  proveedor_id: string;
  razon_social: string;
  es_local: boolean;
  aporta: string[];
  aporte_unico: string[];
}

export interface FilaCobertura {
  tipo: "rubro" | "certificacion" | "maquinaria" | "experiencia" | "dotacion";
  requisito: string;
  exigido: string;
  celdas: { proveedor_id: string; aporta: boolean; valor: string }[];
  cubierto: boolean;
}

export interface PropuestaUTE {
  socios: AporteSocio[];
  evaluacion: EvaluacionProveedor;
  explicacion: string;
  matriz: FilaCobertura[];
}

export interface OpcionRecomendada {
  tipo: TipoOpcion;
  proveedor_ids: string[];
  puntaje: number;
  explicacion: string;
  notas: string[];
}

export interface AnalisisLote {
  lote: Lote;
  monto_usd: number;
  ranking: EvaluacionProveedor[];
  utes: PropuestaUTE[];
  recomendada: OpcionRecomendada;
}

export interface ReporteCupo {
  monto_total_usd: number;
  linea_base_local_sj_pct: number;
  monto_local_sj_usd: number;
  porcentaje_local_sj: number;
  meta_provincial_pct: number;
  monto_nacional_usd: number;
  porcentaje_nacional: number;
  meta_rigi_pct: number;
  lotes_sin_cobertura_local: string[];
  oportunidades_desarrollo: string[];
  advertencias: string[];
}

export interface AnalisisPliego {
  pliego_id: string;
  titulo: string;
  lotes: AnalisisLote[];
  reporte: ReporteCupo;
  pesos: Record<string, number>;
}

export interface ItemChecklist {
  categoria: string;
  requisito: string;
  cumple: boolean;
  accion_sugerida: string;
  cubierto_por: string;
}

export interface ChecklistPreparacion {
  proveedor_id: string;
  razon_social: string;
  lote_id: string;
  items: ItemChecklist[];
  pendientes: number;
  aviso: string;
}

export interface Taxonomia {
  familias: Record<string, string>;
  rubros: { codigo: string; nombre: string; familia: string; unidad: string }[];
  certificaciones: Record<string, string>;
  maquinaria: Record<string, string>;
}

export interface Sugerencia {
  rubro: string;
  nombre: string;
  confianza: number;
  evidencia: string;
}
