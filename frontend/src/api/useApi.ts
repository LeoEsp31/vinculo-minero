import { useEffect, useState } from "react";

export interface Estado<T> {
  datos: T | null;
  error: string | null;
  cargando: boolean;
}

/** Hook mínimo para pedir datos al montar o cuando cambian las dependencias. */
export function useApi<T>(pedido: () => Promise<T>, deps: unknown[] = []): Estado<T> {
  const [estado, setEstado] = useState<Estado<T>>({ datos: null, error: null, cargando: true });

  useEffect(() => {
    let vigente = true;
    setEstado({ datos: null, error: null, cargando: true });
    pedido()
      .then((datos) => vigente && setEstado({ datos, error: null, cargando: false }))
      .catch(
        (e: Error) => vigente && setEstado({ datos: null, error: e.message, cargando: false }),
      );
    return () => {
      vigente = false;
    };
  }, deps);

  return estado;
}
