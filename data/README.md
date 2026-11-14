# data/

Capas medallion **reproducibles** — nada aquí se versiona salvo `sample/` y este README.

| Capa | Contenido | Formato | Quién escribe |
|---|---|---|---|
| `bronze/` | Copias crudas e inmutables de PSI + sidecar `.meta.json` (url, fecha, http, bytes, sha256). Respuestas JSON del API tal cual. | original | `flamesafe catalog`, `flamesafe bronze` |
| `silver/` | Una tabla por tabla fuente: tipada, limpia, unidades explícitas, flags de faltantes, columnas de procedencia. | Parquet | `flamesafe silver` |
| `gold/` | Tablas armonizadas listas para análisis/modelos/dashboard, definidas por las preguntas de investigación. | Parquet + DuckDB | `flamesafe gold` |
| `external/` | Insumos no-PSI (abstracts de publicaciones, estándares) con su fuente. | varios | manual / scripts |
| `sample/` | Fixtures diminutos para tests (< 1 MB total). **Sí se versiona.** | csv/json | manual |

Regenerar todo: `make pipeline` (o `flamesafe catalog && flamesafe bronze && flamesafe silver && flamesafe gold`).
Detalle: [docs/02_data_engineering/PIPELINE_MEDALLION.md](../docs/02_data_engineering/PIPELINE_MEDALLION.md).
