import type { TipoOpcion } from "./api/tipos";

export const usd = (n: number) =>
  new Intl.NumberFormat("es-AR", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(n);

export const pct = (n: number) => `${n.toLocaleString("es-AR", { maximumFractionDigits: 1 })}%`;

export const NOMBRE_CRITERIO: Record<string, string> = {
  cobertura_rubros: "Cobertura de rubros",
  capacidad: "Capacidad",
  certificaciones: "Certificaciones",
  maquinaria: "Maquinaria",
  experiencia: "Experiencia minera",
  dotacion: "Dotación",
};

export const OPCION: Record<TipoOpcion, { etiqueta: string; clase: string }> = {
  directa_local: { etiqueta: "PyME local", clase: "ok" },
  ute_local: { etiqueta: "UTE local", clase: "ute" },
  directa_no_local: { etiqueta: "Proveedor no local", clase: "aviso" },
  sin_cobertura: { etiqueta: "Sin cobertura", clase: "mal" },
};
