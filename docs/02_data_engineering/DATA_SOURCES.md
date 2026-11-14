# Fuentes de datos y log de verificación

> Fuente de verdad de **cómo** obtenemos los datos y **qué verificamos, cuándo**. Ningún conteo se escribe aquí sin haberlo
> obtenido del API. El repositorio de referencia se usa solo como guía (ADR-0003).
>
> **Evidencia reproducible:** `flamesafe verify-api` → [verification/api_verification_2026-11-14.json](verification/api_verification_2026-11-14.json)
> (solo metadatos; sin archivos de datos ni credenciales).

## 1. NASA Physical Sciences Informatics (PSI)

| Recurso | URL |
|---|---|
| Portal | <https://psi.nasa.gov> |
| Repositorio UI | <https://psi.nasa.gov/physci/repo> |
| Investigación (UI) | `https://psi.nasa.gov/physci/repo/data/investigations/{PSI-ID}` |

### Endpoints del API público (configurados en `configs/sources.yaml`, cliente en `src/flamesafe/ingestion/psi_client.py`)

| Uso | Método + ruta (base `https://psi.nasa.gov/geode-py/ws`) | Verificado |
|---|---|---|
| Búsqueda de investigaciones | `GET /repo/search?source=psi&type=investigation&size=200&from=0` | ✔ 2026-11-14 · HTTP 200 · ~1 MB · ~3.5 s |
| Detalle de investigación | `GET /repo/investigations/{PSI-ID}` | ✔ 2026-11-14 · 24/24 HTTP 200 · hasta ~2.9 MB (PSI-10) y ~7 s |
| Descarga de archivo | `GET /studies/{PSI-ID}/download?file={nombre url-encoded}` | ✔ 2026-11-14 · 22/22 tablas experimentales HTTP 200, tamaño = listado |
| URL prefirmada | mismo endpoint + `&redirect=false` → texto plano con URL S3 prefirmada | ✔ 2026-11-14 |

### Comportamiento observado (2026-11-14)

- **Búsqueda:** JSON estilo Elasticsearch, en `hits.hits[]._source`. Campos: `Accession`, `Acronym`, `Title`, `Research Area`,
  `SubResearch Area`, `Project Type`, `Flight Platform`, `Experiment Hardware`, `Objectives`, `Approach`, `Hypothesis`,
  `Research Impacts/Earth Benefits`, `Publication Title`, `Publication Author List`, `Keywords` y otros.
- **Detalle:** metadatos (`title`, `investigationAcronym`, `doi`, `objective`, `approach`, `hypothesis`, `researchImpacts`,
  `experimentHardware` {Name, Link}, `publications[]`, `licenseName`), más las listas de archivos:
  - `added`: inventario actual. Cada archivo trae `file_name`, `file_size`, `s3_path`, `s3_version_id`, `restricted`, `visible` y `version`.
  - `experimentalTable`: tablas curadas. **Pueden no estar en `added`.**
  - `removed`: versiones previas de archivos.
  - `totalFileSize`: tamaño registrado. No equivale a la suma de los archivos expuestos.
- **Errores:** id de investigación inexistente → **HTTP 403** (no 404). Archivo inexistente → **HTTP 404**.
- **Seguridad:** la URL prefirmada incluye credenciales AWS temporales (`AWSAccessKeyId`, `Signature`, `x-amz-security-token`).
  El cliente las redacta con `redact_url()`. **Nunca** se registran ni se commitean.
- **Licencia de datos:** 23/24 registros declaran `licenseName = "Creative Commons Zero v1.0 Universal"` (CC0). PSI-10 tiene el campo vacío.
  Aun así mantenemos la política de no redistribuir archivos crudos en el repo y de citar PSI-ID y DOI.

## 2. Colección de combustión verificada (2026-11-14)

**133** investigaciones en PSI. **24** son `Research Area = "Combustion Science"`, que coincide con lo esperado.
Totales: **16,354** archivos `added` · **22** tablas experimentales (**211,116 bytes**), de las cuales **14** no están en `added` ·
**13,496.77 GB** registrados · acceso: **20** `available`, **4** `experimental_table_only`, **0** `no_public_files`.
Investigaciones de tierra (no microgravedad): PSI-60, PSI-62, PSI-115, PSI-117 y PSI-142.

| PSI-ID | Acrónimo | Sub-área (PSI) | Plataforma | `added` | Tablas exp. | `removed` | Publicaciones | GB registrados | Acceso |
|---|---|---|---|---:|---:|---:|---:|---:|---|
| PSI-10 | ACME/Flame Design | Flames of Gaseous Fuels | ISS | 3,807 | 2 | 0 | 33 | 2,180.44 | available |
| PSI-20 | ACME BRE | Flames of Gaseous Fuels | ISS | 1 | 1 | 0 | 16 | 2,035.57 | available |
| PSI-21 | ACME CLD Flame | Flames of gaseous fuel | ISS | 1 | 1 | 0 | 18 | 2,005.54 | available |
| PSI-22 | ACME E-FIELD Flames | Laminar Flames | ISS | 0 | 1 | 0 | 25 | 950.21 | experimental_table_only |
| PSI-23 | ACME s-Flame | Flames of gaseous fuels | ISS | 4,163 | 1 | 6,814 | 44 | 782.17 | available |
| PSI-25 | BASS-II | Spacecraft Fire Safety | ISS | 694 | 1 | 131 | 17 | 274.63 | available |
| PSI-26 | BASS | Spacecraft Fire Safety | ISS | 211 | 1 | 24 | 10 | 163.55 | available |
| PSI-39 | CFI | Droplets | ISS | 2,831 | 1 | 2,698 | 7 | 718.89 | available |
| PSI-47 | DAFT / DAFT-2 | Spacecraft Fire Safety | ISS | 32 | 1 | 185 | 2 | 0.04 | available |
| PSI-60 | — (tierra) | Gaseous | — | 1 | 0 | 0 | 1 | 0.00 | available |
| PSI-62 | — (tierra) | Spacecraft Fire Safety | — | 1 | 0 | 0 | 4 | 0.00 | available |
| PSI-68 | FLEX-2 | Spacecraft Fire Safety | ISS | 0 | 1 | 0 | 48 | 1,224.75 | experimental_table_only |
| PSI-69 | FLEX | Spacecraft Fire Safety | ISS | 0 | 1 | 0 | 51 | 923.83 | experimental_table_only |
| PSI-98 | SAFFIRE-I | Spacecraft Fire, Smoke Distribution | ISS | 74 | 1 | 85 | 6 | 12.25 | available |
| PSI-99 | SAFFIRE-II | Surface Combustion | Cygnus Spacecraft | 0 | 1 | 0 | 7 | 16.93 | experimental_table_only |
| PSI-100 | SAFFIRE-III | Spacecraft Fire Safety | ISS | 85 | 1 | 97 | 3 | 35.21 | available |
| PSI-101 | SAME-R | Spacecraft Fire Safety | ISS | 342 | 1 | 379 | 6 | 6.31 | available |
| PSI-102 | SAME | Spacecraft Fire Safety | ISS | 104 | 1 | 52 | 16 | 0.66 | available |
| PSI-106 | SLICE | — | ISS | 1 | 1 | 0 | 5 | 72.91 | available |
| PSI-107 | SPICE | Fire Safety | ISS | 186 | 1 | 216 | 9 | 6.95 | available |
| PSI-115 | — (tierra) | Smoke Aerosol, Combustion Simulation | N/A | 47 | 0 | 38 | 0 | 0.26 | available |
| PSI-117 | — (tierra) | Droplet | — | 15 | 0 | 0 | 10 | 0.07 | available |
| PSI-142 | — (tierra) | Spacecraft Fire Safety | N/A | 2 | 1 | 3 | 12 | 0.00 | available |
| PSI-159 | ACME CFI-G | Flames of Gaseous Fuels | ISS | 3,756 | 2 | 0 | 2 | 2,085.59 | available |

"Plataforma" se transcribe tal como la reporta PSI. Ojo: SAFFIRE voló en Cygnus en todas sus ediciones, pero PSI solo lo indica para
SAFFIRE-II. Hay que confirmarlo con la literatura antes de mostrarlo.

## 3. Contraste con el repositorio de referencia (ADR-0003)

| Afirmación de referencia (snapshot 2026-11-08) | Nuestro resultado (2026-11-14) | Veredicto |
|---|---|---|
| 133 investigaciones, 24 de combustión | 133 / 24 | ✔ coincide |
| 16,354 `added`, 22 tablas exp., 14 fuera de `added`, 211,116 bytes | idénticos | ✔ coincide |
| 13,496.77 GB registrados | 13,496.77 GB | ✔ coincide |
| ET-only: PSI-22, 68, 69, 99 | idénticos | ✔ coincide |
| sha256 de tablas PSI-10 (×2), PSI-69, PSI-159 (×2) | idénticos | ✔ coincide |
| Telemetría y sensores XLSX de **SAFFIRE-I (PSI-98) → HTTP 404** | **HTTP 200**: XLSX válido, tamaño = listado (2,775,737 B la telemetría) | ✖ **ya no aplica**: estos archivos están disponibles |

**Implicación:** SAFFIRE-I se vuelve candidato a telemetría utilizable en la triage (DE-05). Hay que re-verificar en DE-06.

## 4. Fuentes complementarias

| Fuente | Uso | URL |
|---|---|---|
| Publicaciones (DOI) listadas en cada registro PSI | Corpus RAG, interpretación física | vía DOI |
| NASA Technical Reports Server (NTRS) | Reportes técnicos SAFFIRE, BASS, FLEX | <https://ntrs.nasa.gov> |
| Páginas de experimentos NASA GRC (`experimentHardware.Link`) | Contexto de hardware y objetivos | ver detalle PSI |
| Repositorio de referencia (AFAQ) | Mapa de exploración, no se copia | <https://github.com/YoussefHegazy74/flame-in-freefall> |

## 5. Log de verificación

| Fecha/hora (UTC) | Quién | Qué se verificó | Resultado | Evidencia |
|---|---|---|---|---|
| 2026-11-14 | DE (DE-01) | Total de investigaciones / de combustión | 133 / 24 | `verification/api_verification_2026-11-14.json` |
| 2026-11-14 | DE (DE-01) | 24 detalles HTTP 200 | 24/24 | ídem |
| 2026-11-14 | DE (DE-01) | Descarga de las 22 tablas experimentales | 22/22 HTTP 200, 22/22 tamaño = listado, sha256 registrados | ídem |
| 2026-11-14 | DE (DE-01) | Re-chequeo de 404 de SAFFIRE-I (3 XLSX) | 3/3 HTTP 200 | ídem |
| 2026-11-14 | DE (DE-01) | Controles negativos | archivo inexistente 404 · id inexistente 403 | ídem |
| 2026-11-14 | DE (DE-02) | Snapshot de catálogo en bronze (`flamesafe catalog`) | 25 archivos (búsqueda + 24 detalles), 21,689,225 bytes, completo; conteos idénticos al reporte DE-01 | `data/bronze/catalog/snapshot_2026-11-14/manifest.json` (local, no versionado) |

## 6. Atribución
Los datos son de NASA PSI (CC0 1.0 según el registro) y se citan por PSI-ID y DOI. No redistribuimos archivos crudos en el repositorio.
No implicamos aval de NASA.
