# Supuestos, limitaciones, riesgos y próximos pasos

Complementa [arquitectura](arquitectura.md) y [límites y uso responsable](limites-y-uso-responsable.md).

## Supuestos

1. **Las PyMEs declaran su capacidad mensual por rubro** en la misma unidad que usa la
   minera (t/mes, HH/mes, m³/mes, etc.). La taxonomía de 16 rubros es la que fija esas unidades.
2. **La condición de proveedor local se estima** con tres datos declarados: domicilio
   operativo en San Juan, tributación en San Juan y al menos 80 % de personal sanjuanino.
   Quien la verifica es el Repromin.
3. **Al dividir un ítem en lotes**, la cantidad y el monto se reparten en partes iguales.
4. **Los pesos del puntaje los definió el equipo.** Son públicos y se pueden cambiar
   (`POST /api/pliegos/{id}/analisis`).
5. **El porcentaje de compre local es una estimación sobre un pliego**, no sobre las
   compras anuales ni sobre el monto de inversión de un proyecto. Las metas provinciales son
   objetivos, no cupos obligatorios ([fuentes](fuentes.md)).

## Limitaciones del prototipo

- Datos ficticios y en memoria: lo que se carga desde los formularios se pierde al
  reiniciar ([ADR 0003](adr/0003-datos-en-memoria.md)).
- Sin usuarios ni permisos: cualquiera que entra a la demo ve todo.
- En una UTE, una certificación cuenta como cubierta si la tiene al menos un socio
  (issue #11).
- La capacidad se reparte entre lotes en orden (*greedy*), no de forma óptima (issue #15).
- La demo corre en un plan gratuito: se duerme sin uso y tarda en despertar.

## Riesgos y cómo los mitigamos

| Riesgo | Qué podría pasar | Mitigación |
|---|---|---|
| **Datos declarados incorrectos** | Una PyME exagera su capacidad o carga una certificación vencida. | La plataforma muestra lo declarado como declarado y no valida ni homologa: eso lo hacen el Repromin y la minera. Las certificaciones se evalúan con su fecha de vencimiento. |
| **Confiar demasiado en el puntaje** | Se usa el número como veredicto, sin mirar el contexto. | Cada puntaje trae su desglose ("¿Por qué?"), los pesos son públicos y la recomendación final siempre es de una persona. |
| **Sesgo hacia las PyMEs grandes** | Siempre ganan las mismas empresas. | División en lotes de tamaño accesible y UTEs entre PyMEs chicas. Ver [sesgos conocidos](limites-y-uso-responsable.md#sesgos-que-conocemos). |
| **Privacidad de datos comerciales** | Se exponen capacidades, equipos o personal de una PyME. | En producción: consentimiento explícito, cada PyME ve y corrige su perfil, y el ranking de un lote lo ven solo la minera convocante y las PyMEs involucradas. Ley 25.326 para datos personales. |
| **La minera no quiere dividir el paquete** | La sugerencia de lotes no se usa. | La lotificación es una sugerencia. Las UTEs sirven también para el paquete completo, y el reporte muestra cuánto compre local se pierde sin dividir. |
| **La UTE no se concreta** | Las PyMEs no llegan a asociarse. | La plataforma explica qué aporta cada socio y genera un borrador de carta de intención. La formalización legal queda a cargo de las empresas. |
| **Cambios en la normativa** | La reglamentación de la ley provincial cambia requisitos o umbrales. | El umbral de personal local es un parámetro (`PORCENTAJE_PERSONAL_SJ_REQUERIDO`) y las metas se muestran como referencia, con su fuente. |
| **Taxonomía incompleta** | Un rubro real no encaja en los 16 definidos. | Validarla con PyMEs y cámaras (issue #14). Agregar un rubro es editar `taxonomia.py`. |
| **Errores en el motor** | Un cambio rompe el cálculo. | Tests automáticos en cada cambio, cobertura cercana al 90 % del backend, y un test que protege el escenario de la demo. |

## Próximos pasos

**Corto plazo (después del hackatón)**
1. Validar la taxonomía y los criterios con PyMEs y cámaras de proveedores (issue #14).
2. Certificaciones que tienen que tener todos los socios de una UTE (issue #11).
3. Base de datos persistente, usuarios y permisos (issue #16).
4. Medir el acierto del sugeridor: palabras clave contra embeddings (issue #12).

**Mediano plazo**
1. Piloto con una minera y una cámara de proveedores, con datos reales y consentimiento.
2. Asignación de capacidad entre lotes con optimización (issue #15).
3. Integración con el Repromin y con los indicadores públicos de compre local, si el Estado
   habilita un mecanismo de intercambio de datos.
