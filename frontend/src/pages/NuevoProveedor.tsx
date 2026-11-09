import { useState, type FormEvent } from "react";
import { api } from "../api/cliente";
import type { Proveedor, Sugerencia } from "../api/tipos";
import { useApi } from "../api/useApi";
import { SelectorRubro } from "../components/SelectorRubro";

// Mismo umbral que PORCENTAJE_PERSONAL_SJ_REQUERIDO en backend/app/core/modelos.py.
const PERSONAL_SJ_REQUERIDO = 80;

const DEPARTAMENTOS_SJ = [
  "Albardón", "Angaco", "Calingasta", "Capital", "Caucete", "Chimbas", "Iglesia", "Jáchal",
  "9 de Julio", "Pocito", "Rawson", "Rivadavia", "San Martín", "Santa Lucía", "Sarmiento",
  "Ullum", "Valle Fértil", "25 de Mayo", "Zonda",
]; // prettier-ignore

type Nuevo = Omit<Proveedor, "id">;

const VACIO: Nuevo = {
  razon_social: "",
  ficticio: true,
  pais: "Argentina",
  provincia: "San Juan",
  departamento: "",
  descripcion: "",
  capacidades: [],
  certificaciones: [],
  maquinaria: [],
  dotacion: 0,
  anios_experiencia_minera: 0,
  arraigo: {
    domicilio_operativo_sj: true,
    tributa_en_sj: true,
    porcentaje_personal_sanjuanino: 100,
    inscripto_repromin: false,
  },
};

export function NuevoProveedor() {
  const tax = useApi(api.taxonomia);
  const [p, setP] = useState<Nuevo>(VACIO);
  const [sugerencias, setSugerencias] = useState<Sugerencia[] | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [creado, setCreado] = useState<Proveedor | null>(null);

  if (tax.cargando) return <p className="estado">Cargando catálogo de rubros…</p>;
  if (tax.error || !tax.datos) return <p className="error">{tax.error}</p>;
  const t = tax.datos;

  const cambiar = (c: Partial<Nuevo>) => setP({ ...p, ...c });
  const cambiarArraigo = (c: Partial<Nuevo["arraigo"]>) =>
    cambiar({ arraigo: { ...p.arraigo, ...c } });
  const unidad = (rubro: string) => t.rubros.find((r) => r.codigo === rubro)?.unidad ?? "";
  const tieneRubro = (rubro: string) => p.capacidades.some((c) => c.rubro === rubro);

  const a = p.arraigo;
  const faltantesLocal = [
    !a.domicilio_operativo_sj && "domicilio operativo en San Juan",
    !a.tributa_en_sj && "tributación en San Juan",
    a.porcentaje_personal_sanjuanino < PERSONAL_SJ_REQUERIDO &&
      `al menos ${PERSONAL_SJ_REQUERIDO}% de personal sanjuanino`,
  ].filter(Boolean);

  const sugerir = async () => {
    if (p.descripcion.trim().length < 3) return;
    setSugerencias(await api.sugerirRubros(p.descripcion));
  };

  const enviar = async (e: FormEvent) => {
    e.preventDefault();
    if (p.capacidades.length === 0) {
      setError("Agregá al menos un rubro con su capacidad mensual.");
      return;
    }
    setEnviando(true);
    setError(null);
    try {
      setCreado(
        await api.crearProveedor({ ...p, id: `S-${Date.now().toString(36).toUpperCase()}` }),
      );
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setEnviando(false);
    }
  };

  if (creado)
    return (
      <section>
        <h1>Empresa registrada</h1>
        <div className="tarjeta">
          <p>
            <strong>{creado.razon_social}</strong> ya forma parte del análisis: los rankings y las
            alianzas de todos los pliegos la tienen en cuenta.
          </p>
          <p className="tenue">
            Registrarse acá no homologa a la empresa ni la inscribe en el Repromin.
          </p>
          <div className="botonera">
            <a className="boton" href="#/">
              Ver pliegos
            </a>
            <a className="boton boton--sec" href="#/proveedores">
              Ver proveedores
            </a>
          </div>
        </div>
      </section>
    );

  return (
    <section>
      <a href="#/proveedores" className="volver">
        ← Proveedores
      </a>
      <h1>Registrar una PyME</h1>
      <p className="bajada">
        Con este perfil la plataforma calcula en qué lotes puede competir la empresa y con quién le
        conviene asociarse. Es un prototipo: <strong>no cargues datos reales</strong>; todo queda
        rotulado como [DEMO] y se borra al reiniciar el servidor.
      </p>

      <form className="tarjeta form" onSubmit={enviar}>
        <div className="campos">
          <label>
            Razón social
            <input
              required
              value={p.razon_social}
              onChange={(e) => cambiar({ razon_social: e.target.value })}
            />
          </label>
          <label>
            Provincia
            <input
              required
              value={p.provincia}
              onChange={(e) => cambiar({ provincia: e.target.value })}
            />
          </label>
          <label>
            Departamento
            <input
              required
              list="departamentos-sj"
              value={p.departamento}
              onChange={(e) => cambiar({ departamento: e.target.value })}
            />
            <datalist id="departamentos-sj">
              {DEPARTAMENTOS_SJ.map((d) => (
                <option key={d} value={d} />
              ))}
            </datalist>
          </label>
          <label>
            Personal (personas)
            <input
              type="number"
              min={0}
              required
              value={p.dotacion}
              onChange={(e) => cambiar({ dotacion: Number(e.target.value) })}
            />
          </label>
          <label>
            Experiencia en minería (años)
            <input
              type="number"
              min={0}
              required
              value={p.anios_experiencia_minera}
              onChange={(e) => cambiar({ anios_experiencia_minera: Number(e.target.value) })}
            />
          </label>
        </div>

        <h2>¿Qué hace la empresa?</h2>
        <label className="campos__ancho">
          Describilo con tus palabras
          <textarea
            rows={3}
            value={p.descripcion}
            onChange={(e) => cambiar({ descripcion: e.target.value })}
            placeholder="Ej.: hacemos soldadura y montaje de estructuras de acero para la industria"
          />
        </label>
        <div className="botonera">
          <button
            type="button"
            className="boton boton--sec"
            onClick={sugerir}
            disabled={p.descripcion.trim().length < 3}
          >
            Sugerir rubros
          </button>
        </div>
        {sugerencias && (
          <div className="sugerencias">
            <p className="tenue">
              El sistema <strong>sugiere</strong> y muestra por qué; vos decidís qué agregar.
            </p>
            {sugerencias.length === 0 && <p>Sin coincidencias. Probá con otras palabras.</p>}
            <ul>
              {sugerencias.map((s) => (
                <li key={s.rubro}>
                  <strong>{s.nombre}</strong> <em className="tenue">({s.evidencia})</em>{" "}
                  {tieneRubro(s.rubro) ? (
                    <span className="chip chip--ok">Agregado</span>
                  ) : (
                    <button
                      type="button"
                      className="boton--link"
                      onClick={() =>
                        cambiar({
                          capacidades: [...p.capacidades, { rubro: s.rubro, capacidad_mensual: 0 }],
                        })
                      }
                    >
                      Agregar
                    </button>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}

        <h3>Rubros y capacidad mensual</h3>
        {p.capacidades.length === 0 && (
          <p className="tenue">Todavía no agregaste rubros. Usá el sugeridor o agregalos a mano.</p>
        )}
        {p.capacidades.map((c, i) => (
          <div key={i} className="fila-capacidad">
            <SelectorRubro
              tax={t}
              value={c.rubro}
              onChange={(rubro) =>
                cambiar({
                  capacidades: p.capacidades.map((x, j) => (j === i ? { ...x, rubro } : x)),
                })
              }
            />
            <input
              type="number"
              required
              min={0.01}
              step="any"
              aria-label="Capacidad mensual"
              placeholder="Capacidad"
              value={c.capacidad_mensual || ""}
              onChange={(e) =>
                cambiar({
                  capacidades: p.capacidades.map((x, j) =>
                    j === i ? { ...x, capacidad_mensual: Number(e.target.value) } : x,
                  ),
                })
              }
            />
            <span className="tenue">{unidad(c.rubro)}</span>
            <button
              type="button"
              className="boton--link"
              onClick={() => cambiar({ capacidades: p.capacidades.filter((_, j) => j !== i) })}
            >
              Quitar
            </button>
          </div>
        ))}
        <div className="botonera">
          <button
            type="button"
            className="boton boton--sec"
            onClick={() =>
              cambiar({ capacidades: [...p.capacidades, { rubro: "", capacidad_mensual: 0 }] })
            }
          >
            + Agregar rubro
          </button>
        </div>

        <details className="desplegable">
          <summary>Certificaciones ({p.certificaciones.length})</summary>
          {Object.entries(t.certificaciones).map(([codigo, nombre]) => {
            const cert = p.certificaciones.find((c) => c.codigo === codigo);
            return (
              <div key={codigo} className="fila-opcion">
                <label className="check">
                  <input
                    type="checkbox"
                    checked={!!cert}
                    onChange={(e) =>
                      cambiar({
                        certificaciones: e.target.checked
                          ? [...p.certificaciones, { codigo, vence: null }]
                          : p.certificaciones.filter((c) => c.codigo !== codigo),
                      })
                    }
                  />
                  {nombre}
                </label>
                {cert && (
                  <label className="tenue">
                    Vence{" "}
                    <input
                      type="date"
                      value={cert.vence ?? ""}
                      onChange={(e) =>
                        cambiar({
                          certificaciones: p.certificaciones.map((c) =>
                            c.codigo === codigo ? { ...c, vence: e.target.value || null } : c,
                          ),
                        })
                      }
                    />
                  </label>
                )}
              </div>
            );
          })}
        </details>
        <details className="desplegable">
          <summary>Equipos propios ({p.maquinaria.length})</summary>
          <div className="opciones">
            {Object.entries(t.maquinaria).map(([codigo, nombre]) => (
              <label key={codigo} className="check">
                <input
                  type="checkbox"
                  checked={p.maquinaria.includes(codigo)}
                  onChange={(e) =>
                    cambiar({
                      maquinaria: e.target.checked
                        ? [...p.maquinaria, codigo]
                        : p.maquinaria.filter((m) => m !== codigo),
                    })
                  }
                />
                {nombre}
              </label>
            ))}
          </div>
        </details>

        <h3>Arraigo en San Juan</h3>
        <div className="opciones">
          <label className="check">
            <input
              type="checkbox"
              checked={a.domicilio_operativo_sj}
              onChange={(e) => cambiarArraigo({ domicilio_operativo_sj: e.target.checked })}
            />
            Domicilio operativo en San Juan
          </label>
          <label className="check">
            <input
              type="checkbox"
              checked={a.tributa_en_sj}
              onChange={(e) => cambiarArraigo({ tributa_en_sj: e.target.checked })}
            />
            Tributa en San Juan
          </label>
          <label className="check">
            <input
              type="checkbox"
              checked={a.inscripto_repromin}
              onChange={(e) => cambiarArraigo({ inscripto_repromin: e.target.checked })}
            />
            Inscripta en el Repromin
          </label>
        </div>
        <label>
          Personal sanjuanino (%)
          <input
            type="number"
            min={0}
            max={100}
            required
            value={a.porcentaje_personal_sanjuanino}
            onChange={(e) =>
              cambiarArraigo({ porcentaje_personal_sanjuanino: Number(e.target.value) })
            }
          />
        </label>
        <p className={faltantesLocal.length ? "aviso-local aviso-local--no" : "aviso-local"}>
          {faltantesLocal.length
            ? `Con estos datos no se estimaría como proveedor local sanjuanino. Falta: ${faltantesLocal.join(", ")}.`
            : "Con estos datos se estimaría como proveedor local sanjuanino."}{" "}
          <span className="tenue">
            Es una estimación con datos declarados; quien lo verifica es el Repromin.
          </span>
        </p>

        {error && <p className="error">No se pudo guardar. {error}</p>}
        <button className="boton" disabled={enviando}>
          {enviando ? "Guardando…" : "Registrar empresa"}
        </button>
      </form>
    </section>
  );
}
