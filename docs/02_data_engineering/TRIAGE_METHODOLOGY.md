# Metodología de exploración y triage de las 24 investigaciones PSI

> **Objetivo:** decidir, con criterios explícitos y repetibles, qué información de PSI es realmente útil para las preguntas de
> investigación — sin descargar el archivo completo. Tareas DE-03 → DE-05, PHY-02. Cierra en **G1**.

## 1. Embudo en 4 niveles

| Nivel | Pregunta | Qué se descarga | Salida | Aplica a |
|---|---|---|---|---|
| **L0 · Metadatos** | ¿Qué es y qué estudió? | JSON de detalle (KB) | fila en catálogo | 24/24 |
| **L1 · Inventario** | ¿Qué archivos expone y en qué formatos? | nada (listado de `added` + `experimentalTable`) | conteos por extensión/categoría, bytes, flag `experimental_table_only` | 24/24 |
| **L2 · Muestreo de formato** | ¿Cómo están estructurados los datos? | tablas experimentales + 1–3 archivos representativos (< 20 MB c/u) | perfil `investigations/PSI-XX.md` | candidatas con puntaje L1 ≥ umbral |
| **L3 · Adquisición** | ¿Qué entra al pipeline? | archivos del manifest | `configs/sources.yaml::investigations` | Tier 1–2 |

Regla de presupuesto: L2 ≤ 100 MB total, L3 ≤ 500 MB total. Video/ZIP/imágenes solo con ADR.

## 2. Perfil de formato (L2)

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

## 4. Matriz de triage (salida de DE-05)

Archivo: `docs/02_data_engineering/triage_matrix.csv` (generado) + resumen aquí.

| PSI-ID | Acrónimo | Pilar | Entorno | R1 | R2 | R3 | R4 | R5 | R6 | Score | Tier | RQ que habilita | Justificación |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| _por llenar_ | | | | | | | | | | | | | |

## 5. Criterios de salida (G1)
- 24/24 con L0 + L1 · candidatas con L2 · matriz con justificación · manifest dentro de presupuesto · ADR-0002 aceptado.
- Hallazgos de acceso (404, `experimental_table_only`, registros de tierra) registrados en [DATA_SOURCES.md](DATA_SOURCES.md).
