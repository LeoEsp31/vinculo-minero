import type { ReporteCupo as Reporte } from "../api/tipos";
import { pct, usd } from "../formato";

function Barra({ valor, meta, etiqueta }: { valor: number; meta: number; etiqueta: string }) {
  return (
    <div className="barra-meta" aria-label={`${etiqueta}: ${pct(valor)} (meta ${pct(meta)})`}>
      <div className="barra-meta__relleno" style={{ width: `${Math.min(valor, 100)}%` }} />
      <div className="barra-meta__marca" style={{ left: `${meta}%` }} title={`Meta ${pct(meta)}`} />
    </div>
  );
}

export function ReporteCupo({ r }: { r: Reporte }) {
  return (
    <section className="tarjeta reporte">
      <h2>Compre local estimado</h2>
      <div className="reporte__antes-despues">
        <div>
          <span className="cifra cifra--tenue">{pct(r.linea_base_local_sj_pct)}</span>
          <span className="rotulo">Hoy: paquetes originales, PyMEs solas</span>
        </div>
        <span className="flecha" aria-hidden>
          →
        </span>
        <div>
          <span className="cifra">{pct(r.porcentaje_local_sj)}</span>
          <span className="rotulo">Con lotes sugeridos y UTEs locales</span>
        </div>
      </div>

      <div className="reporte__metas">
        <div>
          <div className="reporte__fila">
            <span>Proveedores sanjuaninos</span>
            <strong>
              {usd(r.monto_local_sj_usd)} de {usd(r.monto_total_usd)}
            </strong>
          </div>
          <Barra valor={r.porcentaje_local_sj} meta={r.meta_provincial_pct} etiqueta="Local SJ" />
          <small>
            Meta provincial de referencia: {pct(r.meta_provincial_pct)} (Ley de Desarrollo Local
            Minero)
          </small>
        </div>
        <div>
          <div className="reporte__fila">
            <span>Proveedores argentinos</span>
            <strong>{pct(r.porcentaje_nacional)}</strong>
          </div>
          <Barra valor={r.porcentaje_nacional} meta={r.meta_rigi_pct} etiqueta="Nacional" />
          <small>Mínimo de referencia RIGI: {pct(r.meta_rigi_pct)} (Ley 27.742)</small>
        </div>
      </div>

      {r.oportunidades_desarrollo.length > 0 && (
        <div className="reporte__oportunidades">
          <h3>Oportunidades de desarrollo de proveedores</h3>
          <ul>
            {r.oportunidades_desarrollo.map((o) => (
              <li key={o}>{o}</li>
            ))}
          </ul>
        </div>
      )}

      <details className="advertencias">
        <summary>Cómo leer esta estimación</summary>
        <ul>
          {r.advertencias.map((a) => (
            <li key={a}>{a}</li>
          ))}
        </ul>
      </details>
    </section>
  );
}
