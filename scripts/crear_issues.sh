#!/usr/bin/env bash
# Crea etiquetas e issues iniciales del backlog en el repo actual de GitHub.
# Requisitos: GitHub CLI (`gh`) y `gh auth login`. Uso: bash scripts/crear_issues.sh
set -euo pipefail

etiqueta() { gh label create "$1" --color "$2" --description "$3" --force >/dev/null; }

etiqueta "motor"    "b4652a" "backend/app/core: lotes, scoring, UTEs"
etiqueta "api"      "1d76db" "backend/app/api"
etiqueta "frontend" "5319e7" "frontend/"
etiqueta "infra"    "0e8a16" "CI, deploy, Docker"
etiqueta "ia"       "c5def5" "Sugeridor y embeddings"
etiqueta "docs"     "fef2c0" "Documentación y fuentes"
etiqueta "pitch"    "f9d0c4" "Video, diapositivas, guion"
etiqueta "P1"       "d73a4a" "Imprescindible para la demo"
etiqueta "P2"       "fbca04" "Suma puntos si llegamos"
etiqueta "P3"       "c2e0c6" "Después del hackatón"

issue() { gh issue create --title "$1" --label "$2" --body "$3" >/dev/null && echo "✔ $1"; }

issue "Commitear package-lock.json y usar npm ci en CI" "infra,P1" \
"Después del primer \`npm install\`, commitear \`frontend/package-lock.json\` y en \`.github/workflows/ci.yml\` cambiar a \`npm ci\` con \`cache: npm\`."

issue "Deploy público de backend y frontend" "infra,P1" \
"Publicar la demo con una URL estable y ponerla en el README. Opción simple: un solo servicio con Docker (\`docker compose\`) o backend y frontend por separado (definir \`VITE_API_URL\`). Tener un plan B grabado."

issue "Formulario de carga de pliego" "frontend,P1" \
"Formulario para crear un pliego con ítems (paquete, rubro, cantidad, monto, certificaciones, maquinaria, experiencia, dotación). Selects alimentados por \`GET /api/taxonomia\`. Envía \`POST /api/pliegos\` y redirige al análisis."

issue "Alta de PyME con sugeridor de rubros" "frontend,P1" \
"Formulario de perfil de PyME. El campo de descripción llama a \`POST /api/sugerir-rubros\` y propone rubros con su evidencia; el usuario confirma. Envía \`POST /api/proveedores\`."

issue "Tests de la API para alta de pliego y proveedor" "api,P1" \
"Casos: alta válida (201), id duplicado (409), rubro o certificación inexistente (422)."

issue "Verificar fuentes y completar número de ley provincial" "docs,P1" \
"Revisar cada enlace de \`docs/fuentes.md\`, completar el número de la Ley de Desarrollo Local Minero y el artículo exacto del RIGI contra el texto oficial."

issue "Guion del pitch y video de 1 minuto" "pitch,P1" \
"Partir de \`docs/guion-demo.md\`. Video con los integrantes hablando (no diapositivas), subido a Drive con acceso público."

issue "Diapositivas (máximo 3)" "pitch,P1" \
"Problema → solución (con captura del reporte 1,8 % → 76,8 %) → por qué nosotros (explicable, libre, local)."

issue "Simulador de pesos en la UI" "frontend,P2" \
"Sliders para los 6 pesos (que sumen 100 %) que llaman a \`POST /api/pliegos/{id}/analisis\` y muestran cómo cambia el ranking. Refuerza el mensaje de transparencia."

issue "Certificaciones exigidas a todos los socios de la UTE" "motor,P2" \
"Hoy una certificación se cubre si la tiene al menos un socio. Agregar un atributo por certificación (p. ej. ISO 45001 la deben tener todos) y respetarlo en \`alianzas.py\` y en el checklist. Con tests."

issue "Evaluación del sugeridor: palabras clave vs. embeddings" "ia,P2" \
"Etiquetar a mano 20-30 descripciones de PyMEs, medir acierto top-1 y top-3 de ambos sugeridores y documentarlo en ADR 0002. Da know-why para la defensa."

issue "Vista 'Mi empresa': lotes a los que puedo presentarme" "frontend,P2" \
"Para una PyME, listar los lotes donde es apta o casi apta, con su checklist de preparación."

issue "Validar la taxonomía con PyMEs o una cámara de proveedores" "docs,P2" \
"Mostrar rubros, certificaciones y equipos a 1-2 actores reales y ajustar. Documentar qué cambió (sin publicar datos de las empresas)."

issue "Asignación global de capacidad entre lotes" "motor,P3" \
"Hoy es greedy por orden de lotes. Explorar programación lineal entera o una heurística mejor."

issue "Persistencia en SQLite/PostgreSQL" "api,P3" \
"Implementar otra versión de \`Repositorio\` (ver ADR 0003) sin tocar el motor."

issue "ESLint y tests de componentes (Vitest)" "frontend,P3" \
"Configurar lint de React y tests básicos de los componentes principales."

echo "Listo."
