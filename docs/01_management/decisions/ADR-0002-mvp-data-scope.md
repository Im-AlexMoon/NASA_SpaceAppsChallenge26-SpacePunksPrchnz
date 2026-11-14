# ADR-0002 — Alcance de datos del MVP

- **Estado:** **Aceptado (DE, 2026-11-14)**, pendiente de ratificación PHY-02 (pilares, entornos y R1) para cerrar **G1**.
- **Tarea relacionada:** DE-05 · insumos: DE-01…DE-04
- **Fuentes de verdad:** [configs/triage.yaml](../../../configs/triage.yaml) (puntajes) ·
  [configs/acquisition_manifest.yaml](../../../configs/acquisition_manifest.yaml) (selección) ·
  [triage_matrix.csv](../../02_data_engineering/triage_matrix.csv) y [acquisition_manifest.csv](../../02_data_engineering/acquisition_manifest.csv) (resultados resueltos)

## Contexto
PSI expone 24 investigaciones de combustión: 13.5 TB registrados y 6.27 TB expuestos, dominados por video, imágenes y ZIP. Las
tablas experimentales curadas pesan 211 KB. El perfilado L2 (DE-04) mostró dónde hay **resultados medidos bajo condiciones variadas**,
que es lo que necesitan la estadística y los modelos. También mostró que varias tablas relevantes solo contienen logs, rangos o texto libre.

## Decisión

### 1. Método de triage
Rúbrica R1–R6 ponderada (TRIAGE_METHODOLOGY §3) **con dos gates nuevos**:
- **Tier 1** exige R4 = 3, R3 ≥ 2 y R5 ≥ 2.
- **Tier 2** exige R3 ≥ 2 o R4 ≥ 2.

Sin los gates, registros muy relevantes pero sin resultado analizable (BASS-II, SAFFIRE) llegaban a Tier 1 solo por R1 y R2.
**El tier mide la calidad y relevancia del dato; el alcance del MVP se decide por pregunta de investigación** (punto 2).

Resultado: **Tier 1 (6)** PSI-159, PSI-10, PSI-69, PSI-101, PSI-39, PSI-107 · **Tier 2 (8)** PSI-98, PSI-100, PSI-102, PSI-25,
PSI-26, PSI-47, PSI-99, PSI-117 · **Tier 3 (10)** el resto.

### 2. Alcance por pregunta

| Bloque | Pregunta / modelo | Datasets | Rol |
|---|---|---|---|
| **MVP** | RQ1 · M1/M3 (ignición y extinción vs O₂ y presión) | **PSI-159** CFI-G (333 pruebas) | primario |
| | | PSI-10 Flame Design + Chamber Calculator `EventData` | extensión, si la unión por ID funciona (DE-07) |
| **MVP** | RQ2 · M2 (supresión por dilución, presión) | **PSI-69** FLEX (274) + **PSI-39** CFI DataSummary (146) | primarios |
| | | PSI-117 (de tierra; experimento vs. modelo) | validación / baseline físico |
| **MVP** | RQ5 (catálogo, comparación, ranking) | las 24 (silver catalog + 22 tablas experimentales + triage) | catálogo |
| Stretch | RQ4 (detección) | PSI-101 SAME-R, PSI-107 SPICE, PSI-98/100 SAFFIRE-I/III, PSI-102 SAME, PSI-47 DAFT | si el tiempo alcanza tras el scope freeze (H+12) |
| Stretch | RQ3 (sólidos) | PSI-25 BASS-II, PSI-26 BASS, PSI-99 SAFFIRE-II | contexto cualitativo y µg vs 1 g |
| F5 | Corpus RAG | 31 PDF de Reports y Science Documents de Tier 1–2 | documentos |

### 3. Manifest de adquisición L3 (lo que descarga DE-06)
**147 archivos, 263.3 MB:**

| Grupo | Archivos | Tamaño |
|---|---:|---:|
| Tablas experimentales | 22 | 0.2 MB |
| MVP RQ1 | 3 | 1.9 MB |
| MVP RQ2 | 11 | 0.5 MB |
| RQ4 (stretch) | 76 | 158.2 MB |
| RQ3 (stretch) | 4 | 0.2 MB |
| Documentos RAG | 31 | 102.2 MB |

Cambios de presupuesto respecto a `configs/sources.yaml`: `max_file_mb` sube de 30 a **50** solo porque el BASS-II Summary Report pesa
49 MB. `max_files` (150) y `max_total_mb` (500) no cambian. Sigue sin descargarse video, ZIP, imágenes ni flujos crudos de ACME
(`*_data.csv`, más de 1 GB por familia).

## Alternativas consideradas
| Opción | Pros | Contras |
|---|---|---|
| Rúbrica sin gates | más simple | promovía registros sin resultado (BASS-II, SAFFIRE) a Tier 1 |
| MVP = todos los Tier 1 (incluye SAME-R y SPICE) | más cobertura de pilares | 2 dominios extra de parsing antes del scope freeze; detección queda como stretch con datos ya descargados |
| Incluir los flujos crudos de ACME | señales temporales de radiómetros y termopares | > 1 GB, no los necesitan las RQ del MVP |

## Consecuencias
- M1 se apoya primero en CFI-G, que trae los resultados en su tabla. PSI-10 aporta más datos solo tras unirlo con `EventData`: es el riesgo **R-DE-05a**.
  **Resuelto en DE-07:** `EventData` trae `TP` (normales) e `INV_TP` (inversas); la unión cubre 325/327 pruebas.
- M2 combina FLEX y CFI. Requiere armonizar unidades (mmHg vs atm; confirmar que la "tasa de quemado" de FLEX es K en mm²/s, **R-DE-05b**) y unir la `Master Sheet` con `DATA` de CFI.
- Los datos de detección (RQ4) quedan descargados en DE-06 aunque su análisis sea stretch. Así no hay re-trabajo si hay tiempo.
- PHY-02 puede añadir un `override` en `configs/triage.yaml` (con `tier`, `reason` y `by`) y regenerar con `flamesafe triage`.
