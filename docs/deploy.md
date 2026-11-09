# Deploy público

La demo se publica como **un solo servicio**: el `Dockerfile` de la raíz compila la web
(React) y la API (FastAPI) la sirve junto con `/api` y `/docs`. Un dominio, sin CORS ni
variables de entorno obligatorias.

```bash
docker build -t vinculo-minero .
docker run -p 8000:8000 vinculo-minero      # http://localhost:8000
```

Sin Docker se puede probar igual: `cd frontend && npm run build`, y después
`cd backend && VM_WEB_DIR=../frontend/dist uvicorn app.main:app` → http://localhost:8000.

## Opción recomendada: Render (conecta con GitHub, plan gratuito)

1. Entrar a [render.com](https://render.com) con la cuenta de GitHub del dueño del repo.
2. *New → Blueprint* y elegir `vinculo-minero`. Render lee `render.yaml` y crea el servicio.
3. Esperar el primer build (unos minutos) y copiar la URL `https://….onrender.com` al README.
4. Cada merge a `main` vuelve a desplegar solo.

Verificar en la web de Render las condiciones vigentes del plan gratuito. Lo importante para
la demo:

- **El servicio gratuito se duerme si nadie lo usa** y tarda en despertar. Abrir la URL unos
  minutos antes del pitch y tener a mano el video de la demo (plan B).
- **Los datos cargados desde los formularios viven en memoria** (ADR 0003): se pierden cuando
  el servicio se reinicia o se duerme. Los datos demo (P001, P002 y las 28 PyMEs) siempre
  vuelven a estar.

## Otras plataformas

La imagen escucha en `$PORT` (o 8000) y corre con un usuario sin privilegios, así que sirve
para cualquier plataforma que acepte un `Dockerfile` (Railway, Fly.io, Hugging Face Spaces,
etc.). Revisar en cada una cómo se indica el puerto.

## Checklist antes de la presentación

- [ ] La URL abre la lista de pliegos y P001 muestra **1,8 % → 76,8 %**.
- [ ] `/docs` abre la documentación de la API.
- [ ] "Cargar un pliego → Completar con un ejemplo → Guardar" funciona.
- [ ] La URL está en el README y en la entrega.
