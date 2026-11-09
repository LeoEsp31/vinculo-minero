# Vínculo Minero

**Vinculación explicable entre la demanda minera y las PyMEs proveedoras de San Juan.**

**Demo en línea:** https://vinculo-minero.onrender.com · API: https://vinculo-minero.onrender.com/docs
(plan gratuito: si estuvo un rato sin uso, la primera carga puede tardar).

> Prototipo para el hackatón *Hackeando la Minería* (Ciclo Pilares San Juan, 2026) —
> Desafío 3: *Mapeo y vinculación de proveedores locales*.
> Todos los datos del repositorio son **ficticios**. La plataforma **no reemplaza** los
> procesos de homologación de las empresas mineras ni la inscripción en el Repromin.

---

## El problema

San Juan fijó objetivos de **60 % de compras a proveedores sanjuaninos y 80 % de empleo
local** para los grandes proyectos mineros, creó un registro de proveedores con requisitos
de arraigo (**Repromin**) y obliga a las mineras a publicar sus planes de demanda. A nivel
nacional, los proyectos adheridos al **RIGI** deben presentar un plan de proveedores locales
por al menos el **20 %** del monto de inversión destinado a proveedores. Ver
[docs/fuentes.md](docs/fuentes.md).

Pero un registro no alcanza. Las mineras suelen publicar **paquetes grandes** que ninguna
PyME local puede cubrir sola, y las PyMEs no saben **con quién asociarse** ni **qué les falta**
para presentarse. El resultado: aunque haya capacidad local, el contrato se va afuera.

## La solución

| Paso | Qué hace | Para quién |
|---|---|---|
| **1. Lotificación sugerida** | Separa del paquete solo lo que bloquea a las PyMEs locales: volúmenes demasiado grandes (se dividen) o requisitos que nadie local tiene. | Minera |
| **2. Calificación explicable** | Puntaje 0-100 con **pesos públicos** y desglose por criterio, más filtros excluyentes (certificaciones vigentes, equipos, experiencia). | Minera y PyME |
| **3. Motor de alianzas** | Si ninguna PyME cubre un lote, busca **UTEs de 2 o 3 PyMEs locales** complementarias y explica qué aporta cada una. | PyMEs |
| **4. Preparación para homologación** | Checklist de brechas por PyME, borrador de carta de intención para la UTE y **reporte de compre local** frente a las metas provincial y RIGI. | Todos |

**Lo que nos diferencia: es una caja de cristal.** Cada puntaje, cada lote y cada alianza
viene con su explicación en lenguaje claro. La PyME sabe *por qué* quedó donde quedó
(know-why, no solo know-how).

### Resultado en la demo (pliego ficticio P001)

```
Hoy (paquetes originales, PyMEs solas):      1,8 % del monto alcanzable por PyMEs sanjuaninas
Con lotes sugeridos + UTEs locales:          76,8 %
```

## Cómo correrlo

Requisitos: Python 3.11+ y Node 22+.

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload        # API en http://localhost:8000 · docs en /docs

# Frontend (otra terminal)
cd frontend
npm install
npm run dev                          # http://localhost:5173
```

Con Docker: `docker compose up --build` → http://localhost:8080

Deploy público (un solo servicio, web + API): ver [docs/deploy.md](docs/deploy.md).

Atajos: `make ayuda`, `make test`, `make lint`.

## Estructura

```
backend/
  app/core/        Motor de dominio (Python puro, sin dependencias de la web)
    taxonomia.py     Rubros, certificaciones y equipos (el idioma común)
    modelos.py       Modelos pydantic
    lotes.py         1. Lotificación sugerida
    scoring.py       2. Calificación explicable
    alianzas.py      3. UTEs (cobertura de conjuntos)
    preparacion.py   4. Checklist de brechas y carta de intención
    analisis.py      Orquestación + reporte de compre local
    sugeridor.py     IA asistiva: sugiere rubros desde texto libre
  app/api/         FastAPI (rutas + servicio)
  app/data/        Datos de demostración (generados por scripts/)
  tests/
frontend/          React + Vite + TypeScript
docs/              Arquitectura, decisiones (ADR), límites, fuentes, plan
```

## Uso responsable de datos e IA

- El matching se hace con **reglas y algoritmos documentados**, no con un modelo de lenguaje.
- La IA (opcional, modelo abierto que corre local) **solo sugiere** rubros a partir de texto
  libre, muestra la evidencia, y una persona confirma.
- Los pesos del puntaje son **públicos** (`GET /api/pesos` y la página *Cómo calculamos*).
- Datos 100 % ficticios en el prototipo. Ver [docs/limites-y-uso-responsable.md](docs/limites-y-uso-responsable.md).

## Documentación

- [Arquitectura](docs/arquitectura.md)
- [Decisiones de diseño (ADR)](docs/adr/)
- [Plan de la semana y roles](docs/plan-semana.md)
- [Guion de la demo y el pitch](docs/guion-demo.md)
- [Supuestos, riesgos y próximos pasos](docs/riesgos-y-proximos-pasos.md)
- [Declaración de IA y componentes de terceros](docs/declaracion-ia-y-terceros.md)
- [Deploy](docs/deploy.md)
- [Cómo contribuir](CONTRIBUTING.md)

## Equipo

Estudiantes de la FCEFN — Universidad Nacional de San Juan, cátedra *Aspectos Profesionales y Sociales*:
Baltazar Bustos Fierro Medina · Enzo Darío Arrabal Fajardo · Nicolás Ignacio Flores · Leandro Rubén Espinosa.

## Licencia

[AGPL-3.0-or-later](LICENSE): software libre con copyleft, también cuando se ofrece como
servicio web. Ver [docs/adr/0004-licencia-agpl.md](docs/adr/0004-licencia-agpl.md).
