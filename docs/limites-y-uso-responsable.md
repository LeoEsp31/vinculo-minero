# Límites del desafío y uso responsable

## Límite del desafío: "No reemplaza los procesos de homologación"

| Lo que **sí** hace | Lo que **no** hace |
|---|---|
| Sugiere lotes, rankea y propone alianzas | No adjudica contratos |
| Muestra brechas ("te falta ISO 45001 vigente") | No certifica ni homologa a nadie |
| Genera un **borrador** de carta de intención | No genera documentos con validez legal |
| Estima la condición de proveedor local | No reemplaza la inscripción en el Repromin |
| Estima el % de compre local de un pliego | No audita el cumplimiento de la ley |

Cómo se garantiza en el producto:
- La etapa 4 se llama **"Preparación para homologación"**.
- Banner permanente en la UI y aviso en cada checklist, carta y reporte.
- Revisión de PR: casilla "no usé las palabras homologado/certificado".

## Datos

- **Prototipo:** 100 % ficticios, rotulados `[DEMO]` / `[FICTICIO]`. Un test falla si
  aparece un registro sin rótulo.
- **En producción:** los perfiles de las PyMEs son datos comerciales sensibles (capacidad,
  equipos, personal). Principios: consentimiento explícito de la PyME, que cada PyME vea y
  corrija su perfil, y que el ranking de un lote lo vean solo la minera convocante y las
  PyMEs involucradas. A tener en cuenta la Ley 25.326 de Protección de Datos Personales
  para los datos de personas.

## IA

- La IA no toma decisiones: solo sugiere rubros desde texto libre y muestra su evidencia.
- Todo lo que decide algo (puntaje, apto o no apto, lotes, UTEs) es determinista y
  explicable, con pesos públicos.
- Si se activa el sugeridor por embeddings, el modelo es abierto y corre local: los textos
  de las PyMEs no salen del servidor.

## Sesgos que conocemos

- Favorecer siempre a las PyMEs más grandes: mitigado con la lotificación (lotes de tamaño
  accesible) y las UTEs.
- Penalizar a quien no cargó bien su perfil: el checklist muestra qué falta, en vez de
  esconderlo en un número.
- Los pesos los define el equipo: por eso son públicos y la API permite probar otros
  (`POST /api/pliegos/{id}/analisis`).
