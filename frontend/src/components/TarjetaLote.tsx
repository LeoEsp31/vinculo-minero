import { Fragment, useState } from "react";
import type { AnalisisLote } from "../api/tipos";
import { OPCION, usd } from "../formato";
import { DesgloseScore } from "./DesgloseScore";
import { Preparacion } from "./Preparacion";

export function TarjetaLote({ a, pliegoId }: { a: AnalisisLote; pliegoId: string }) {
  const [abierto, setAbierto] = useState(false);
  const [detalle, setDetalle] = useState<string | null>(null);
  const opcion = OPCION[a.recomendada.tipo];
  const ute = a.utes.find(
    (u) =>
      u.socios
        .map((s) => s.proveedor_id)
        .sort()
        .join() === [...a.recomendada.proveedor_ids].sort().join(),
  );

  return (
    <article className="tarjeta lote">
      <header className="lote__cabecera">
        <div>
          <span className="lote__id">{a.lote.id}</span>
          <h3>{a.lote.nombre}</h3>
          <p className="lote__motivo">{a.lote.motivo}</p>
        </div>
        <div className="lote__monto">
          <strong>{usd(a.monto_usd)}</strong>
          <span className={`chip chip--${opcion.clase}`}>{opcion.etiqueta}</span>
        </div>
      </header>

      <p className="lote__recomendacion">{a.recomendada.explicacion}</p>
      {a.recomendada.notas.map((n) => (
        <p key={n} className="nota">
          {n}
        </p>
      ))}

      {ute && (
        <div className="ute">
          <h4>UTE sugerida · {ute.evaluacion.puntaje_total.toFixed(1)} puntos</h4>
          <div className="ute__socios">
            {ute.socios.map((s) => (
              <div key={s.proveedor_id} className="socio">
                <strong>{s.razon_social}</strong>
                {s.es_local && <span className="chip chip--ok">Local</span>}
                <ul>
                  {s.aporta.map((x) => (
                    <li key={x} className={s.aporte_unico.includes(x) ? "unico" : ""}>
                      {x}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}

      {a.recomendada.proveedor_ids.length > 0 && (
        <Preparacion
          pliegoId={pliegoId}
          loteId={a.lote.id}
          socios={a.recomendada.proveedor_ids.map((id) => ({
            proveedor_id: id,
            razon_social: a.ranking.find((e) => e.proveedor_id === id)?.razon_social ?? id,
          }))}
        />
      )}

      <button className="boton boton--link" onClick={() => setAbierto(!abierto)}>
        {abierto ? "Ocultar ranking" : `Ver ranking completo (${a.ranking.length} proveedores)`}
      </button>

      {abierto && (
        <table className="ranking">
          <thead>
            <tr>
              <th>Proveedor</th>
              <th>Puntaje</th>
              <th>¿Cubre sola el lote?</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {a.ranking.map((e) => (
              <Fragment key={e.proveedor_id}>
                <tr>
                  <td>
                    {e.razon_social} {e.es_local && <span className="chip chip--ok">Local</span>}
                  </td>
                  <td>
                    <div className="mini-barra">
                      <div style={{ width: `${e.puntaje_total}%` }} />
                    </div>
                    {e.puntaje_total.toFixed(1)}
                  </td>
                  <td>{e.apto ? "Sí" : "No"}</td>
                  <td>
                    <button
                      className="boton boton--link"
                      onClick={() => setDetalle(detalle === e.proveedor_id ? null : e.proveedor_id)}
                    >
                      {detalle === e.proveedor_id ? "Cerrar" : "¿Por qué?"}
                    </button>
                  </td>
                </tr>
                {detalle === e.proveedor_id && (
                  <tr>
                    <td colSpan={4}>
                      <DesgloseScore ev={e} />
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}
          </tbody>
        </table>
      )}
    </article>
  );
}
