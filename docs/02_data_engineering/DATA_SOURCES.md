# Fuentes de datos y log de verificación

> Fuente de verdad de **cómo** obtenemos los datos y **qué verificamos, cuándo**. Ningún conteo se escribe aquí sin haberlo
> obtenido del API (tarea DE-01/DE-02). El repositorio de referencia se usa solo como guía (ADR-0003).

## 1. NASA Physical Sciences Informatics (PSI)

| Recurso | URL |
|---|---|
| Portal | <https://psi.nasa.gov> |
| Repositorio UI | <https://psi.nasa.gov/physci/repo> |
| Investigación (UI) | `https://psi.nasa.gov/physci/repo/data/investigations/{PSI-ID}` |

### Endpoints del API público (configurados en `configs/sources.yaml`)

| Uso | Método + ruta (base `https://psi.nasa.gov/geode-py/ws`) | Verificado (fecha, HTTP) |
|---|---|---|
| Búsqueda de investigaciones | `GET /repo/search?source=psi&type=investigation&size=200&from=0` | ☐ |
| Detalle de investigación | `GET /repo/investigations/{PSI-ID}` | ☐ |
| Descarga de archivo | `GET /studies/{PSI-ID}/download?file={nombre url-encoded}` | ☐ |

Campos relevantes del detalle (a confirmar): metadatos (título, acrónimo, DOI, área, objetivos, enfoque, publicaciones),
`added` (inventario actual de archivos), `experimentalTable` (tablas curadas — pueden **no** estar en `added`), `removed`, `totalFileSize`.

Advertencias conocidas a re-verificar: archivos listados que devuelven 404; registros con 0 archivos `added` pero con tabla
experimental (`experimental_table_only`); `totalFileSize` ≠ suma de archivos expuestos.

## 2. Fuentes complementarias

| Fuente | Uso | URL |
|---|---|---|
| Publicaciones (DOI) listadas en cada registro PSI | Corpus RAG, interpretación física | vía DOI |
| NASA Technical Reports Server (NTRS) | Reportes técnicos SAFFIRE, BASS, FLEX | <https://ntrs.nasa.gov> |
| Páginas de experimentos NASA GRC | Contexto de hardware y objetivos | <https://www.nasa.gov/glenn/> |
| Repositorio de referencia (AFAQ) | Mapa de exploración — no se copia | <https://github.com/YoussefHegazy74/flame-in-freefall> |

## 3. Log de verificación

| Fecha/hora | Quién | Qué se verificó | Resultado | Evidencia (archivo/commit) |
|---|---|---|---|---|
| | | Total de investigaciones / de combustión | | |
| | | 24 detalles HTTP 200 | | |
| | | Tablas experimentales descargables | | |
| | | Archivos con 404 | | |

## 4. Atribución
Los datos son de NASA PSI y se citan por PSI-ID y DOI. No redistribuimos archivos crudos en el repositorio. No implicamos aval de NASA.
