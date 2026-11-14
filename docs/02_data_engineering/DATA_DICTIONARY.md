# Data dictionary

> Tarea DE-10. Las tablas gold **se documentan antes de construirse** (contrato DS→DE, tarea DS-02) y este archivo se actualiza
> con cada cambio. Las tablas silver del catálogo (DE-03) ya están documentadas abajo.

## Convenciones
- Nombres `snake_case`, sufijo de unidad: `_kpa`, `_k`, `_cm_s`, `_mg_s`, `_mm`, `_s`, `_bytes`; fracción molar `_xo2` (0–1).
- `__flag`: token original cuando el valor es NULL o no numérico.
- `is_computed`: la fuente lo calculó (no es medición directa).
- Procedencia mínima en toda tabla: `psi_id` + (`source_file`, `source_sha256`) y, en tablas de datos, `source_row`.
- Strings vacíos → NULL. Nada se imputa.

## Matriz de comparabilidad (llenar en F1/F2 con PHY)

| Concepto | Investigación A (col, unidad, medido/calc.) | Investigación B | ¿Comparable? | Regla |
|---|---|---|---|---|
| Oxígeno | | | | XO₂ ↔ %vol convertible explícitamente |
| Presión | | | | todo a kPa |
| Temperatura | | | | medida ≠ calculada: nunca en el mismo eje sin etiqueta |
| Flujo | | | | caudal másico ≠ velocidad sin geometría |

---

## Silver · catálogo (`data/silver/catalog/`, DE-03, `flamesafe silver`)

Fuente: snapshot bronze `data/bronze/catalog/snapshot_*/` (JSON del API PSI). Columnas de procedencia comunes a todas las
tablas: `snapshot`, `source_file` (`PSI-XX.json`) y `source_sha256`.

### `investigations` — 1 fila = 1 investigación (24)

| Columna | Tipo | Origen PSI | Notas |
|---|---|---|---|
| `psi_id` | str | `accession` del manifest | clave |
| `acronym`, `title` | str | `investigationAcronym`, `title` | 5 registros de tierra sin acrónimo |
| `doi` | str | `doi` | normalizado: minúsculas, sin prefijo `https://doi.org/` |
| `research_area`, `sub_research_area` | str | `researchArea`, `subResearchArea` | sub-área con texto libre inconsistente |
| `project_type`, `is_ground_investigation` | str, bool | `projectType` | ground = PSI-60, 62, 115, 117 y 142 |
| `flight_program` | str | `flightProgram` | |
| `flight_platform` | str | búsqueda `Flight Platform` | ⚠️ SAFFIRE-I/III dicen ISS, pero el hardware dice Cygnus |
| `experiment_hardware`, `experiment_hardware_link` | str | `experimentHardware(Link)` | texto libre **no normalizado**: requiere `hardware_family` en gold (CIR/MDCA/MSG/Saffire…) |
| `managing_center`, `keywords` | str | `managingNasaCenter`, búsqueda `Keywords` | |
| `related_investigations` | list[str] | `related_glds` | PSI-IDs únicos, ordenados |
| `start_date`, `end_date` | timestamp | `investigationStartDate/EndDate` (MM-DD-YYYY) | inválida → NULL + issue |
| `release_date`, `modified_date` | timestamp | `releaseDate`, `modifiedDate` (DD-Mon-YYYY) | |
| `record_version`, `version_reason` | int, str | `version`, `versionReason` | |
| `license_id`, `license_name` | str | `licenseIdentifier`, `licenseName` | CC0-1.0 en 23/24; PSI-10 vacío |
| `objective`, `approach`, `hypothesis`, `research_impacts`, `description` | str | ídem | corpus para RAG y ranking |
| `n_added_files`, `n_removed_files`, `n_experimental_tables`, `n_tables_not_in_added` | int | conteos de `added`, `removed`, `experimentalTable` | |
| `n_publications`, `n_publications_with_doi` | int | `publications` | |
| `added_bytes` | int | Σ `added[].file_size` | bytes realmente expuestos |
| `registered_total_bytes` | int | `totalFileSize` | ≠ `added_bytes` (registrado vs expuesto) |
| `access_status` | str | derivado | `available` / `experimental_table_only` / `no_public_files` |

### `files` — 1 fila = 1 archivo listado (27,076)

| Columna | Tipo | Origen | Notas |
|---|---|---|---|
| `psi_id`, `file_name` | str | `added[]`/`removed[]` | |
| `inventory` | str | lista de origen | `added` (actual) / `removed` (histórico, **no** descargable como actual) |
| `category` | str | carpeta en `remote_path` | `Raw Data`, `Analyzed Data`, `Engineering Documents`, `Reference Data`, `Experimental table`… |
| `extension` | str | `file_name` | minúsculas |
| `file_bytes` | float | `file_size` | |
| `file_version`, `restricted`, `visible` | int, bool, bool | ídem | |
| `is_experimental_table` | bool | nombre ∈ `experimentalTable` | |
| `date_created`, `date_modified` | timestamp UTC | `{"$date": ms}` | |
| `remote_path` | str | ídem | ruta lógica en PSI; base para el manifest de descarga (DE-05/06) |

### `experimental_tables` — 1 fila = 1 tabla curada (22)

`psi_id`, `file_name`, `extension`, `listed_bytes`, `in_added` (14 son `False`: solo existen en `experimentalTable`), `restricted`,
`subcategory`, `date_modified`, `remote_path`.

### `publications` — 1 fila = 1 publicación ligada a un registro (352)

`psi_id`, `pub_index` (orden en el registro), `title`, `doi` (normalizado; 284 con DOI), `author_list` (texto tal cual),
`status` (`published` en las 352), `pubmed_id`.
Una misma publicación puede aparecer en varios registros: deduplicar por `doi` en gold.

### `contacts` — 1 fila = 1 investigador listado (86)

`psi_id`, `first_name`, `mid_initials`, `last_name`, `affiliation`, `roles` (separados por `; `).
**Privacidad:** se descartan `email`, `phone`, `fax` y `address` del JSON crudo. Un test verifica que no lleguen a silver.

---

## Gold

### `<tabla_gold>`
- **Granularidad:** una fila = …
- **Fuente(s):** PSI-XX `<archivo>`
- **Filtros aplicados:**

| Columna | Tipo | Unidad | Origen (col. fuente) | Transformación | Medida/Calc./Log | Nulos permitidos | Notas |
|---|---|---|---|---|---|---|---|
