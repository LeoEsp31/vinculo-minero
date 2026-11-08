import { useEffect, useState } from "react";
import { Analisis } from "./pages/Analisis";
import { Pliegos } from "./pages/Pliegos";
import { Proveedores } from "./pages/Proveedores";
import { Transparencia } from "./pages/Transparencia";

// Router mínimo por hash (#/ruta): sin dependencias y funciona en cualquier hosting estático.
function useRuta(): string {
  const [ruta, setRuta] = useState(() => window.location.hash.slice(1) || "/");
  useEffect(() => {
    const cambio = () => setRuta(window.location.hash.slice(1) || "/");
    window.addEventListener("hashchange", cambio);
    return () => window.removeEventListener("hashchange", cambio);
  }, []);
  return ruta;
}

function Pagina({ ruta }: { ruta: string }) {
  const analisis = ruta.match(/^\/pliegos\/([^/]+)$/);
  if (analisis) return <Analisis pliegoId={decodeURIComponent(analisis[1])} />;
  if (ruta === "/proveedores") return <Proveedores />;
  if (ruta === "/como-calculamos") return <Transparencia />;
  return <Pliegos />;
}

export default function App() {
  const ruta = useRuta();
  return (
    <>
      <header className="barra">
        <a href="#/" className="marca">
          Vínculo <span>Minero</span>
        </a>
        <nav>
          <a href="#/">Pliegos</a>
          <a href="#/proveedores">Proveedores</a>
          <a href="#/como-calculamos">Cómo calculamos</a>
        </nav>
      </header>
      <div className="aviso-demo" role="note">
        Prototipo de hackatón · Datos ficticios · No reemplaza la homologación ni el Repromin
      </div>
      <main className="contenedor">
        <Pagina ruta={ruta} />
      </main>
      <footer className="pie">Software libre (AGPL-3.0) · Hecho en San Juan</footer>
    </>
  );
}
