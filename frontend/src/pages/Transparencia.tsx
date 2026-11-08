import { api } from "../api/cliente";
import { useApi } from "../api/useApi";
import { NOMBRE_CRITERIO } from "../formato";

/** Página "caja de cristal": cómo se calcula todo, sin secretos. */
export function Transparencia() {
  const pesos = useApi(api.pesos);
  const tax = useApi(api.taxonomia);

  return (
    <section>
      <h1>Cómo calculamos</h1>
      <div className="tarjeta">
        <h2>Pesos del puntaje de compatibilidad</h2>
        <p className="tenue">
          El puntaje (0 a 100) es la suma de estos criterios. Además del puntaje, un proveedor solo
          se recomienda si cumple <strong>todos</strong> los requisitos excluyentes del lote.
        </p>
        <ul>
          {pesos.datos &&
            Object.entries(pesos.datos).map(([k, v]) => (
              <li key={k}>
                {NOMBRE_CRITERIO[k] ?? k}: <strong>{Math.round(v * 100)}%</strong>
              </li>
            ))}
        </ul>
        <h3>Regla de desempate</h3>
        <ol>
          <li>Proveedores que cumplen los excluyentes antes que los que no</li>
          <li>Mayor puntaje</li>
          <li>Proveedor local sanjuanino antes que no local</li>
          <li>Orden alfabético del identificador</li>
        </ol>
        <h3>Uso de IA</h3>
        <p>
          La IA solo <strong>sugiere</strong> rubros a partir de texto libre y siempre muestra la
          evidencia. El ranking, la lotificación y las UTEs se calculan con reglas y algoritmos
          documentados. La plataforma no homologa proveedores ni reemplaza el Repromin.
        </p>
      </div>

      {tax.datos && (
        <div className="tarjeta">
          <h2>Taxonomía de rubros</h2>
          <table className="ranking">
            <thead>
              <tr>
                <th>Código</th>
                <th>Rubro</th>
                <th>Familia</th>
                <th>Unidad</th>
              </tr>
            </thead>
            <tbody>
              {tax.datos.rubros.map((r) => (
                <tr key={r.codigo}>
                  <td>{r.codigo}</td>
                  <td>{r.nombre}</td>
                  <td>{tax.datos?.familias[r.familia]}</td>
                  <td>{r.unidad}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
