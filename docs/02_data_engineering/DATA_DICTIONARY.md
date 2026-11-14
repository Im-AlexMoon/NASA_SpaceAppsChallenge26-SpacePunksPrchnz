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

## Silver · tablas de datos (`data/silver/tables/`, DE-07, `flamesafe silver`)

Parsers con **specs declarativas** en `src/flamesafe/pipeline/silver_parsers.py`. Si falta una columna de la spec, es error (drift de
esquema). Una columna inesperada no vacía se conserva como texto y genera una advertencia. Los tokens no tipables quedan como
NULL + `<col>__flag` con el token original. Las unidades de la fuente van en el nombre de la columna. Todas las tablas incluyen
`psi_id`, `source_file`, `source_sha256` y `source_row` (fila física, 1-based). Reporte: `data/silver/_reports/tables_parse_report.json`.

| Tabla | Fuente | Filas | Valores marcados (`__flag`) | Notas |
|---|---|---:|---|---|
| `psi159__normal_flames` | ET CFI-G Normal | 179 | `extinction_mode` 46 (`-`), `peak_burner_t_c` 46 (`-`), `tad_k`/`zst` 2 (`#DIV/0!`) | `ignition_outcome` yes/no; `cool_flame_raw` texto |
| `psi159__inverse_flames` | ET CFI-G Inverse | 154 (861 filas vacías descartadas) | `extinction_mode` 15, `color` 24, T pico 2+2 (`-`, `#VALUE!`) | `ignition_outcome` yes/no/**flash** |
| `psi10__normal_flames` | ET Flame Design Normal | 207 | 60 filas × 6 columnas (`RAMP`/`RAMPED`) | sin resultado en la tabla |
| `psi10__inverse_flames` | ET Flame Design Inverse | 120 | 11 filas (`RAMP`/`LOW O2`) | sin resultado en la tabla |
| `psi10__eventdata` | 2 Chamber Calculators `EventData` | 604 eventos | — | `op` = TP (normales) / **INV_TP (inversas)**; `ignite` bool; `tpid` |
| `psi159__eventdata` | Chamber Calculator `EventData` | 675 eventos | `t_end_gmt` 1 | verificación cruzada de `Hot ignition` |
| `psi69__flex_droplets` | ET FLEX (cp1252) | 274 | `d0_mm` 6 y `d_ext_visible_mm` 28 (`–`), `burn_time_s` 2 (`~6`, `~9`) | encabezados O/N/CO renombrados a `x_o2`/`x_n2`/`x_co2`; `burning_rate_k` con unidad dudosa; 1 fila con p = 0 |
| `psi39__cfi_tests` | DataSummary `Master Sheet` | 227 | — | `pressure_raw` ("1 atm") → `p_atm` |
| `psi39__cfi_results` | DataSummary `DATA` | 227 (146 con análisis completo) | — | `k_hot_mm2_s`, `k_cool_mm2_s`, `d_ext_hot_mm`, `d_ext_cool_mm` |
| `psi117__figure_points` | 9 CSV de figuras | 15,861 puntos | — | formato largo; `role` = experiment / model / error_bar / unknown (historias temporales sin etiqueta) |
| `psi117__readme` | ReadMe XLSX | 9 | — | condiciones crudas por archivo; 2 filas con XN2 en % (advertencia) |
| `et__<psi>__<tabla>` (×22) | todas las tablas experimentales | 2–469 | variable | tipado genérico (≥50 % numérico → float) para Compare y RQ5 |

---

## Gold

> **Contrato DS-02 v1 (2026-11-14).** Specs acordadas antes de construir (DE-08). Unidades canónicas según `configs/pipeline.yaml`
> (kPa, K, mg/s, mm, fracción molar). Convierten solo las funciones de `physics/units.py`.

### `gas_flame_tests` (RQ1 · M1/M3)
- **Granularidad:** una fila = una prueba de llama esférica de gas (punto de prueba ACME).
- **Fuentes:** silver `psi159__normal_flames`, `psi159__inverse_flames`, `psi10__normal_flames`, `psi10__inverse_flames`,
  `psi10__eventdata` (resultado `Ignite` de Flame Design; `op` TP = normales, INV_TP = inversas) y `psi159__eventdata` (verificación cruzada).

| Columna | Tipo | Unidad | Origen | Transformación | M/C/L | Nulos | Notas |
|---|---|---|---|---|---|---|---|
| `psi_id`, `campaign` | str | — | — | `CFI-G` / `Flame Design` | L | no | |
| `test_id` | str | — | `Test` | sin espacios, mayúsculas | L | no | clave con `psi_id` |
| `test_day` | int | — | `Day` | — | L | no | grupo de CV |
| `flame_type` | cat | — | `Flame Type` | minúsculas | L | no | normal / inverse |
| `fuel` | cat | — | `Fuel` / `Fuel Type` (EventData) / implícito C2H4 | nombres canónicos | L | no | Flame Design inversa = etileno ambiental |
| `xo2` | float | fracción | normal: `XO2 (init)` / `XO2 before test` · inversa: `XO2` | — | M (control) | no | lado oxidante |
| `xo2_final` | float | fracción | `XO2 (final)` / `XO2 after test` | — | M | sí | |
| `x_fuel` | float | fracción | `Xfuel` / `Xf` / `XC2H4 initial` / `Xf before test` | tokens → flag | M (control) | sí | |
| `p_kpa` | float | kPa | `pmean (atm)` (o `pinit`) / `approx p (bar)` | atm→kPa, bar→kPa | M | no | |
| `po2_kpa` | float | kPa | derivada | `xo2 × p_kpa` | C | no | revisar PHY-04 en inversas |
| `m_fuel_mg_s`, `m_o2_mg_s`, `m_n2_mg_s`, `m_total_mg_s` | float | mg/s | columnas de caudal | tokens `RAMP` → NULL + flag | M (control) | sí | |
| `zst`, `tad_k` | float | —, K | `mean Zst`/`Zst`, `Tad (K)` | `#DIV/0!` → NULL + flag | **C** | sí | nunca en el mismo eje que T medida |
| `ignited` | bool | — | CFI-G `Hot ignition` · FD EventData `Ignite` (`TP` normales, `INV_TP` inversas) | yes/no → bool; `flash` → NULL | M | sí | FD: 207/207 normales y 118/120 inversas unidas |
| `ignition_outcome` | cat | — | ídem | yes / no / flash | M | sí | |
| `outcome_source` | cat | — | — | `experimental_table` / `eventdata` / `none` | L | no | |
| `extinction_mode` | cat | — | `Self-ext or flow term` | SE → self_extinguished, FT → flow_terminated, `-` → NULL | M | sí | solo CFI-G |
| `burn_time_s` | float | s | `burn time (sec)` | — | M | sí | solo CFI-G |
| `cool_flame` | bool | — | `Cool flame?` | empieza con yes/no | M | sí | solo CFI-G normal (8 informadas) |
| `peak_burner_t_k` | float | K | `Peak burner T (C )` / `Peak burner temp (K)` | °C → K | M | sí | |
| `qualifier` | str | — | tokens `RAMP`, `RAMPED`, `LOW O2` | — | L | sí | prueba no estacionaria |
| `source_file`, `source_row` | str, int | — | — | — | L | no | procedencia |

### `droplet_tests` (RQ2 · M2)
- **Granularidad:** una fila = una prueba de gota (FLEX o CFI).
- **Fuentes:** silver `psi69__flex_droplets` y `psi39__cfi_tests` ⋈ `psi39__cfi_results` (por `flex_number`).

| Columna | Tipo | Unidad | Origen | Transformación | M/C/L | Nulos | Notas |
|---|---|---|---|---|---|---|---|
| `psi_id`, `campaign`, `test_id` | str | — | `FLEX Test #` / `Flex Number` | — | L | no | |
| `test_date` | date | — | `Test Date` | — | L | sí | grupo de CV |
| `fuel` | cat | — | `Fuel` | nombres canónicos | L | no | |
| `p_kpa` | float | kPa | FLEX `Ambient pressure; mmHg` · CFI `Pressure` ("1 atm") | mmHg→kPa, atm→kPa | M | no | p = 0 → error |
| `x_o2`, `x_n2`, `x_co2`, `x_he` | float | fracción | FLEX `O/N/CO/He initial…` · CFI `Oxygen/Nitrogen/Helium` | encabezados FLEX sin subíndice (renombrado explícito) | M (control) | no | CFI sin CO₂ → 0 explícito solo si la fuente lo implica (no imputar) |
| `d0_mm` | float | mm | `Droplet initial diameter; mm` / `D0 ( mm )` | `–` → NULL + flag | M | sí | |
| `fiber` | bool | — | CFI `Fiber` | — | L | sí | FLEX NULL |
| `test_end` | cat | — | FLEX `Test end` | extinction / disruption / completion | M | sí | CFI NULL |
| `d_ext_hot_mm` | float | mm | FLEX `Visible flame extinction diameter` · CFI `Dext, hot` | — | M | sí | |
| `d_ext_cool_mm` | float | mm | CFI `Dext,cool` | `NaN` literal → NULL + flag | M | sí | |
| `k_hot_mm2_s` | float | mm²/s | CFI `khot` · FLEX `Burning rate` (si PHY confirma R-DE-05b) | — | M | sí | |
| `k_cool_mm2_s` | float | mm²/s | CFI `kcool` | — | M | sí | |
| `burn_time_s` | float | s | FLEX `Burn time; s` · CFI `HF Burn Time` | `~6` → NULL + flag | M | sí | |
| `reignitions` | int | — | CFI `Reignitions` | — | M | sí | |
| `analysis_complete` | bool | — | CFI `Completed Analysis?` | — | L | sí | |

### `droplet_reference_points` (validación de M2)
- **Granularidad:** un punto de figura publicada (PSI-117), en formato largo: `data_file`, `block`, `role` (experiment / model / unknown),
  `x_name`, `x`, `y_name`, `y`, más las condiciones del ReadMe (`fuel`, `d0_mm`, `p_atm`, `xo2`, `doi`, `figure`).
  **Los puntos `model` nunca se usan como mediciones.**

### `investigations` (RQ5)
- **Granularidad:** una investigación (24). Une silver `catalog/investigations` con el triage (`configs/triage.yaml`): R1–R6, score,
  tier, pilares, entornos, RQ. Añade `hardware_family` normalizado (CIR-ACME, CIR-MDCA, MSG, Saffire-Cygnus, SAME, otro).
