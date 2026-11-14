# Data dictionary

> Tarea DE-10 (**cerrada 2026-11-14**). Las tablas gold se documentan antes de construirse (contrato DS→DE, DS-02) y este archivo se
> actualiza con cada cambio. **`flamesafe validate` falla si alguna columna gold no está documentada aquí o si se documenta una que no existe.**

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

> **Construido en DE-08 (2026-11-14)** con `flamesafe gold` → `data/gold/*.parquet` + `data/gold/flamesafe.duckdb`.
> Filas: `gas_flame_tests` 660 · `droplet_tests` 501 · `droplet_reference_points` 15,861 · `investigations` 24 · `publications` 303.
> Reporte: `data/gold/_reports/gold_report.json` (reconciliación, verificaciones cruzadas, invariantes).
>
> ⚠️ **Semántica de `ignited` (R-DE-08a).** En CFI-G viene de `Hot ignition`. En Flame Design viene del `Ignite` de EventData, que es
> una **decisión operativa** sobre si se consumió el gas, no una medición de ignición caliente. En CFI-G ambas fuentes coinciden en
> 279/323 pruebas (86 %). En 42 casos la tabla dice "ignición caliente sí" y EventData dice "no"; son llamas breves (mediana 5 s frente a
> 40 s de las concordantes). En Flame Design, `ignited` es casi constante (323 sí / 2 no). **No mezclar campañas** en un modelo de
> ignición sin usar `outcome_source` como variable o sin una decisión de PHY.
>
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
| `p_source` | cat | — | — | `approx p (bar)` / `pmean (atm)` / `pinit (atm)` (si falta `pmean`) | L | no | qué columna dio `p_kpa` |
| `po2_kpa` | float | kPa | derivada | `xo2 × p_kpa` | C | no | revisar PHY-04 en inversas |
| `m_fuel_mg_s`, `m_o2_mg_s`, `m_n2_mg_s`, `m_total_mg_s` | float | mg/s | columnas de caudal | tokens `RAMP` → NULL + flag | M (control) | sí | |
| `zst`, `tad_k` | float | —, K | `mean Zst`/`Zst`, `Tad (K)` | `#DIV/0!` → NULL + flag | **C** | sí | nunca en el mismo eje que T medida |
| `ignited` | bool | — | CFI-G `Hot ignition` · FD EventData `Ignite` (`TP` normales, `INV_TP` inversas) | yes/no → bool; `flash` → NULL | M | sí | FD: 207/207 normales y 118/120 inversas unidas |
| `ignition_outcome` | cat | — | ídem | yes / no / flash | M | sí | |
| `outcome_source` | cat | — | — | `experimental_table` / `eventdata` / `none` | L | no | |
| `ignite_eventdata` | bool | — | EventData `Ignite` unido por `tpid` | — | L (decisión operativa) | sí | verificación cruzada en CFI-G |
| `hc_burnrate_mg_s` | float | mg/s | CFI-G inversa `HC burnrate (mg/s)` | — | M (control) | sí | semántica por confirmar con PHY; no se mezcla con `m_fuel_mg_s` |
| `fuel_dilution_pct` | float | % | prefijo "30% butane" | — | L | sí | % de combustible en la botella (resto N₂) |
| `tfp` | bool | — | `TFP` | — | L | sí | acrónimo sin definir en la fuente |
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
| `x_co2_inferred` | bool | — | derivada | CFI: `x_co2 = 0` solo si O₂+N₂+He = 1 ± 0.005 (223/227) | L | no | en las 4 restantes `x_co2` queda NULL |
| `flex_burning_rate_unverified` | float | ¿mm²/s? | FLEX `Burning rate; mm` | — | M | sí | fuera de `k_hot_mm2_s` hasta resolver R-DE-05b |
| `fuel_blend` | str | — | CFI `[.60]/[.40] C12H26/iso-dodecane` | → "60/40" | L | sí | |
| `quality_flags` | str | — | derivada | p ≤ 0 en la fuente (FLEX: 1 fila, `p_kpa` NULL); suma de fracciones ≠ 1 (CFI) | L | sí | |
| `source_file`, `source_row` | str, int | — | — | — | L | no | procedencia (CFI: fila de la `Master Sheet`) |

### `droplet_reference_points` (validación de M2)
- **Granularidad:** un punto (x, y) de una figura publicada (PSI-117, investigación de tierra), en formato largo.
  **Los puntos `model` / `unknown` nunca se usan como mediciones.**

| Columna | Tipo | Origen | Notas |
|---|---|---|---|
| `psi_id` | str | — | siempre PSI-117 |
| `data_file` | str | nombre del CSV sin prefijo | une con el ReadMe |
| `block`, `block_label`, `row_label` | int, str, str | bloque lado a lado y etiquetas (`C7`, `Expt`, `Sim`) | `row_label` se propaga a las filas siguientes del bloque |
| `role` | cat | inferido de etiquetas y encabezados | experiment / model / error_bar / unknown (historias temporales sin etiqueta) |
| `x_name`, `x`, `y_name`, `y` | str, float, str, float | encabezados y valores de la figura | unidades según el encabezado (p. ej. `P (atm)`, `Dext_HF`) |
| `fuel`, `d0_mm_raw`, `p_atm_raw`, `xo2_raw`, `xn2_raw` | str | ReadMe | **texto crudo** (hay rangos "0.5 - 3.0" y XN2 en %) |
| `third_component`, `third_component_raw` | str | ReadMe (7.ª columna: `XO3` o `XHe`) | |
| `doi`, `figure` | str | ReadMe | referencia del artículo y figura |
| `source_file`, `source_row`, `source_sha256` | str, int, str | — | procedencia |

### `investigations` (RQ5)
- **Granularidad:** una investigación (24). Une `silver/catalog/investigations` (ver § Silver · catálogo, mismas columnas y
  semántica) con el triage (`configs/triage.yaml`) y añade columnas derivadas.

| Columna | Tipo | Origen | Notas |
|---|---|---|---|
| `psi_id`, `acronym`, `title`, `doi`, `research_area`, `sub_research_area`, `project_type`, `is_ground_investigation` | — | silver catalog | ver § Silver · catálogo |
| `flight_program`, `flight_platform`, `experiment_hardware`, `experiment_hardware_link`, `managing_center`, `keywords`, `related_investigations` | — | silver catalog | |
| `start_date`, `end_date`, `release_date`, `modified_date`, `record_version`, `version_reason`, `license_id`, `license_name` | — | silver catalog | |
| `objective`, `approach`, `hypothesis`, `research_impacts`, `description` | str | silver catalog | corpus para RAG y fichas |
| `n_added_files`, `n_removed_files`, `n_experimental_tables`, `n_tables_not_in_added`, `n_publications`, `n_publications_with_doi`, `added_bytes`, `registered_total_bytes`, `access_status` | — | silver catalog | |
| `snapshot`, `source_file`, `source_sha256` | str | silver catalog | procedencia (snapshot bronze) |
| `R1`, `R2`, `R3`, `R4`, `R5`, `R6`, `score`, `tier`, `tier_notes` | int / float / str | triage (DE-05) | puntajes y tier con gates |
| `pillars`, `environments`, `rqs`, `justification` | str | triage (DE-05) | listas separadas por coma; pendiente ratificación PHY-02 |
| `hardware_family` | cat | derivada de `experiment_hardware` | CIR-ACME, CIR-MDCA, MSG, Saffire (Cygnus), CSD (SAME), P-Trak (DAFT), Ground lab, unknown |
| `n_gold_tests` | int | derivada | filas en `gas_flame_tests` + `droplet_tests` |
| `mvp_role` | str | ADR-0002 | RQ1 / RQ2 / RQ2 (validation) / NULL |

### `publications` (RAG y dashboard)
- **Granularidad:** una publicación única. Se deduplica por DOI normalizado; las que no tienen DOI quedan una fila por registro.

| Columna | Tipo | Origen | Notas |
|---|---|---|---|
| `doi` | str | silver `publications.doi` | NULL en 68 publicaciones sin DOI |
| `title`, `author_list`, `status` | str | silver | primera aparición |
| `psi_ids` | list[str] | silver | registros PSI que la citan |
| `n_records` | int | derivada | 44 DOI aparecen en más de un registro |
