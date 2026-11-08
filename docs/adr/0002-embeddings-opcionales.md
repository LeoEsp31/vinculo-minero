# ADR 0002 — IA solo asistiva: embeddings abiertos y opcionales para sugerir rubros

**Estado:** aceptada

## Contexto

Las PyMEs describen lo que hacen con sus palabras ("hacemos montaje de naves"), y el
matching necesita códigos de rubro. Un modelo de lenguaje ayuda a traducir eso, pero si
decide solo, vuelve la caja negra.

## Decisión

- Interfaz única `Sugeridor` con dos implementaciones:
  - `SugeridorPalabrasClave` (por defecto): sin dependencias; devuelve qué palabras coincidieron.
  - `SugeridorEmbeddings` (opcional): modelo **abierto** de *sentence-transformers*
    (`paraphrase-multilingual-MiniLM-L12-v2`) que corre **local**. Se activa con
    `VM_SUGERIDOR=embeddings` y `pip install -e ".[ia]"`.
- El sugeridor **solo sugiere**: una persona confirma el rubro antes de usarlo.

## Consecuencias

- La demo funciona sin GPU, sin internet y sin costos.
- Respecto de la definición de IA de código abierto de la OSI: el código es nuestro y
  abierto, el modelo tiene pesos abiertos y la "información sobre los datos" del modelo
  base es la que publica su autor. Hay que citarla en el informe.
- Pendiente: una evaluación chica (20-30 descripciones etiquetadas a mano) para comparar
  ambos sugeridores con datos, no con intuición.
