# Progress — tablero de fases

> Se actualiza en cada sync (cada 4 h) y al cerrar un gate.
> Estado: ⬜ no iniciado · 🟦 en curso · 🟨 en riesgo · 🟥 bloqueado · ✅ cerrado

**H+0 (inicio):** `____-__-__ __:__` · **Deadline:** `____-__-__ __:__`

## Estado por fase

| Fase | Gate | Objetivo | Estado | % | Responsable | Nota |
|---|---|---|---|---|---|---|
| F0 Setup y alineación | G0 | H+2 | 🟦 | 20 | | Repo + plan listos |
| F1 Descubrimiento y triage | G1 | H+5 | 🟨 | 90 | DE | DE-01…05 ✔; **G1 espera a PHY-02** (ratificar pilar, entorno y R1) |
| F2 Pipeline medallion | G2 | H+9 | ✅ | 100 | DE | **G2 cerrado**: gate de datos PASSED, rebuild determinista |
| F3 EDA y estadística | G3 | H+14 | 🟦 | 55 | DS | discovery ✔ · EDA RQ1 v1 ✔ · auditoría + segmentación + categóricas de gas ✔ (PR #3) · pendiente PHY-03, EDA RQ2 (gotas) |
| F4 Modelado | G4 | H+17 | 🟦 | 55 | DS | M1 v1 ✔ (ignición + duración, model card M-01, pendiente PHY) · M2 (gotas) espera EDA RQ2 + ADR-0006 |
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

### DE-06 cerrado — 2026-11-14
- ✔ Hecho: `flamesafe bronze` descarga el lock `acquisition_manifest.csv`. También tiene `--dry-run` y `--verify-only`.
  - Valida presupuesto y drift contra el catálogo, reutiliza lo ya descargado con sha256 válido y re-hashea todo al final.
  - Reporte por grupo con duplicados. 6 tests nuevos (55 en total).
- 📌 Resultado:
  - **145/147** archivos (262.2 MB): 93 descargados y 52 reutilizados de L2. 0 diferencias de tamaño, 0 drift, integridad 153/153.
  - **2 × HTTP 404** re-verificados: PDF de reportes finales en PSI-26 (BASS y SPICE). Solo afectan al corpus RAG.
  - 3 PDF idénticos entre registros (SAFFIRE I/III, SAME/SAME-R): deduplicar por sha256 en el corpus RAG.
- ▶ Siguiente: DS-02 (contrato de variables por RQ) → DE-07 (parsers silver de CFI-G, Flame Design + EventData, FLEX, CFI DataSummary y PSI-117).

### DS-02 y DE-07 cerrados — 2026-11-14
- ✔ DS-02: contrato de variables por RQ en RESEARCH_QUESTIONS.md y specs columna a columna de las tablas gold
  `gas_flame_tests`, `droplet_tests`, `droplet_reference_points` e `investigations` en DATA_DICTIONARY.md.
- ✔ DE-07: framework silver con specs declarativas (errores por drift de esquema, tokens → NULL + `__flag`, unidades de la fuente
  en los nombres, procedencia por fila). Hay 7 parsers que producen 33 tablas: 11 semánticas MVP y 22 genéricas de tablas experimentales.
  - 0 errores; 2 advertencias reales: FLEX con p = 0 mmHg en 1 fila y PSI-117 ReadMe con XN2 en %.
  - 12 tests nuevos (64 unitarios + 3 de integración).
- 📌 Hallazgo clave: **R-DE-05a resuelto**. `EventData` registra las inversas como `INV_TP`, así que Flame Design tiene resultado
  de ignición en 325/327 pruebas. Para M1 hay ~660 pruebas con resultado (CFI-G 333 + Flame Design 325).
  Además, en CFI-G `EventData` permite verificar `Hot ignition` en 331 pruebas.
- ▶ Siguiente: DE-08, construir gold (`gas_flame_tests`, `droplet_tests`, `droplet_reference_points`, `investigations`), junto con DE-09 (pandera) y DE-10.

### DE-08 cerrado — 2026-11-14
- ✔ Hecho: `flamesafe gold` genera 5 tablas gold (Parquet) y `flamesafe.duckdb`. Las conversiones van por `physics/units.py`.
  - Columnas derivadas explícitas: `po2_kpa`, `fuel_dilution_pct`, `x_co2_inferred`.
  - El reporte incluye verificaciones cruzadas, cobertura de resultados e invariantes.
  - 13 tests nuevos (85 en total, incluidos 4 de integración).
- 📌 Resultado:
  - `gas_flame_tests` 660 (650 con `ignited`) · `droplet_tests` 501 (148 con k caliente, 341 con Dext caliente, 274 con `test_end`)
    · `droplet_reference_points` 15,861 · `investigations` 24 · `publications` 303 (235 DOI únicos; 44 DOI compartidos entre registros).
  - Invariantes: 1 violación, CFI 1274A con Dext caliente 19 % mayor que D₀. Otros 8 casos con < 5 % de exceso son plausibles por hinchamiento térmico.
- ⚠️ **R-DE-08a:** el `Ignite` de EventData es una decisión operativa. Coincide en 86 % con `Hot ignition` de CFI-G y discrepa sobre
  todo en llamas breves. En Flame Design es casi constante. **M1 debe entrenarse con CFI-G** y Flame Design queda para contexto/validación (decisión PHY).
- ▶ Siguiente: DE-09 (contratos pandera para silver/gold) y DE-10 (cerrar el data dictionary) → **G2**.

### DE-09 y DE-10 cerrados · 🚦 G2 CERRADO — 2026-11-14
- ✔ `flamesafe validate` implementa el gate G2 en código. Contratos: **37/37** (5 gold estrictos, 10 silver MVP y 22 genéricos de procedencia).
  Reconciliación: **34/34** (bronze→silver y silver→gold). Ningún token convertido en valor: **19/19** columnas. Cobertura del diccionario: **5/5** tablas.
- ✔ Rebuild desde bronze, con silver y gold borrados: **gold idéntico** (hash por tabla). `make pipeline` ahora termina en `validate`.
- ✔ Fixtures de CI en `data/sample/gold_*.parquet` (160 KB, estratificados con casos borde). 16 tests nuevos (101 en total).
- ✔ DATA_DICTIONARY completo para las 5 tablas gold; `validate` falla si se desincroniza.
- ▶ Siguiente:
  - **F3/F4 desbloqueados para DS** (DS-03…DS-13): EDA sobre gold y M1 con CFI-G.
  - **F5:** RAG-01 puede usar los 29 PDF descargados y `publications`.
  - **F6:** APP-02 puede hacer el vertical slice con DuckDB.
  - **G1** sigue pendiente de PHY-02.

### Decisiones PHY + notebook 01_discovery — 2026-11-14
- ✔ **Decisiones PHY recibidas:**
  - `flash` (8 casos de CFI-G): categoría propia, fuera del ajuste binario principal de M1, con análisis de sensibilidad (flash = sí / flash = no).
  - Tasa de quemado de FLEX: **mm²/s**. Evidencia interna en el notebook: frente a K̂ = (d₀² − d_ext²)/t_quemado, cociente mediano 1.05
    (IQR 1.03–1.09) y Spearman 0.96 en 196 pruebas (control CFI: 1.21 y 0.74). Falta formalizarlo en ADR-0006 y pasar la columna a `k_hot_mm2_s`.
- ✔ `notebooks/01_discovery/01_discovery_gold_coverage_am.ipynb`: inventario, diseño experimental, confusores, faltantes, cobertura cerca
  de los hábitats y material de validación. Lee solo DuckDB gold y corre completo ("Restart & Run All").
- 📌 Hallazgos que condicionan el EDA:
  - Los resultados secundarios (`extinction_mode`, `burn_time_s`, `peak_burner_t_k`, `tfp`) **solo existen en CFI-G**. Flame Design aporta
    condiciones, `zst`/`tad_k` y un resultado casi siempre "yes" (98.8 %): sirve como soporte positivo, no como clase negativa.
  - `xo2` y `p` se variaron casi de forma independiente (|ρ| ≤ 0.3), así que H1 (po2 vs. xo2) es contestable.
  - Cerca de la base lunar (±0.05 xo2, ±25 % p) hay solo 6 pruebas (todas CFI-G); cerca de la atmósfera de exploración, 30. El traje
    espacial queda fuera del dominio de gold.
  - 9 pruebas de gotas con d_ext ≥ d₀ (1 FLEX, 8 CFI) para revisar en el EDA.
  - Corrección: CFI-G tiene 62 "no" (no 60); MODELING_PLAN actualizado.
- ▶ Siguiente: ADR-0006 (decisiones PHY + R-DE-05b en el pipeline), DS-03 (ratificar RQs) y `02_eda` empezando por RQ1.

### DS-04/DS-05 · EDA RQ1 v1 — 2026-11-14
- ✔ `notebooks/02_eda/02_eda_rq1_ignition_boundary_am.ipynb` sobre CFI-G (normales e inversas por separado), con pruebas pre-registradas
  T1–T4, SE robustos por `test_day`, Holm sobre la familia primaria y validación cruzada dejando fuera días completos.
- ✔ `src/flamesafe/analysis/stats.py` (logit agrupado, Holm, CV por grupos, bootstrap por grupos, umbral logístico) + 4 tests.
  CI instala ahora el extra `analysis`.
- 📌 Resultados (candidatos a finding, pendientes de PHY-03):
  - **F-01 (más fuerte):** en llamas normales encendidas, +0.05 de xo2 multiplica por ≈ 2.2 (IC 95 % 1.6–3.2) las odds de que la llama
    siga hasta el corte de flujo en vez de autoextinguirse (exploratorio, p < 0.001).
  - **F-02:** límite pobre claro (ninguna ignición con `x_fuel` < ~0.03); efecto del O₂ en la ignición en la dirección esperada
    (OR ≈ 1.4 por +0.05) pero **no significativo tras Holm** (p_holm ≈ 0.11 en las 4 pruebas primarias).
  - **F-03 (brecha):** H1 (xo2 + p vs. po2) no se puede decidir en llamas normales (ΔAIC ≈ 0); en inversas gana xo2 + p (ΔAIC ≈ 5.6).
  - **F-04 (brecha):** ninguna prueba de llama normal cerca de la base lunar (30 % O₂, 70 kPa); cerca de la atmósfera de exploración, 19 de 3 días.
  - Sensibilidad `flash`: OR(xo2) estable (1.22–1.25), la decisión PHY no sesga el resultado.
- ⚠️ El modelo logístico lineal está mal especificado en llamas normales (efecto no monótono del combustible: tres regímenes).
  **M1 debe tratar el combustible de forma no lineal.** Preguntas PHY: significado de `Xfuel` en CFI-G normal, dirección de la presión
  en inversas, 2 pruebas con `x_fuel = 0` (21125A4, 21125H3).
- ▶ Siguiente: PHY-03 sobre F-01…F-04, ADR-0006 (FLEX → `k_hot_mm2_s`) y EDA RQ2 (diluyentes en gotas).

### DS-04 · EDA del equipo: auditoría, segmentación y categóricas (PR #3) — 2026-11-15
- ✔ Integrado en `main` (`f10c8b0`):
  - `notebooks/02_eda/02_eda_legit.ipynb` (J0SETS): auditoría de identidad y cronología, familias experimentales, candidatos a réplica,
    faltantes estructurales, correlaciones y PCA por familia, y asociaciones categórica × numérica dentro de bloques. Solo descriptivo
    (sin p-valores ni modelos). Se versiona **sin salidas**; corre completo sin errores y escribe tablas en `artifacts/` (ignorado por git).
  - `src/flamesafe/analysis/segmentation.py`, `categorical.py`, `notebook_sections.py` + 2 archivos de tests; scripts generadores en `scripts/append_eda_*.py`.
  - `notebooks/01_discovery/01_eda_nochateado.ipynb` (Hugo-Edel): exploración inicial de `burn_time_s` y `extinction_mode`.
  - `uv.lock` versionado y dependencias nuevas en `pyproject.toml`.
- ✔ Verificación local: `pytest -m "not integration"` 113 pasan; `ruff check src tests app` sin errores.
- 📌 Hallazgos de esta ronda:
  - 660 filas, 660 identidades únicas, **0 copias** retiradas. **1 prueba con cronología imposible** (21265H1: el fin es ~1 día anterior
    al inicio) y **4 sin timestamp** (21209A2, 21242P2, 22042M1, 22035D3). Se conservan marcadas, sin corregir ni imputar.
  - **23 familias** (campaña × llama × combustible × dilución × periodo) y **46 bloques de operación**: 10 familias tienen < 20 pruebas
    y 11 vienen de una sola operación. Familia no equivale a independencia.
  - **47 pruebas en 19 grupos con condiciones idénticas** (candidatos a réplica); en 8 grupos el resultado difiere con las mismas
    condiciones registradas. Esto es variabilidad real o condiciones no registradas: no se eliminan.
  - Los **8 `flash` son todos etano en CFI-G inversa**, con O₂ bajo (mediana 0.15 frente a 0.85 en los "yes" del mismo bloque).
    No basta para atribuirlo solo al combustible.
  - **Confusión de diseño:** etileno solo en Flame Design; etano y butano solo en CFI-G. En 44 contrastes de categoría no hay
    operaciones compartidas, así que categoría y jornada no se pueden separar.
  - Cohorte binaria CFI-G = 322 (177 normales y 145 inversas tras quitar anomalías y controles): coincide con las n de RQ1.
    Tasa de ignición 74.6 % (normales) y 89.7 % (inversas); robusta a incluir o excluir anomalías y controles de flujo cero.
  - `burn_time_s` con `flow_terminated` se acumula en ~66 s (26 de 89): es el **corte del experimento (dato censurado)**, no un tiempo
    de extinción. Cualquier análisis de duración debe tratarlo como censurado.
- ⚠️ Para revisar:
  - ✔ **Corregido:** `pyproject.toml` declaraba `scypy>=0.0.8` (otro paquete de PyPI, no SciPy) y `01_eda_nochateado` hacía
    `import scypy`. Ahora es `scipy>=1.13`; `uv.lock` regenerado (solo cambia scypy → scipy). Sigue pendiente decidir si seaborn,
    scikit-learn, ipykernel y fastparquet pasan de dependencias núcleo a extras (`analysis`/`dev`).
  - 57 pruebas sin ignición tienen `burn_time_s = 0` (⚠️ por verificar en la fuente si es un 0 real o "no aplica"; según la regla del
    repo, lo que no aplica debe ir como NULL + flag).
  - Las salidas de los notebooks imprimen rutas locales absolutas (incluido un usuario de Windows); preferir rutas relativas.
- ▶ Siguiente: PHY-03 (F-01…F-04 + preguntas abiertas: `flash`, equivalencia de `Ignite`, `HC burnrate`, `po2_kpa` en inversas,
  tolerancia de réplica), ADR-0006 (FLEX → `k_hot_mm2_s`), EDA RQ2 (gotas) y empezar M1 con validación agrupada por operación.

### DS-08…DS-13 · M1 v1: ignición y duración de llamas de gas — 2026-11-15
- ✔ Objetivos acordados con el equipo: **probabilidad de ignición** y **cuánto tiempo sigue ardiendo una llama encendida**.
  Duración modelada como **supervivencia**: autoextinción = evento, corte de flujo = censura por la derecha.
- ✔ `src/flamesafe/models/m1.py` (cohortes, validación dejando fuera días, logística penalizada con spline y CV anidada, Weibull AFT,
  Cox con errores por día, bootstrap de días, dominio de aplicabilidad) + `tests/unit/test_models_m1.py` (9 tests). `lifelines` en el extra `analysis`.
- ✔ `notebooks/03_modeling/03_m1_ignition_survival_am.ipynb` y `docs/03_data_science/model_cards/M-01.md`.
- 📌 Resultados (candidatos, pendientes de PHY-03/04):
  - **Duración, llama normal:** índice C fuera de muestra 0.81 (IC 0.75–0.84), +0.13 sobre solo O₂. +0.05 O₂ → duración ×2.3;
    Cox HR 0.19 (0.13–0.29). Más presión acorta la llama (duplicar: HR 2.2). Tad/Zst como variables rinden igual que las crudas.
  - **Duración, llama inversa:** C 0.82; manda la fracción de combustible del ambiente.
  - **Ignición, llama normal:** cumple G4 (log-loss 0.485 vs 0.609 trivial, Δ −0.12, IC −0.19 a −0.06; AUC 0.81). La señal viene de la
    fuente de combustible, no de O₂ + presión. **Inversa:** nada supera la tasa base (90 %).
  - **Hábitats (normal, µg):** cerca de la cabina ISS la llama dura ~9 s (mediana observada); cerca de la atmósfera de exploración
    (34 %, 56.5 kPa) ~88 s. **~10× más**, coherente entre datos y modelo. Base lunar: 0 pruebas (cae en el hueco de O₂ 0.24–0.33).
- ⚠️ Para PHY: censura posiblemente informativa en llamas normales (cortes de 13 a 276 s; en inversas 26/58 a los 66 s), meseta de
  llamas estables en O₂ bajo (modelo de fracción curada), signos de presión y combustible, y la decisión `flash` en inversas.
- ▶ Siguiente: revisión PHY de M-01, indicador físico con Cantera (margen de extinción) como experimento, EDA RQ2 → M2, y la tarjeta
  "consulta de atmósfera" del dashboard con M1.

### Investigación · iteración 1: ecuación física de duración e inventario de información sin usar — 2026-11-15
- 🎯 Cambio de prioridad acordado: conocimiento antes que entregables; agotar la información disponible con modelos físicos y rigor.
- ✔ `docs/03_data_science/RESEARCH_LOG.md` (bitácora), `src/flamesafe/models/aft.py` (AFT con censura y familias de error),
  `src/flamesafe/physics/spherical_flame.py` (grupos de llama esférica), 6 tests y `scripts/research/r01_physics_burn_time.py`.
- 📌 Hallazgos (candidatos):
  - **Corrección:** CFI-G y Flame Design son llamas de difusión **esféricas** (quemador poroso), no de chorro. M-01 corregida.
  - **Weibull de M1 v1 es sobreconfiado** fuera de muestra; log-logística lo corrige. M1 v2 debe cambiar de familia.
  - **Ecuación física** (llama normal): ln t = 16.6 − 19.5·(1000/Tad) − 0.49 ln p − 0.57 ln ṁ + 1.30 ln L. Iguala al modelo
    empírico con menos parámetros y sin conocer el combustible (mejora fuera de muestra +0.14, IC −0.09 a +0.41: no concluyente).
    La dependencia con Tad y con la presión coincide entre llamas normales e inversas.
  - **Negativo:** la temperatura crítica de extinción no se identifica desde la tabla resumen.
  - **Censura informativa:** parte de los cortes de flujo son por límite de temperatura del quemador (comentarios en silver).
  - "Autoextinguida" puede ser transición a **llama fría** (invisible, sigue reaccionando).
- 📦 Información sin usar: 656 series temporales por prueba (radiómetros, PMT, termopares; ≈ 2.7 GB), comentarios por prueba,
  EventData (energía del ignitor), BASS-II, Saffire-2, SPICE y gotas.
- ✔ Decisión tomada: ADR-0005 aceptado (ver la entrada siguiente).
- ▶ Siguiente sin descargas: llevar `comments`/`color`/EventData a gold, M1 v2 (log-logística + riesgos competitivos) y gotas (RQ2).

### Investigación · iteración 2: series temporales por prueba (ADR-0005) — 2026-11-15
- ✔ **ADR-0005** aceptado: extensión opcional con manifiesto propio (`configs/timeseries_manifest.yaml`, 3,000 MB). El manifiesto
  núcleo y su presupuesto (150 archivos, 500 MB) no cambian. El ADR de decisiones PHY y de la tasa de FLEX pasa a ser **ADR-0006**.
- ✔ `flamesafe timeseries`: 3,325 archivos, 2,716.5 MB, 0 diferencias de tamaño. `flamesafe ts-features`: 655 pruebas, 0 errores.
- ✔ `src/flamesafe/pipeline/timeseries.py` (10 tests), descarga en paralelo en `ingestion/download.py`,
  `scripts/research/r02_timeseries_transfer.py`.
- 📌 Hallazgos (candidatos; detalle en RESEARCH_LOG R7–R11):
  - Detector validado: 99.6 % de acuerdo con el modo de extinción del investigador en CFI-G y Spearman 0.995 en duración.
  - Flame Design gana duración y modo de extinción en 244 llamas (antes no tenía).
  - **La ecuación física ajustada solo con CFI-G predice Flame Design (etileno, otra campaña) sin reajuste:** índice C 0.93
    (IC 0.80–0.96), pendiente de calibración 1.16 (IC 0.72–1.48). En llamas inversas ordena (C 0.82) pero no calibra.
  - Censura informativa confirmada: en CFI-G normal, 22 de 30 cortes de flujo son por límite térmico del quemador (~728 K).
  - Las llamas autoextinguidas oscilan antes de apagarse (16–90 % con ≥ 5 s, frente a 2–17 % de las cortadas); mediana 8.9 s de anticipo. Preliminar.
- ▶ Siguiente: caudal crítico en las 66 pruebas de rampa, M1 v2 con riesgos competitivos (autoextinción / límite térmico / temporizador)
  y predicción para la base lunar, validación de la oscilación como precursor, y llevar `acme__timeseries_features` a gold.

### Investigación · iteración 3 y visión del producto — 2026-11-16
- ✔ `main` al día: PR #7 integrado y el modelo de Cox de Hugo-Edel (`notebooks/03_modeling/03_m2_cox_survival.ipynb`).
- ✔ `src/flamesafe/physics/thermochem.py` (Zst y Tad con Cantera, validados contra 587 pruebas), 3 tests, Cantera en el extra `analysis`.
- ✔ `scripts/research/r03_m1v2_lunar_ramps.py` y RESEARCH_LOG R12–R15.
- 📌 Hallazgos (candidatos):
  - **M1 v2**: ecuación física log-logística sobre 255 llamas normales de las dos campañas; índice C 0.89 dejando fuera un día,
    calibración razonable y estable frente al supuesto de censura por límite térmico.
  - **Primera lectura para la base lunar** (30 % O₂, 70 kPa, µg): duración mediana ~60 s (IC 90 % 47–75), unas 4–5 veces la de la
    cabina ISS. Nivel de evidencia B: interpolación del modelo, sin pruebas cercanas.
  - Pruebas de rampa: tendencia coherente con un caudal crítico, sin ley ajustable (exploratorio).
- ✔ **Visión del producto**: `docs/05_dashboard/PRODUCT_VISION.md` y **ADR-0007** (lecturas del modelo con niveles de evidencia en
  la primera versión). Modifica la fila «Predicciones» del plan RAG; pendiente de que sus responsables lo incorporen.
- ▶ Siguiente: piloto de video en la nube (requiere ADR y acceso confirmado), unificar el Cox de Hugo con la censura por límite
  térmico, llevar `acme__timeseries_features` a gold, revisión PHY, gotas y sólidos.

