# Metodología de exploración y triage de las 24 investigaciones PSI

> **Objetivo:** decidir, con criterios explícitos y repetibles, qué información de PSI es realmente útil para las preguntas de
> investigación — sin descargar el archivo completo. Tareas DE-03 → DE-05, PHY-02. Cierra en **G1**.

## 1. Embudo en 4 niveles

| Nivel | Pregunta | Qué se descarga | Salida | Aplica a |
|---|---|---|---|---|
| **L0 · Metadatos** | ¿Qué es y qué estudió? | JSON de detalle (KB) | fila en catálogo | 24/24 |
| **L1 · Inventario** | ¿Qué archivos expone y en qué formatos? | nada (listado de `added` + `experimentalTable`) | conteos por extensión/categoría, bytes, flag `experimental_table_only` | 24/24 |
| **L2 · Muestreo de formato** | ¿Cómo están estructurados los datos? | tablas experimentales + 1–3 archivos representativos (< 20 MB c/u) | perfil `investigations/PSI-XX.md` | candidatas con puntaje L1 ≥ umbral |
| **L3 · Adquisición** | ¿Qué entra al pipeline? | archivos del manifest | `configs/acquisition_manifest.yaml` → `acquisition_manifest.csv` | según ADR-0002 |

Regla de presupuesto: L2 ≤ 100 MB total, L3 ≤ 500 MB total. Video/ZIP/imágenes solo con ADR.

## 2. Perfil de formato (L2)

> **Ejecutado en DE-04 (2026-11-14):** `flamesafe profile` → 60 archivos, 50.3 MB. Perfiles e índice con tiers en borrador:
> [investigations/README.md](investigations/README.md).

Por cada investigación candidata, llenar [investigations/_TEMPLATE.md](investigations/_TEMPLATE.md):
estructura de carpetas · formatos · encabezados reales · unidades · tokens faltantes/errores · granularidad (fila = prueba, día,
punto de telemetría, resumen) · variables controladas vs. medidas vs. calculadas · documentos de ayuda (readme, test matrix) ·
publicaciones con DOI · problemas de acceso (404, archivos vacíos).

**Clave:** distinguir siempre *variable medida* (p. ej. diámetro de extinción) de *calculada* (p. ej. Tad) y de *log de prueba*
(p. ej. fecha, número de muestra). Solo las medidas son evidencia experimental directa.

## 3. Rúbrica de puntaje (0–3 por criterio)

| Criterio | Peso | 0 | 1 | 2 | 3 |
|---|---:|---|---|---|---|
| **R1 Relevancia fire-safety** (PHY) | 0.30 | sin relación | indirecta | un pilar (prev./det./sup.) | pilar central + entornos tripulados |
| **R2 Accesibilidad** | 0.15 | nada descargable | solo docs | tabla resumen | tabla + archivos crudos verificados |
| **R3 Estructura tabular** | 0.20 | solo video/imágenes | texto libre | tablas heterogéneas | tabla limpia fila = prueba |
| **R4 Riqueza de variables** | 0.20 | sin variables de condición | 1 variable | O₂ *o* presión *o* flujo + resultado | varias condiciones + resultado medido |
| **R5 Tamaño muestral** | 0.10 | < 5 filas | 5–30 | 30–150 | > 150 |
| **R6 Comparabilidad** | 0.05 | aislada | comparte hardware | comparte variables | variables equivalentes con otras |

**Puntaje = Σ peso × criterio / 3** (0–1). Tier: **1 Primary** ≥ 0.70 · **2 Supporting** 0.45–0.70 · **3 Context** < 0.45.
PHY puede subir/bajar un tier con justificación escrita (p. ej. una investigación pequeña pero única en supresión).

**Gates (añadidos en DE-05, ADR-0002):** el puntaje ponderado premia mucho la relevancia (R1) y el acceso (R2). Para que un registro
sin resultado analizable no llegue a "Primary" solo por ser relevante, cada tier exige además:

| Tier | Condición adicional | Si no se cumple |
|---|---|---|
| 1 | R4 = 3 (resultado medido bajo condiciones variadas) **y** R3 ≥ 2 **y** R5 ≥ 2 (n ≥ 30) | baja a Tier 2 |
| 2 | R3 ≥ 2 **o** R4 ≥ 2 (hay algo analizable) | baja a Tier 3 |

Los puntajes, pilares, entornos y justificaciones viven en [configs/triage.yaml](../../configs/triage.yaml).
`flamesafe triage` calcula y renderiza la matriz (§4) y `triage_matrix.csv`. Un `override` (PHY) requiere `tier`, `reason` y `by`.

## 4. Matriz de triage (salida de DE-05)

Archivo generado: [triage_matrix.csv](triage_matrix.csv). **Tier ≠ alcance del MVP:** el tier mide calidad y relevancia del dato.
Qué entra al MVP se decide por RQ en [ADR-0002](../01_management/decisions/ADR-0002-mvp-data-scope.md).

<!-- TRIAGE:BEGIN — generado por `flamesafe triage` desde configs/triage.yaml -->

| PSI | Acrónimo | R1 | R2 | R3 | R4 | R5 | R6 | Score | Tier | Pilar | Entornos | RQ | Justificación |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|---|
| [PSI-159](investigations/PSI-159.md) | ACME CFI-G | 3 | 3 | 3 | 3 | 3 | 3 | 1.000 | **1** | prevencion | nave, estacion, base_lunar, rover, marte | RQ1, RQ5 | Ignición, autoextinción vs. corte de flujo y llama fría por prueba (333); XO2 0.12–0.85 y 0.5–3.3 bar cubren atmósferas de exploración. |
| [PSI-10](investigations/PSI-10.md) | ACME/Flame Design | 3 | 3 | 2 | 3 | 3 | 3 | 0.933 | **1** | prevencion | nave, estacion, base_lunar, rover, marte | RQ1, RQ5 | 327 pruebas con XO2 hasta 0.85 y 0.42–3 atm; el resultado (ignición) solo existe en el EventData del Chamber Calculator: R4=3 condicionado a esa unión. |
| [PSI-69](investigations/PSI-69.md) | FLEX | 3 | 2 | 3 | 3 | 3 | 2 | 0.933 | **1** | supresion, prevencion | nave, estacion, base_lunar, rover, marte | RQ2, RQ5 | 274 gotas con O2/CO2/He/presión variados y extinción, tasa y tiempo de quemado medidos; experimental_table_only (archivo crudo no expuesto). |
| [PSI-101](investigations/PSI-101.md) | SAME-R | 3 | 3 | 2 | 3 | 3 | 2 | 0.917 | **1** | deteccion | nave, estacion, base_lunar, rover | RQ4, RQ5 | 109 pruebas de humo (material, velocidad, envejecimiento) con respuesta de detectores y aerosol en 44 corridas HKP; requiere unir HKP↔ET por número de prueba. |
| [PSI-39](investigations/PSI-39.md) | CFI | 2 | 3 | 3 | 3 | 3 | 3 | 0.900 | **1** | prevencion, supresion | nave, estacion, base_lunar | RQ2, RQ1, RQ5 | DataSummary: k y Dext de llama caliente/fría en 146 pruebas, con He y 0.5–5 atm; comparable con FLEX y PSI-117. |
| [PSI-107](investigations/PSI-107.md) | SPICE | 2 | 3 | 2 | 3 | 3 | 2 | 0.817 | **1** | deteccion, prevencion | nave, estacion | RQ4, RQ5 | Longitud de punto de humo medida vs. combustible, boquilla, caudal y aire (SmokePointReview); relevancia indirecta (formación de hollín). |
| [PSI-98](investigations/PSI-98.md) | SAFFIRE-I | 3 | 3 | 3 | 2 | 3 | 2 | 0.917 | **2** ⟵ 1 (gate T1: R4<3) | deteccion, prevencion | nave, estacion | RQ4, RQ5 | Telemetría de incendio a escala (radiómetros, detectores de humo FIZ, P/T de cabina), disponible desde DE-01; condiciones casi fijas (2 muestras). |
| [PSI-100](investigations/PSI-100.md) | SAFFIRE-III | 3 | 3 | 3 | 2 | 3 | 2 | 0.917 | **2** ⟵ 1 (gate T1: R4<3) | deteccion, prevencion | nave, estacion | RQ4, RQ5 | Telemetría más rica de PSI; exportes CSV/XLSX que no deben concatenarse; 2 muestras → pocas condiciones. |
| [PSI-102](investigations/PSI-102.md) | SAME | 3 | 3 | 2 | 3 | 1 | 2 | 0.850 | **2** ⟵ 1 (gate T1: R5<2) | deteccion | nave, estacion, base_lunar, rover | RQ4, RQ5 | Material, flujo y pérdida de masa medidos, pero solo 8 condiciones → gate de Tier 1 (n). |
| [PSI-25](investigations/PSI-25.md) | BASS-II | 3 | 3 | 2 | 2 | 2 | 2 | 0.817 | **2** ⟵ 1 (gate T1: R4<3) | prevencion | nave, estacion, base_lunar, rover | RQ3, RQ5 | Sólidos con O2 y flujo variados (129), pero sin resultado de inflamabilidad tabulado (propagación solo en video) → gate de Tier 1. |
| [PSI-26](investigations/PSI-26.md) | BASS | 3 | 3 | 2 | 2 | 2 | 2 | 0.817 | **2** ⟵ 1 (gate T1: R4<3) | prevencion | nave, estacion, base_lunar, rover | RQ3, RQ5 | As-run matrix con O2, presión y CO2 (130); resultados solo como observaciones en texto libre. |
| [PSI-47](investigations/PSI-47.md) | DAFT / DAFT-2 | 2 | 3 | 2 | 1 | 3 | 2 | 0.683 | **2** | deteccion | estacion, base_lunar, marte | RQ4, RQ5 | Lecturas de P-Trak/DustTrak de polvo en la ISS; contexto de falsas alarmas por polvo lunar; una sola condición. |
| [PSI-99](investigations/PSI-99.md) | SAFFIRE-II | 3 | 2 | 1 | 2 | 1 | 2 | 0.667 | **2** | prevencion | nave, estacion | RQ3, RQ5 | Única tabla con propagación en µg y en 1 g (9 muestras, en texto con unidades); valor narrativo para el acotamiento de gravedad. |
| [PSI-117](investigations/PSI-117.md) | — (tierra) | 2 | 2 | 2 | 2 | 1 | 3 | 0.650 | **2** | prevencion, supresion | nave, estacion | RQ2, RQ5 | Investigación de tierra con datos de figuras (Dext, k; experimento vs. modelo); pocos puntos; útil como validación y baseline físico de M2. |
| [PSI-68](investigations/PSI-68.md) | FLEX-2 | 3 | 2 | 1 | 1 | 1 | 2 | 0.600 | **3** ⟵ 2 (gate T2: R3 y R4 < 2) | supresion | nave, estacion, base_lunar, rover, marte | RQ2, RQ5 | Solo rangos de condiciones por combustible (8 filas); define el espacio de diseño de FLEX-2 pero no es analizable. |
| [PSI-22](investigations/PSI-22.md) | ACME E-FIELD Flames | 2 | 2 | 1 | 1 | 2 | 2 | 0.533 | **3** ⟵ 2 (gate T2: R3 y R4 < 2) | prevencion | base_lunar, marte | RQ5 | Proxy de gravedad parcial (campo eléctrico) para la narrativa; experimental_table_only, solo resumen por día. |
| [PSI-20](investigations/PSI-20.md) | ACME BRE | 2 | 2 | 1 | 1 | 1 | 2 | 0.500 | **3** ⟵ 2 (gate T2: R3 y R4 < 2) | prevencion | nave, estacion | RQ3, RQ5 | Emulador de tasa de quemado de materiales (destacado en el reto) pero la tabla es por día, con O2 como lista y presión no identificada. |
| [PSI-115](investigations/PSI-115.md) | — (tierra) | 2 | 2 | 1 | 1 | 0 | 2 | 0.467 | **3** ⟵ 2 (gate T2: R3 y R4 < 2) | deteccion | nave, estacion | RQ4, RQ5 | Simulación de tierra del humo de SAME (.dat no perfilados); contexto de modelado. |
| [PSI-21](investigations/PSI-21.md) | ACME CLD Flame | 1 | 2 | 1 | 1 | 2 | 2 | 0.433 | **3** | prevencion | nave, estacion | RQ5 | Resumen por día (32) con rangos en texto; sin resultados medidos. |
| [PSI-142](investigations/PSI-142.md) | — (tierra) | 1 | 2 | 2 | 1 | 1 | 0 | 0.433 | **3** | prevencion | nave, estacion | RQ5 | Índice de datos de figuras CFE/HFE; no comparable directamente con las tablas del MVP. |
| [PSI-23](investigations/PSI-23.md) | ACME s-Flame | 1 | 2 | 1 | 1 | 1 | 2 | 0.400 | **3** | prevencion | nave, estacion | RQ5 | Resumen por día (18) y test log; sin resultados medidos en tablas; relevancia indirecta (estructura de llamas con hollín). |
| [PSI-106](investigations/PSI-106.md) | SLICE | 1 | 2 | 2 | 0 | 1 | 2 | 0.400 | **3** | prevencion | nave, estacion | RQ5 | Solo fecha y tipo de combustible (12). |
| [PSI-60](investigations/PSI-60.md) | — (tierra) | 1 | 1 | 0 | 0 | 0 | 1 | 0.167 | **3** | deteccion | nave, estacion | RQ5 | Investigación de tierra; solo un archivo de metadatos. |
| [PSI-62](investigations/PSI-62.md) | — (tierra) | 1 | 1 | 0 | 0 | 0 | 1 | 0.167 | **3** | prevencion | nave, estacion | RQ5 | Investigación de tierra; solo un archivo de metadatos. |

Resumen: Tier 1: 6 · Tier 2: 8 · Tier 3: 10

<!-- TRIAGE:END -->

## 5. Criterios de salida (G1)
- 24/24 con L0 + L1 · candidatas con L2 · matriz con justificación · manifest dentro de presupuesto · ADR-0002 aceptado.
- Hallazgos de acceso (404, `experimental_table_only`, registros de tierra) registrados en [DATA_SOURCES.md](DATA_SOURCES.md).
