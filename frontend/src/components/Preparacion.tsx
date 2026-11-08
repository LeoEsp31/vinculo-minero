import { useState } from "react";
import { api } from "../api/cliente";
import type { ChecklistPreparacion } from "../api/tipos";

interface Props {
  pliegoId: string;
  loteId: string;
  socios: { proveedor_id: string; razon_social: string }[];
}

/** Checklist de preparación para homologación + borrador de carta de intención. */
export function Preparacion({ pliegoId, loteId, socios }: Props) {
  const [checklist, setChecklist] = useState<ChecklistPreparacion | null>(null);
  const [carta, setCarta] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const verChecklist = (id: string) =>
    api
      .preparacion(pliegoId, loteId, id)
      .then(setChecklist)
      .catch((e: Error) => setError(e.message));

  const verCarta = () =>
    api
      .cartaUte(
        pliegoId,
        loteId,
        socios.map((s) => s.proveedor_id),
      )
      .then(setCarta)
      .catch((e: Error) => setError(e.message));

  return (
    <div className="preparacion">
      <div className="botonera">
        {socios.map((s) => (
          <button
            key={s.proveedor_id}
            className="boton boton--sec"
            onClick={() => verChecklist(s.proveedor_id)}
          >
            Checklist de {s.razon_social.replace(" [DEMO]", "")}
          </button>
        ))}
        {socios.length > 1 && (
          <button className="boton" onClick={verCarta}>
            Borrador de carta de intención
          </button>
        )}
      </div>
      {error && <p className="error">{error}</p>}

      {checklist && (
        <div className="checklist">
          <h4>
            Preparación para homologación · {checklist.razon_social} ({checklist.pendientes}{" "}
            pendientes)
          </h4>
          <p className="aviso">{checklist.aviso}</p>
          <ul>
            {checklist.items.map((i) => (
              <li key={i.categoria + i.requisito} className={i.cumple ? "cumple" : "pendiente"}>
                <span aria-hidden>{i.cumple ? "✓" : "○"}</span> <strong>{i.categoria}:</strong>{" "}
                {i.requisito}
                {i.accion_sugerida && <em> — {i.accion_sugerida}</em>}
                {i.cubierto_por && <em> — lo aporta {i.cubierto_por}</em>}
              </li>
            ))}
          </ul>
        </div>
      )}

      {carta && (
        <div className="carta">
          <div className="botonera">
            <button
              className="boton boton--sec"
              onClick={() => navigator.clipboard.writeText(carta)}
            >
              Copiar
            </button>
          </div>
          <pre>{carta}</pre>
        </div>
      )}
    </div>
  );
}
