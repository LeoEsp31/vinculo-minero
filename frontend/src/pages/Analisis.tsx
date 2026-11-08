import { api } from "../api/cliente";
import { useApi } from "../api/useApi";
import { ReporteCupo } from "../components/ReporteCupo";
import { TarjetaLote } from "../components/TarjetaLote";

export function Analisis({ pliegoId }: { pliegoId: string }) {
  const { datos, error, cargando } = useApi(() => api.analisis(pliegoId), [pliegoId]);

  if (cargando) return <p className="estado">Analizando pliego…</p>;
  if (error || !datos) return <p className="error">{error ?? "Sin datos"}</p>;

  return (
    <section>
      <a href="#/" className="volver">
        ← Pliegos
      </a>
      <h1>{datos.titulo}</h1>
      <ReporteCupo r={datos.reporte} />
      <h2>Lotes sugeridos ({datos.lotes.length})</h2>
      {datos.lotes.map((a) => (
        <TarjetaLote key={a.lote.id} a={a} pliegoId={datos.pliego_id} />
      ))}
    </section>
  );
}
