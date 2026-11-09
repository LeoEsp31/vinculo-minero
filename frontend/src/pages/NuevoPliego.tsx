import { useState, type FormEvent } from "react";
import { api } from "../api/cliente";
import type { ItemPliego, Pliego, Taxonomia } from "../api/tipos";
import { useApi } from "../api/useApi";
import { SelectorRubro } from "../components/SelectorRubro";

type Exigencia = "" | "excluyente" | "deseable";

const hoy = () => new Date().toISOString().slice(0, 10);

const itemVacio = (n: number): ItemPliego => ({
  id: `I${n}`,
  paquete: "",
  descripcion: "",
  rubro: "",
  cantidad_mensual: 0,
  monto_estimado_usd: 0,
  certificaciones_excluyentes: [],
  certificaciones_deseables: [],
  maquinaria_requerida: [],
  dotacion_minima: 0,
  experiencia_minima_anios: 0,
});

// Ejemplo inventado para mostrar la carga en vivo (no corresponde a ningún pliego real).
const EJEMPLO: Omit<Pliego, "id" | "fecha_referencia"> = {
  titulo: "Servicios de campamento — Operación Demo Quebrada Sur",
  comprador: "Minera Demo Quebrada Sur SA [FICTICIA]",
  ficticio: true,
  descripcion: "Pliego de ejemplo cargado desde el formulario.",
  items: [
    {
      ...itemVacio(1),
      paquete: "Servicios de campamento",
      descripcion: "Comedor para el campamento",
      rubro: "SRV-CAT",
      cantidad_mensual: 25000,
      monto_estimado_usd: 900000,
      certificaciones_excluyentes: ["HAB-BROM"],
      dotacion_minima: 20,
      experiencia_minima_anios: 2,
    },
    {
      ...itemVacio(2),
      paquete: "Servicios de campamento",
      descripcion: "Limpieza de módulos y oficinas",
      rubro: "SRV-LIM",
      cantidad_mensual: 2000,
      monto_estimado_usd: 250000,
      dotacion_minima: 10,
    },
    {
      ...itemVacio(3),
      paquete: "Transporte",
      descripcion: "Traslado de personal Ciudad de San Juan – campamento",
      rubro: "LOG-PER",
      cantidad_mensual: 50,
      monto_estimado_usd: 400000,
      certificaciones_excluyentes: ["ISO-45001"],
      maquinaria_requerida: ["minibus"],
      experiencia_minima_anios: 3,
    },
  ],
};

export function NuevoPliego() {
  const tax = useApi(api.taxonomia);
  const [pliego, setPliego] = useState<Omit<Pliego, "id">>({
    titulo: "",
    comprador: "",
    ficticio: true,
    descripcion: "",
    fecha_referencia: hoy(),
    items: [itemVacio(1)],
  });
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (tax.cargando) return <p className="estado">Cargando catálogo de rubros…</p>;
  if (tax.error || !tax.datos) return <p className="error">{tax.error}</p>;
  const t = tax.datos;

  const cambiar = (campos: Partial<Omit<Pliego, "id">>) => setPliego({ ...pliego, ...campos });
  const cambiarItem = (i: number, campos: Partial<ItemPliego>) =>
    cambiar({ items: pliego.items.map((it, j) => (j === i ? { ...it, ...campos } : it)) });
  const quitarItem = (i: number) =>
    cambiar({
      items: pliego.items.filter((_, j) => j !== i).map((it, j) => ({ ...it, id: `I${j + 1}` })),
    });

  const enviar = async (e: FormEvent) => {
    e.preventDefault();
    setEnviando(true);
    setError(null);
    try {
      const id = `P-${Date.now().toString(36).toUpperCase()}`;
      const creado = await api.crearPliego({ ...pliego, id });
      window.location.hash = `#/pliegos/${encodeURIComponent(creado.id)}`;
    } catch (err) {
      setError((err as Error).message);
      setEnviando(false);
    }
  };

  return (
    <section>
      <a href="#/" className="volver">
        ← Pliegos
      </a>
      <h1>Cargar un pliego</h1>
      <p className="bajada">
        Cargá los ítems tal como los publica la minera. Al guardar, Vínculo Minero sugiere lotes,
        PyMEs y alianzas. Es un prototipo: <strong>no cargues datos reales</strong>; todo queda
        rotulado como ficticio y se borra al reiniciar el servidor.
      </p>
      <div className="botonera">
        <button
          type="button"
          className="boton boton--sec"
          onClick={() => cambiar({ ...EJEMPLO, fecha_referencia: hoy() })}
        >
          Completar con un ejemplo
        </button>
      </div>

      <form className="tarjeta form" onSubmit={enviar}>
        <div className="campos">
          <label>
            Título
            <input
              required
              value={pliego.titulo}
              onChange={(e) => cambiar({ titulo: e.target.value })}
              placeholder="Ej.: Ampliación de planta — Proyecto Demo"
            />
          </label>
          <label>
            Minera compradora
            <input
              required
              value={pliego.comprador}
              onChange={(e) => cambiar({ comprador: e.target.value })}
            />
          </label>
          <label>
            Fecha de referencia
            <input
              type="date"
              required
              value={pliego.fecha_referencia}
              onChange={(e) => cambiar({ fecha_referencia: e.target.value })}
            />
            <small className="tenue">
              Contra esta fecha se mira si las certificaciones vencieron.
            </small>
          </label>
          <label className="campos__ancho">
            Descripción (opcional)
            <input
              value={pliego.descripcion}
              onChange={(e) => cambiar({ descripcion: e.target.value })}
            />
          </label>
        </div>

        <h2>Ítems ({pliego.items.length})</h2>
        {pliego.items.map((it, i) => (
          <EditorItem
            key={i}
            item={it}
            tax={t}
            onChange={(c) => cambiarItem(i, c)}
            onQuitar={pliego.items.length > 1 ? () => quitarItem(i) : undefined}
          />
        ))}
        <div className="botonera">
          <button
            type="button"
            className="boton boton--sec"
            onClick={() =>
              cambiar({ items: [...pliego.items, itemVacio(pliego.items.length + 1)] })
            }
          >
            + Agregar ítem
          </button>
        </div>

        {error && <p className="error">No se pudo guardar. {error}</p>}
        <button className="boton" disabled={enviando}>
          {enviando ? "Analizando…" : "Guardar y analizar"}
        </button>
      </form>
    </section>
  );
}

function EditorItem({
  item,
  tax,
  onChange,
  onQuitar,
}: {
  item: ItemPliego;
  tax: Taxonomia;
  onChange: (c: Partial<ItemPliego>) => void;
  onQuitar?: () => void;
}) {
  const unidad = tax.rubros.find((r) => r.codigo === item.rubro)?.unidad ?? "";
  const exigencia = (c: string): Exigencia =>
    item.certificaciones_excluyentes.includes(c)
      ? "excluyente"
      : item.certificaciones_deseables.includes(c)
        ? "deseable"
        : "";
  const setExigencia = (c: string, v: Exigencia) => {
    const exc = item.certificaciones_excluyentes.filter((x) => x !== c);
    const des = item.certificaciones_deseables.filter((x) => x !== c);
    if (v === "excluyente") exc.push(c);
    if (v === "deseable") des.push(c);
    onChange({ certificaciones_excluyentes: exc, certificaciones_deseables: des });
  };
  const nCert = item.certificaciones_excluyentes.length + item.certificaciones_deseables.length;

  return (
    <fieldset className="item-form">
      <legend>
        Ítem {item.id}
        {onQuitar && (
          <button type="button" className="boton--link" onClick={onQuitar}>
            Quitar
          </button>
        )}
      </legend>
      <div className="campos">
        <label>
          Paquete
          <input
            value={item.paquete}
            onChange={(e) => onChange({ paquete: e.target.value })}
            placeholder="Lote en el que la minera publica el ítem"
          />
          <small className="tenue">Los ítems con el mismo paquete se publican juntos.</small>
        </label>
        <label>
          Descripción
          <input
            required
            value={item.descripcion}
            onChange={(e) => onChange({ descripcion: e.target.value })}
          />
        </label>
        <label>
          Rubro
          <SelectorRubro tax={tax} value={item.rubro} onChange={(rubro) => onChange({ rubro })} />
        </label>
        <label>
          Cantidad por mes {unidad && <span className="tenue">({unidad})</span>}
          <input
            type="number"
            required
            min={0.01}
            step="any"
            value={item.cantidad_mensual || ""}
            onChange={(e) => onChange({ cantidad_mensual: Number(e.target.value) })}
          />
        </label>
        <label>
          Monto estimado (US$)
          <input
            type="number"
            required
            min={0}
            step="any"
            value={item.monto_estimado_usd || ""}
            onChange={(e) => onChange({ monto_estimado_usd: Number(e.target.value) })}
          />
        </label>
        <label>
          Dotación mínima (personas)
          <input
            type="number"
            min={0}
            value={item.dotacion_minima}
            onChange={(e) => onChange({ dotacion_minima: Number(e.target.value) })}
          />
        </label>
        <label>
          Experiencia minera mínima (años)
          <input
            type="number"
            min={0}
            value={item.experiencia_minima_anios}
            onChange={(e) => onChange({ experiencia_minima_anios: Number(e.target.value) })}
          />
        </label>
      </div>

      <details className="desplegable">
        <summary>Certificaciones ({nCert})</summary>
        {Object.entries(tax.certificaciones).map(([codigo, nombre]) => (
          <label key={codigo} className="fila-opcion">
            <span>{nombre}</span>
            <select
              value={exigencia(codigo)}
              onChange={(e) => setExigencia(codigo, e.target.value as Exigencia)}
            >
              <option value="">No se pide</option>
              <option value="excluyente">Excluyente</option>
              <option value="deseable">Deseable</option>
            </select>
          </label>
        ))}
      </details>
      <details className="desplegable">
        <summary>Equipos requeridos ({item.maquinaria_requerida.length})</summary>
        <div className="opciones">
          {Object.entries(tax.maquinaria).map(([codigo, nombre]) => (
            <label key={codigo} className="check">
              <input
                type="checkbox"
                checked={item.maquinaria_requerida.includes(codigo)}
                onChange={(e) =>
                  onChange({
                    maquinaria_requerida: e.target.checked
                      ? [...item.maquinaria_requerida, codigo]
                      : item.maquinaria_requerida.filter((m) => m !== codigo),
                  })
                }
              />
              {nombre}
            </label>
          ))}
        </div>
      </details>
    </fieldset>
  );
}
