import { api } from "../api/cliente";
import { useApi } from "../api/useApi";
import { usd } from "../formato";

export function Pliegos() {
  const { datos, error, cargando } = useApi(api.pliegos);

  if (cargando) return <p className="estado">Cargando pliegos…</p>;
  if (error) return <p className="error">{error}</p>;

  return (
    <section>
      <h1>Oportunidades de contratación</h1>
      <p className="bajada">
        Elegí un pliego para ver cómo se puede lotificar, qué PyMEs locales pueden cubrir cada lote
        y qué alianzas conviene armar.
      </p>
      <div className="grilla">
        {datos?.map((p) => (
          <a key={p.id} className="tarjeta tarjeta--link" href={`#/pliegos/${p.id}`}>
            {p.ficticio && <span className="chip chip--aviso">Ficticio</span>}
            <h3>{p.titulo}</h3>
            <p>{p.comprador}</p>
            <p className="tenue">
              {p.items.length} ítems · {usd(p.items.reduce((s, i) => s + i.monto_estimado_usd, 0))}{" "}
              estimados
            </p>
          </a>
        ))}
      </div>
    </section>
  );
}
