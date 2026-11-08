# ADR 0003 — Datos en memoria cargados de JSON durante el hackatón

**Estado:** aceptada (revisar después del hackatón)

## Contexto

Tenemos una semana. La demo usa datos ficticios fijos, y lo que hay que mostrar es el motor.

## Decisión

`RepositorioMemoria` carga `app/data/*.json` al iniciar. La API habla con una interfaz
`Repositorio`, así que pasar a SQLite o PostgreSQL es agregar otra implementación sin tocar
el motor ni los endpoints.

## Consecuencias

- Cero configuración: `uvicorn` y listo; tests deterministas.
- Lo que se cree por la API (pliegos, proveedores) se pierde al reiniciar. Aceptable en el prototipo.
