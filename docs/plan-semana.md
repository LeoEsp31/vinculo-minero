# Plan de la semana

**Objetivo:** llegar al hackatón con una demo desplegada, estable y ensayada que cuente una
historia: *"hoy el 2 % de este pliego es alcanzable por PyMEs sanjuaninas; con Vínculo
Minero, el 77 %, y cada número se puede explicar"*.

Lo que ya está hecho (commit inicial): motor completo con tests, API, frontend base, datos
demo, CI, documentación.

## Roles (propuesta: cada uno elige y anota su nombre)

| Rol | Dueño de | Responsable | Revisa a |
|---|---|---|---|
| **A · Motor y datos** | `backend/app/core`, `app/data`, tests | _____ | B |
| **B · API e infraestructura** | `backend/app/api`, CI, deploy | _____ | A |
| **C · Frontend** | `frontend/` | _____ | D |
| **D · Producto y pitch** | `docs/`, guion, video, diapositivas, pruebas de usuario | _____ | C |

Todos defienden todo en la oral: cada uno tiene que poder explicar el scoring, la UTE como
*set cover*, el límite de homologación y la decisión comprar/generar.

## Día a día

| Día | A · Motor | B · API/infra | C · Front | D · Producto |
|---|---|---|---|---|
| 1 | Leer el motor, correr tests, elegir issues | Configurar repo (protección de main, tablero, issues), deploy de prueba | `npm install`, commitear `package-lock.json`, recorrer la UI | Leer docs, verificar `fuentes.md`, borrador del guion |
| 2 | Certificaciones exigidas a todos los socios (#P2) | `POST` pliego/proveedor robustos + tests de API | Matriz de cobertura de la UTE (#P1) | Contactar a 1-2 PyMEs o a la cámara para validar la taxonomía |
| 3 | Evaluación del sugeridor (embeddings vs. palabras clave) | Deploy público estable (URL en README) | Formulario de carga de pliego | Guion de 3 min + estructura del video |
| 4 | Ajustar datos demo con lo validado en el día 2 | Persistencia SQLite (solo si sobra tiempo) | Alta de PyME con sugeridor de rubros | Diapositivas (máx. 3) |
| 5 | Simulador de pesos (backend ya listo) | Monitoreo del deploy, arreglos | Simulador de pesos (sliders) | Grabar el video de 1 min |
| 6 | **Congelamiento de código a la noche.** Solo arreglos | Ídem | Pulido visual, mobile | Ensayo cronometrado ×3 |
| 7 | Ensayo de preguntas de la oral | Plan B: video de la demo por si falla internet | — | Ensayo final |

**Reglas para no romper la demo:** nada se mergea sin CI en verde; después del congelamiento,
solo arreglos con PR; `tests/test_escenario_demo.py` protege la historia del pitch.
