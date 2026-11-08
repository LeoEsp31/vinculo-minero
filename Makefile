.PHONY: ayuda instalar back front test lint datos

ayuda:  ## Lista los comandos disponibles
	@grep -E "^[a-z-]+:.*##" $(MAKEFILE_LIST) | awk -F ":.*## " "{printf \"  %-10s %s\n\", \$$1, \$$2}"

instalar:  ## Instala dependencias de backend y frontend
	cd backend && python -m pip install -e ".[dev]"
	cd frontend && npm install

back:  ## Levanta la API en http://localhost:8000 (docs en /docs)
	cd backend && uvicorn app.main:app --reload

front:  ## Levanta el frontend en http://localhost:5173
	cd frontend && npm run dev

test:  ## Corre los tests del backend
	cd backend && python -m pytest

lint:  ## Lint y tipos (backend y frontend)
	cd backend && ruff check . && mypy app/core
	cd frontend && npm run typecheck && npm run format:check

datos:  ## Regenera los datos de demostración
	cd backend && python scripts/generar_datos_demo.py
