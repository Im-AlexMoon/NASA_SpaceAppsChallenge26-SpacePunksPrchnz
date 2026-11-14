# ADR-0003 — Uso del repositorio de referencia `YoussefHegazy74/flame-in-freefall`

- **Estado:** Propuesto (ratificar en G0)
- **Tarea relacionada:** PM-03

## Contexto
El repositorio <https://github.com/YoussefHegazy74/flame-in-freefall> (equipo AFAQ) documenta con mucho detalle el API de PSI,
el inventario de las 24 investigaciones, problemas de formato (tokens `#DIV/0!`, `RAMP`, unidades mixtas, 404s) y una matriz de
comparabilidad. Es muy valioso para acelerar F1. Su propio `DATA_SOURCES.md` indica que **no tiene licencia de código seleccionada**
(snapshot 2026-11-08), lo que por defecto significa "todos los derechos reservados" sobre su código y su texto.

## Decisión
1. **Lo usamos como mapa**: endpoints, nombres de archivos, advertencias de formato y preguntas abiertas guían nuestra exploración.
2. **No copiamos código ni texto**. Nuestro pipeline se implementa desde cero; nuestra documentación se redacta con nuestras palabras.
3. **Re-verificamos cada hecho** (conteos, tamaños, checksums, 404s) contra el API en vivo y lo registramos con fecha en
   [DATA_SOURCES.md](../../02_data_engineering/DATA_SOURCES.md). Si algo difiere, gana el API.
4. **Citamos** el repositorio en `docs/REFERENCES.md` y en la sección Methods & Sources del dashboard.

## Consecuencias
Aceleramos el descubrimiento sin riesgo de propiedad intelectual ni de heredar errores. Nuestra re-verificación también es un
entregable de valor (log de verificación reproducible).
