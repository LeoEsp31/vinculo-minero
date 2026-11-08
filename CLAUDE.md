# Vínculo Minero — contexto para Claude Code

Proyecto de hackatón (*Hackeando la Minería*, San Juan 2026, Desafío 3: vinculación de
proveedores locales) y trabajo práctico de la cátedra *Aspectos Profesionales y Sociales*
(FCEFN-UNSJ). Equipo de 4 estudiantes. Responder en español rioplatense (voseo).

## Qué hace

Vincula pliegos de mineras con PyMEs sanjuaninas en 4 pasos: (1) sugiere dividir paquetes
grandes en lotes accesibles, (2) puntúa cada PyME con pesos públicos y explica el puntaje,
(3) si ninguna PyME cubre un lote, arma UTEs de 2-3 PyMEs locales (cobertura de conjuntos),
(4) checklist de "preparación para homologación" y reporte de compre local (meta provincial
60 %, RIGI 20 %). Detalle: `README.md` y `docs/arquitectura.md`.

## Reglas que no se rompen

- **Nada de cajas negras:** todo resultado del motor trae su explicación.
- **No homologamos:** nunca decir "homologado"/"certificado" por la plataforma (límite del desafío).
- **Solo datos ficticios** rotulados `[DEMO]`/`[FICTICIO]` (hay un test que lo verifica).
- **No inventar fuentes:** la cátedra descuenta 10 puntos por dato o fuente inventada. Ver `docs/fuentes.md`.
- La IA solo sugiere rubros; el matching es determinista (ADR 0001 y 0002 en `docs/adr/`).

## Comandos

```bash
cd backend && pip install -e ".[dev]"     # instalar
cd backend && python -m pytest            # tests
cd backend && ruff check . && mypy app/core
cd backend && uvicorn app.main:app --reload   # API :8000, docs en /docs
cd frontend && npm install && npm run dev     # web :5173 (proxy /api → :8000)
cd frontend && npm run typecheck && npm run format:check
```

## Estructura y convenciones

- `backend/app/core/`: motor en Python puro (no importa FastAPI). Si lo cambiás, agregá tests.
- `backend/app/api/`: FastAPI. `frontend/src/api/tipos.ts` espeja `backend/app/core/modelos.py`.
- `backend/tests/test_escenario_demo.py` protege la historia del pitch (1,8 % → 76,8 % en P001).
- Datos demo: se generan con `backend/scripts/generar_datos_demo.py` (no editar los JSON a mano).
- Git: GitHub Flow. Rama `tipo/numero-issue-descripcion`, Conventional Commits, PR con CI en
  verde y 1 aprobación. Ver `CONTRIBUTING.md`. Backlog en los issues de GitHub (P1 primero).
- Plan de la semana y roles: `docs/plan-semana.md`. Guion del pitch: `docs/guion-demo.md`.
