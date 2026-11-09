import { useState } from "react";
import { api } from "../api/cliente";
import type { Sugerencia } from "../api/tipos";
import { useApi } from "../api/useApi";

export function Proveedores() {
  const { datos, error, cargando } = useApi(api.proveedores);
  const [texto, setTexto] = useState("");
  const [sugerencias, setSugerencias] = useState<Sugerencia[] | null>(null);

  return (
    <section>
      <h1>Proveedores registrados</h1>
      <div className="botonera">
        <a className="boton" href="#/proveedores/nuevo">
          + Registrar una PyME
        </a>
      </div>

      <div className="tarjeta">
        <h2>¿Qué rubros corresponden a mi empresa?</h2>
        <p className="tenue">
          Describí lo que hace tu empresa con tus palabras. El sistema <strong>sugiere</strong>{" "}
          rubros y muestra por qué; vos confirmás.
        </p>
        <form
          className="formulario"
          onSubmit={(e) => {
            e.preventDefault();
            api.sugerirRubros(texto).then(setSugerencias);
          }}
        >
          <input
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
            placeholder="Ej.: hacemos soldadura y montaje de estructuras de acero"
            minLength={3}
            required
          />
          <button className="boton">Sugerir</button>
        </form>
        {sugerencias && (
          <ul>
            {sugerencias.length === 0 && <li>Sin coincidencias. Probá con otras palabras.</li>}
            {sugerencias.map((s) => (
              <li key={s.rubro}>
                <strong>{s.rubro}</strong> · {s.nombre} <em className="tenue">({s.evidencia})</em>
              </li>
            ))}
          </ul>
        )}
      </div>

      {cargando && <p className="estado">Cargando…</p>}
      {error && <p className="error">{error}</p>}
      <table className="ranking">
        <thead>
          <tr>
            <th>Empresa</th>
            <th>Ubicación</th>
            <th>Rubros</th>
            <th>Certificaciones</th>
            <th>Local SJ</th>
          </tr>
        </thead>
        <tbody>
          {datos?.map((p) => {
            const a = p.arraigo;
            const local =
              a.domicilio_operativo_sj && a.tributa_en_sj && a.porcentaje_personal_sanjuanino >= 80;
            return (
              <tr key={p.id}>
                <td>
                  <strong>{p.razon_social}</strong>
                  <div className="tenue">{p.descripcion}</div>
                </td>
                <td>
                  {p.departamento}, {p.provincia}
                </td>
                <td>{p.capacidades.map((c) => c.rubro).join(", ")}</td>
                <td>{p.certificaciones.map((c) => c.codigo).join(", ") || "—"}</td>
                <td>{local ? <span className="chip chip--ok">Sí</span> : "No"}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </section>
  );
}
