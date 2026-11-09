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
      const d = (await r.json()).detail;
      // FastAPI devuelve los errores de validación (422) como lista: los pasamos a texto.
      if (Array.isArray(d)) {
        detalle = d
          .map((e: { loc?: unknown[]; msg?: string }) => {
            const campo = (e.loc ?? []).filter((x) => x !== "body").join(" › ");
            return campo ? `${campo}: ${e.msg}` : e.msg;
          })
          .join("; ");
      } else if (d) {
        detalle = String(d);
      }
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
  crearPliego: (p: Pliego) =>
    pedir<Pliego>("/pliegos", { method: "POST", body: JSON.stringify(p) }),
  crearProveedor: (p: Proveedor) =>
    pedir<Proveedor>("/proveedores", { method: "POST", body: JSON.stringify(p) }),
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
