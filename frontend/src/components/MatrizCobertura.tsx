import type { PropuestaUTE } from "../api/tipos";

const TIPO: Record<string, string> = {
  rubro: "Rubro",
  certificacion: "Certificación",
  maquinaria: "Equipo",
  experiencia: "Experiencia",
  dotacion: "Personal",
};

/** Requisitos del lote (filas) × socios de la UTE (columnas): qué pone cada PyME. */
export function MatrizCobertura({ ute }: { ute: PropuestaUTE }) {
  return (
    <div className="matriz">
      <table>
        <thead>
          <tr>
            <th>Requisito del lote</th>
            <th>Se pide</th>
            {ute.socios.map((s) => (
              <th key={s.proveedor_id}>
                {s.razon_social.replace(" [DEMO]", "")}
                {s.es_local && <span className="chip chip--ok">Local</span>}
              </th>
            ))}
            <th>UTE</th>
          </tr>
        </thead>
        <tbody>
          {ute.matriz.map((f) => (
            <tr key={f.tipo + f.requisito}>
              <td>
                <span className="tenue">{TIPO[f.tipo]} · </span>
                {f.requisito}
              </td>
              <td className="tenue">{f.exigido}</td>
              {f.celdas.map((c) => (
                <td key={c.proveedor_id} className={c.aporta ? "celda--aporta" : "celda--vacia"}>
                  {c.valor}
                </td>
              ))}
              <td className={f.cubierto ? "celda--ok" : "celda--mal"}>
                {f.cubierto ? "✓ Cubierto" : "✗ Falta"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
