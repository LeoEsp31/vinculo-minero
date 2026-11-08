# ADR 0001 — Motor de matching explicable, sin modelo de lenguaje (generar, no comprar)

**Estado:** aceptada

## Contexto

El producto de referencia que analizamos en el Práctico 2 (plataforma de matching con IA)
es una **caja negra**: la PyME ve su puntaje, pero no sabe por qué lo obtuvo ni qué hacer
para mejorarlo (tiene *know-how* pero no *know-why*). Además, depender de una API
propietaria implica costos por uso, dependencia tecnológica externa y enviar datos
comerciales de las PyMEs a terceros.

## Decisión

El núcleo (lotificación, scoring y UTEs) se implementa con **reglas y algoritmos propios,
documentados y testeados**. Cada resultado devuelve su explicación. Los pesos son públicos.

## Consecuencias

- **Ganamos:** explicabilidad total, resultados reproducibles, sin costo por consulta, sin
  enviar datos a terceros, y capacidad tecnológica local (transferencia endógena).
- **Perdemos:** más trabajo de diseño y mantenimiento de reglas; menos flexibilidad para
  entender texto libre (eso lo cubre el sugeridor opcional, ADR 0002).
