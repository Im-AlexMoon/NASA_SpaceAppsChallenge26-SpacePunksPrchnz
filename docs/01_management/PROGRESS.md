# Progress — tablero de fases

> Se actualiza en cada sync (cada 4 h) y al cerrar un gate.
> Estado: ⬜ no iniciado · 🟦 en curso · 🟨 en riesgo · 🟥 bloqueado · ✅ cerrado

**H+0 (inicio):** `____-__-__ __:__` · **Deadline:** `____-__-__ __:__`

## Estado por fase

| Fase | Gate | Objetivo | Estado | % | Responsable | Nota |
|---|---|---|---|---|---|---|
| F0 Setup y alineación | G0 | H+2 | 🟦 | 20 | | Repo + plan listos |
| F1 Descubrimiento y triage | G1 | H+5 | 🟨 | 90 | DE | DE-01…05 ✔; **G1 espera a PHY-02** (ratificar pilar, entorno y R1) |
| F2 Pipeline medallion | G2 | H+9 | ⬜ | 0 | | |
| F3 EDA y estadística | G3 | H+14 | ⬜ | 0 | | |
| F4 Modelado | G4 | H+17 | ⬜ | 0 | | |
| F5 RAG | G5 | H+16 | ⬜ | 0 | | |
| F6 Dashboard | G6 | H+20 | ⬜ | 0 | | |
| F7 Física | G7 | H+20 | 🟦 | 5 | | Primer en borrador |
| F8 Entrega | G8 | H+24 | ⬜ | 0 | | |

## Bitácora de syncs

<!-- Copia este bloque por cada sync -->
### Sync H+0 — kick-off
- ✔ Hecho: estructura del repo, plan ejecutivo, plantillas.
- ▶ Siguiente: G0 (roles, entorno, RQ v0), arrancar DE-01/DE-02.
- ⛔ Bloqueos: —
- 🔀 Decisiones / recortes: —

### DE-01 cerrado — 2026-11-14
- ✔ Hecho: cliente PSI con reintentos (`psi_client.py`), comando `flamesafe verify-api`, reporte JSON de evidencia y 16 tests (2 en vivo).
- 📌 Hallazgos:
  - 133 investigaciones / 24 de combustión; todos los conteos de referencia coinciden.
  - **La telemetría de SAFFIRE-I ya descarga (HTTP 200).** La referencia la daba por 404.
  - Los datos PSI son **CC0 1.0** (23/24 registros).
  - Un id de investigación inexistente devuelve 403, no 404.
- ▶ Siguiente: DE-02 (catálogo de las 24 investigaciones a bronze) y DE-03 (aplanado del inventario).

### DE-02 cerrado — 2026-11-14
- ✔ Hecho: `flamesafe catalog` guarda un snapshot diario e inmutable en `data/bronze/catalog/`.
  - Contenido: búsqueda + 24 detalles, byte a byte (21.7 MB), con manifest sha256.
  - Re-correr el mismo día reanuda; detecta drift contra el snapshot anterior; solo actualiza `LATEST` si el snapshot está completo.
  - 5 tests nuevos.
- 📌 Validación: los conteos del snapshot son idénticos al reporte de DE-01.
- ⚠️ Los JSON de detalle incluyen contactos de los PIs (nombres y emails). Bronze no se versiona y silver (DE-03) debe eliminarlos.
- ▶ Siguiente: DE-03, aplanar el snapshot en `silver/catalog/{investigations,files,experimental_tables,publications}.parquet`.

### DE-03 cerrado — 2026-11-14
- ✔ Hecho: `flamesafe silver` (paso catálogo) genera 5 tablas Parquet en `data/silver/catalog/` y un reporte de parseo.
  - Filas: investigations 24 · files 27,076 · experimental_tables 22 · publications 352 · contacts 86 (sin email, teléfono, fax ni dirección).
  - Reconciliación 5/5 contra el JSON crudo; totales idénticos a DE-01. 0 errores; 1 aviso informativo: licencia vacía en PSI-10.
  - 9 tests nuevos (29 unitarios en total). Diccionario de silver documentado en DATA_DICTIONARY.md.
- 📌 Hallazgos:
  - Bytes expuestos: 6,267 GB de 13,497 GB registrados. Casi todo es `Raw Data`, dominado por ZIP, TXT, CSV, MDIPSUG y MP4.
  - SAFFIRE-I y SAFFIRE-III: el campo de hardware de PSI confirma **Cygnus**, aunque `Flight Platform` diga ISS.
  - `experiment_hardware` es texto libre inconsistente: hay que normalizarlo a `hardware_family` para Compare y ranking.
  - 284 de las 352 publicaciones tienen DOI y hay duplicados entre registros: deduplicar por DOI en gold y en el corpus RAG.
- ▶ Siguiente: DE-04, perfiles de formato de las candidatas Tier 1/2 a partir de `silver/catalog/files`, y PHY-02, mapeo de pilar y entorno.

### DE-04 cerrado — 2026-11-14
- ✔ Hecho: `flamesafe profile` descarga las muestras L2 listadas en `configs/l2_samples.yaml` dentro del presupuesto y las perfila automáticamente.
  - Descarga: 60 archivos, 50.3 MB, 60/60 OK; cada archivo con sidecar sha256 en `data/bronze/files/`.
  - Perfilado: encoding, preámbulos, bloques lado a lado, tokens no numéricos y unidades del encabezado.
  - Genera 24 perfiles `investigations/PSI-XX.md` con un bloque AUTO que se regenera y un bloque manual que se preserva. 12 tests nuevos (41 en total).
- 📌 Hallazgos: ver [investigations/README.md](../02_data_engineering/investigations/README.md).
  - **CFI (PSI-39) tiene resultados medidos procesados** (k y Dext de llama caliente y fría, 146 pruebas): sube a Tier 1.
  - **PSI-10 no trae resultado en su tabla**: la ignición está en el Chamber Calculator. M1 se basará primero en CFI-G (PSI-159).
  - Supresión: FLEX (CO₂ en 123 pruebas, He en 50; 186 extinciones) + CFI (He) → M2 es viable.
  - Solo SAFFIRE-II tiene tasas de propagación en tabla (µg y 1 g, 9 muestras).
- ▶ Siguiente: DE-05 (matriz de triage puntuada + manifest de adquisición + ADR-0002) con revisión PHY-02.

### DE-05 cerrado — 2026-11-14
- ✔ Hecho:
  - `configs/triage.yaml` tiene puntajes R1–R6, pilares, entornos, RQ y justificación para las 24 investigaciones.
  - `flamesafe triage` calcula el score, aplica los gates de tier y genera la matriz en TRIAGE_METHODOLOGY §4 y `triage_matrix.csv`.
  - También resuelve `configs/acquisition_manifest.yaml` → `acquisition_manifest.csv` (lock que se commitea).
  - 8 tests nuevos (49 en total).
- 📌 Resultado:
  - **Tier 1:** PSI-159, 10, 69, 101, 39, 107 · **Tier 2:** PSI-98, 100, 102, 25, 26, 47, 99, 117 · **Tier 3:** 10 registros.
  - Manifest: 147 archivos, 263.3 MB.
  - ADR-0002 aceptado por DE. MVP: RQ1 (CFI-G + Flame Design), RQ2 (FLEX + CFI, con PSI-117 como validación) y RQ5 (las 24). Stretch: RQ4 y RQ3.
- ⚠️ Cambio de método: se añadieron **gates** a la rúbrica para que la relevancia sola no promueva registros sin resultado analizable.
- ⛔ **G1 bloqueado por PHY-02:** PHY debe ratificar pilar, entorno y R1, o registrar un `override`.
- ▶ Siguiente: PHY-02 para cerrar G1. En paralelo se puede arrancar DE-06 (descargar el manifest) y DS-02 (contrato de variables por RQ).
