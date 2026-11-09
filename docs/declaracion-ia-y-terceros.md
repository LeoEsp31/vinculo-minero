# Declaración de herramientas de IA, software, APIs y componentes de terceros

Entrega de **LIBE** — *Hackeando la Minería* (San Juan, 2026), Desafío 3.

> **Para el equipo antes de entregar:** completar las filas marcadas con ✏️ y borrar este
> recuadro. Cada integrante tiene que declarar qué herramientas de IA usó, incluso las que
> usó solo para escribir textos o preparar el pitch.

## 1. Resumen

- **Vínculo Minero no usa modelos de lenguaje (LLM) para decidir nada.** El puntaje, la
  división en lotes, las UTEs y el reporte de compre local se calculan con reglas y
  algoritmos documentados ([arquitectura](arquitectura.md), [ADR 0001](adr/0001-motor-explicable-sin-llm.md)).
- La única función con IA es **opcional** y **solo sugiere** rubros a partir de texto libre.
  Una persona confirma cada sugerencia ([ADR 0002](adr/0002-embeddings-opcionales.md)).
- La aplicación **no llama a ninguna API externa** mientras funciona.
- Todos los datos son **ficticios** y los generó el equipo con
  `backend/scripts/generar_datos_demo.py`.

## 2. IA dentro del producto

| Componente | Qué hace | ¿Está activo en la demo pública? |
|---|---|---|
| Sugeridor por palabras clave (`SugeridorPalabrasClave`) | Propone rubros comparando palabras de la descripción con la taxonomía y muestra qué palabras coincidieron. Son reglas, no un modelo entrenado. | **Sí** (es el que viene por defecto) |
| Sugeridor por embeddings (`SugeridorEmbeddings`) | Propone rubros comparando el significado del texto con un modelo abierto que corre en el propio servidor. | **No.** Se activa con `VM_SUGERIDOR=embeddings` e instalando el extra `[ia]`. |

Modelo del sugeridor opcional:

| Modelo | Origen | Licencia | Referencia |
|---|---|---|---|
| `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | Hugging Face | Apache-2.0 (según su ficha) | Reimers y Gurevych, *Sentence-BERT*, arXiv:1908.10084 |

Si se activa, los textos de las PyMEs no salen del servidor: el modelo se descarga una vez
y corre localmente.

## 3. IA usada para desarrollar el proyecto

| Herramienta | Proveedor | Para qué se usó | Quién |
|---|---|---|---|
| Claude Code | Anthropic | Asistente de programación: escribir y revisar código, tests, configuración de deploy y documentación técnica (por ejemplo, la matriz de cobertura de la UTE, los formularios de alta, los tests de la API, la imagen de deploy y este documento). | Leandro Espinosa |
| ✏️ | ✏️ | ✏️ (p. ej. redacción del guion, diapositivas, video) | ✏️ |

Cómo se controló lo generado con IA:

- Todo cambio entró por *pull request* con integración continua: tests del motor y de la
  API, lint (`ruff`), tipos (`mypy`, `tsc`), formato (`prettier`) y compilación.
- Los resultados que se muestran en el pitch están protegidos por un test
  (`tests/test_escenario_demo.py`: 1,8 % → 76,8 % en el pliego P001).
- Las fuentes normativas y los datos se verificaron a mano contra la fuente
  ([fuentes](fuentes.md)); la IA no se usó como fuente de datos.

## 4. Software de terceros

Todo el software usado es libre o de código abierto. Versiones de la última compilación.

**Backend (Python 3.12)**

| Componente | Versión | Uso | Licencia |
|---|---|---|---|
| FastAPI | 0.162 | API web | MIT |
| Starlette | 1.10 | Base de FastAPI | BSD-3-Clause |
| Uvicorn | 0.54 | Servidor | BSD-3-Clause |
| Pydantic | 2.14 | Modelos y validación | MIT |
| pytest, pytest-cov | 9.2, 7.1 | Tests (solo desarrollo) | MIT |
| HTTPX | 0.28 | Cliente de tests (solo desarrollo) | BSD-3-Clause |
| Ruff | 0.17 | Lint (solo desarrollo) | MIT |
| mypy | 2.4 | Chequeo de tipos (solo desarrollo) | MIT |
| sentence-transformers | opcional | Sugeridor por embeddings (desactivado en la demo) | Apache-2.0 |

**Frontend**

| Componente | Versión | Uso | Licencia |
|---|---|---|---|
| React, React DOM | 19.3 | Interfaz | MIT |
| Vite, @vitejs/plugin-react | 7.3, 5.2 | Compilación (solo desarrollo) | MIT |
| TypeScript | 5.9 | Tipado (solo desarrollo) | Apache-2.0 |
| Prettier | 3.9 | Formato (solo desarrollo) | MIT |

Las dependencias indirectas quedan fijadas en `frontend/package-lock.json`.

## 5. Servicios y plataformas

| Servicio | Uso |
|---|---|
| GitHub | Repositorio, issues y revisión de código |
| GitHub Actions | Integración continua |
| Render (plan gratuito) | Publicación de la demo: https://vinculo-minero.onrender.com |
| Docker (imágenes oficiales `node:22-alpine` y `python:3.12-slim`) | Imagen de deploy |

## 6. Licencia del proyecto

El código de Vínculo Minero se publica bajo **AGPL-3.0-or-later**
([ADR 0004](adr/0004-licencia-agpl.md)). Según las bases, el equipo conserva la titularidad
de su desarrollo.
