import type { EvaluacionProveedor } from "../api/tipos";
import { NOMBRE_CRITERIO } from "../formato";

/** La "caja de cristal": muestra de dónde sale cada punto del puntaje. */
export function DesgloseScore({ ev }: { ev: EvaluacionProveedor }) {
  return (
    <div className="desglose">
      <table>
        <thead>
          <tr>
            <th>Criterio</th>
            <th>Peso</th>
            <th>Cumplimiento</th>
            <th>Puntos</th>
            <th>Detalle</th>
          </tr>
        </thead>
        <tbody>
          {ev.criterios.map((c) => (
            <tr key={c.criterio}>
              <td>{NOMBRE_CRITERIO[c.criterio] ?? c.criterio}</td>
              <td>{Math.round(c.peso * 100)}%</td>
              <td>
                <div className="mini-barra">
                  <div style={{ width: `${c.puntaje * 100}%` }} />
                </div>
              </td>
              <td>{c.aporte.toFixed(1)}</td>
              <td>
                {c.detalle}
                {c.faltantes.length > 0 && (
                  <ul className="faltantes">
                    {c.faltantes.map((f) => (
                      <li key={f}>{f}</li>
                    ))}
                  </ul>
                )}
              </td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <td colSpan={3}>Total</td>
            <td>
              <strong>{ev.puntaje_total.toFixed(1)}</strong>
            </td>
            <td>{ev.apto ? "Cumple todos los excluyentes" : ev.motivos_no_apto.join(" · ")}</td>
          </tr>
        </tfoot>
      </table>
    </div>
  );
}
