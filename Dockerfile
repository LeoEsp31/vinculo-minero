# Imagen única para el deploy público: la API sirve también la web compilada.
#   docker build -t vinculo-minero .
#   docker run -p 8000:8000 vinculo-minero   →  http://localhost:8000
# Las plataformas (Render, Hugging Face Spaces, Railway, etc.) definen PORT; si no, usa 8000.

FROM node:22-alpine AS web
WORKDIR /web
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 VM_WEB_DIR=/app/web
COPY backend/pyproject.toml ./
COPY backend/app ./app
RUN pip install --no-cache-dir .
COPY --from=web /web/dist ./web

# Usuario sin privilegios (lo exigen algunas plataformas, p. ej. Hugging Face Spaces)
RUN useradd --create-home --uid 1000 vm
USER vm

EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
