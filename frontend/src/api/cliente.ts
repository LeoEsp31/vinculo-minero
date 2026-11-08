import type {
  AnalisisPliego,
  ChecklistPreparacion,
  Pliego,
  Proveedor,
  Sugerencia,
  Taxonomia,
} from "./tipos";

const BASE = (import.meta.env.VITE_API_URL ?? "").replace(/\/$/, "");

async function pedir<T>(ruta: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${BASE}/api${ruta}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!r.ok) {
    let detalle = r.statusText;
    try {
      detalle = (await r.json()).detail ?? detalle;
    } catch {
      /* respuesta sin JSON */
    }
    throw new Error(`Error ${r.status}: ${detalle}`);
  }
  const tipo = r.headers.get("content-type") ?? "";
  return (tipo.includes("application/json") ? r.json() : r.text()) as Promise<T>;
}

export const api = {
  pliegos: () => pedir<Pliego[]>("/pliegos"),
  pliego: (id: string) => pedir<Pliego>(`/pliegos/${id}`),
  analisis: (id: string) => pedir<AnalisisPliego>(`/pliegos/${id}/analisis`),
  analisisConPesos: (id: string, pesos: Record<string, number>) =>
    pedir<AnalisisPliego>(`/pliegos/${id}/analisis`, {
      method: "POST",
      body: JSON.stringify({ pesos }),
    }),
  preparacion: (pliegoId: string, loteId: string, proveedorId: string) =>
    pedir<ChecklistPreparacion>(`/pliegos/${pliegoId}/lotes/${loteId}/preparacion/${proveedorId}`),
  cartaUte: (pliegoId: string, loteId: string, socios: string[]) =>
    pedir<string>(
      `/pliegos/${pliegoId}/lotes/${loteId}/carta-ute?socios=${encodeURIComponent(socios.join(","))}`,
    ),
  proveedores: () => pedir<Proveedor[]>("/proveedores"),
  taxonomia: () => pedir<Taxonomia>("/taxonomia"),
  pesos: () => pedir<Record<string, number>>("/pesos"),
  sugerirRubros: (texto: string) =>
    pedir<Sugerencia[]>("/sugerir-rubros", { method: "POST", body: JSON.stringify({ texto }) }),
};
