# Cómo trabajamos

## Flujo de Git (GitHub Flow)

1. `main` siempre funciona y está protegida: **nadie pushea directo a `main`**.
2. Cada tarea es un **issue**. Antes de empezar, asignátelo y movelo a *En curso* en el tablero.
3. Creá una rama desde `main` actualizada:
   ```bash
   git switch main && git pull
   git switch -c feat/12-formulario-pliego     # tipo/numero-de-issue-descripcion
   ```
   Tipos: `feat/`, `fix/`, `docs/`, `refactor/`, `test/`, `chore/`.
4. Commits chicos con [Conventional Commits](https://www.conventionalcommits.org/es/):
   ```
   feat(front): formulario de carga de pliego
   fix(motor): no contar dos veces la capacidad de una PyME
   docs: guion del pitch
   ```
5. Abrí un **Pull Request** temprano (puede ser *draft*). Completá la plantilla y enlazá el issue (`Cierra #12`).
6. Se mergea con **CI en verde + 1 aprobación** de otro integrante. Usamos *Squash and merge*.
7. Si `main` avanzó: `git pull --rebase origin main` en tu rama y resolvé conflictos.

> Regla práctica para una semana: PRs de menos de ~300 líneas, que se revisen en el día.

## Reglas de oro del producto

1. **Nada de cajas negras.** Toda recomendación (puntaje, lote, UTE) devuelve su explicación.
2. **No inventamos datos reales.** Solo datos ficticios rotulados `[DEMO]`. Hay un test que lo verifica.
3. **No homologamos.** Nunca decir "homologado" o "certificado" por la plataforma. Decimos "preparación para homologación".
4. **La IA sugiere, la persona decide.**

## Convenciones de código

- **Dominio en español** (pliego, lote, UTE, proveedor), igual que lo hablan los usuarios.
- Backend: Python 3.11+, tipado, `ruff` para lint (`ruff check .`), `mypy app/core`.
  El motor (`app/core`) **no importa nada de FastAPI**: así se testea solo y se puede reutilizar.
- Frontend: TypeScript estricto, Prettier (`npm run format`). Los tipos de `src/api/tipos.ts`
  espejan los modelos de `backend/app/core/modelos.py`.
- Si cambiás el motor, agregá un test. Si cambiás la historia de la demo, actualizá
  `tests/test_escenario_demo.py`.

## Configuración del repositorio (la hace el admin una vez)

- *Settings → Branches → Add rule* para `main`: Require a pull request (1 approval),
  Require status checks (`Backend`, `Frontend`), Require branches to be up to date.
- *Settings → General → Pull Requests*: activar solo **Squash merging** y *Automatically delete head branches*.
- Crear las etiquetas y los issues iniciales: `bash scripts/crear_issues.sh` (necesita `gh auth login`).
- Crear un *Project* (tablero) con columnas: Pendiente · En curso · En revisión · Hecho.
- Completar `.github/CODEOWNERS` con los usuarios reales.
