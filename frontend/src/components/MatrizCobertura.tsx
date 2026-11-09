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
  // Si la API no trae la matriz (p. ej. backend desactualizado), no rompemos la página.
  const filas = ute.matriz ?? [];
  if (filas.length === 0) return null;

  return (
    <div className="matriz">
      <table>
        <thead>
          <tr>
            <th>Requisito del lote</th>
            <th>Se pide</th>
            {ute.socios.map((s) => (
              <th key={s.proveedor_id}>
                {s.razon_social}
                {s.es_local && <span className="chip chip--ok">Local</span>}
              </th>
            ))}
            <th>UTE</th>
          </tr>
        </thead>
        <tbody>
          {filas.map((f) => {
            // Si un solo socio aporta un requisito cubierto, ese aporte es imprescindible.
            const unico = f.cubierto && f.celdas.filter((c) => c.aporta).length === 1;
            return (
              <tr key={f.tipo + f.requisito}>
                <td>
                  <span className="tenue">{TIPO[f.tipo]} · </span>
                  {f.requisito}
                </td>
                <td className="tenue">{f.exigido}</td>
                {f.celdas.map((c) => (
                  <td
                    key={c.proveedor_id}
                    className={
                      c.aporta ? `celda--aporta${unico ? " celda--unica" : ""}` : "celda--vacia"
                    }
                  >
                    {c.valor}
                  </td>
                ))}
                <td className={f.cubierto ? "celda--ok" : "celda--mal"}>
                  {f.cubierto ? "✓ Cubierto" : "✗ Falta"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <p className="tenue matriz__nota">
        En negrita: lo que solo aporta ese socio (sin él, la UTE no cubre el requisito).
      </p>
    </div>
  );
}
