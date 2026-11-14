# PSI-69 — FLEX · Flame Extinguishment Experiment

<!-- AUTO:BEGIN — generado por `flamesafe profile`; no editar a mano dentro de este bloque -->

| Campo | Valor (PSI) |
|---|---|
| DOI de datos | 10.60555/mbq8-0451 |
| Tipo | Microgravity Investigation |
| Sub-área | Spacecraft Fire Safety |
| Programa / plataforma | International Space Station (ISS) / International Space Station (ISS) |
| Hardware | Combustion Integrated Rack (CIR)-Fluids and Combustion Facility (FCF), Multi-user Droplet Combustion Appartatus (MDCA) |
| Centro | Glenn Research Center (GRC) |
| Periodo | 2007-08-01 → 2016-07-31 |
| Licencia | Creative Commons Zero v1.0 Universal |
| Investigaciones relacionadas | — |
| Snapshot | snapshot_2026-11-14 |

### Inventario (L1)

| Archivos `added` | Tablas exp. (fuera de `added`) | `removed` | Publicaciones (con DOI) | GB expuestos | GB registrados | Acceso |
|---:|---:|---:|---:|---:|---:|---|
| 0 | 1 (1) | 0 | 51 (45) | 0.00 | 923.83 | `experimental_table_only` |

**Objetivo (texto PSI):**

> The FLEX (Flame Extinguishment Experiment) investigation aims to map the flammability limits of liquid fuels in microgravity environments, measure the effectiveness of various gaseous fire suppressants such as CO2, He, and SF6, and develop reliable predictive models for combustion limits under reduced gravity conditions. The mission seeks to validate and improve simplified models by incorporating detailed chemical reactions, heat transfer, and material movement, using both space-based data and extensive ground-based tests. Key flight experiment goals include obtaining high-resolution measurements of droplet burning rates, flame extinction behavior, heat radiation, soot levels, and …

**Hipótesis (texto PSI):**

> The primary hypothesis of the FLEX mission is that microgravity conditions fundamentally alter the combustion and extinction characteristics of liquid fuel droplets due to changes in species and energy transport dynamics, radiative heat loss, and chemical kinetics. Specifically, the hypothesis posits that the lack of buoyant convection in microgravity will lead to significant differences in the flammability limits and suppression efficacy of various fire suppressant agents compared to normal gravity conditions. This hypothesis underpins the design of the FLEX experiments, which aim to map flammability boundaries, quantify suppressant efficacy, and develop predictive models to improve fire …

### Archivos perfilados (L2)

#### `PSI-69_Experimental table_FLEX.csv`

- Lista: `experimentalTable` · 24,776 bytes · sha256 `37c88ce8ae9391b7…` · HTTP 200
- CSV · encoding `cp1252` · delimitador `,` · encabezado en fila 1 · filas no vacías **274** / físicas 274 · **15** columnas · bloques lado a lado: 1

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | FLEX Test # |  | numeric | 274 | 274 | 1 … 274 |  |
| 2 | FLEX Identifier |  | text | 274 | 273 | 20CAL08, 20CAL10, 20CAL12 |  |
| 3 | Test Date |  | text | 274 | 80 | 3/5/2009, 3/31/2009, 4/10/2009 |  |
| 4 | Test GMT |  | text | 273 | 269 | 17:22:03, 19:20:06, 21:17:46 |  |
| 5 | Fuel |  | text | 274 | 2 | Methanol, Heptane |  |
| 6 | Ambient pressure; mmHg | mmHg | numeric | 274 | 183 | 0 … 2320 |  |
| 7 | O initial ambient composition; mole fraction | mole fraction | numeric | 274 | 15 | 0.12 … 0.34 |  |
| 8 | N initial ambient composition; mole fraction | mole fraction | numeric | 274 | 33 | 0.09 … 0.88 |  |
| 9 | CO initial ambient composition; mole fraction | mole fraction | numeric | 274 | 14 | 0 … 0.7 |  |
| 10 | He initial ambient composition; mole fraction | mole fraction | numeric | 274 | 10 | 0 … 0.45 |  |
| 11 | Droplet initial diameter; mm | mm | numeric | 268 | 164 | 1.1 … 4.67 | `–`×6 |
| 12 | Visible flame extinction diameter; mm | mm | mixed | 225 | 146 | 0 … 4.6 | `–`×28 |
| 13 | Burning rate; mm | mm | numeric | 258 | 60 | 0.05 … 1.06 |  |
| 14 | Burn time; s | s | numeric | 268 | 164 | 0.3 … 39.2 | `~6`×1, `~9`×1 |
| 15 | Test end |  | text | 274 | 3 | Disruption, Extinction, Completion |  |

### Publicaciones con DOI (primeras 8)

- A Numerical Study On The Extinction Characteristics Of Droplet Combustion Under Microgravity Conditions — doi:10.2514/6.2012-1252
- Tethered methanol droplet combustion in carbon-dioxide enriched environment under microgravity conditions — doi:10.1016/j.combustflame.2011.06.014
- Activation energy asymptotics for methanol droplet extinction in microgravity — doi:10.1016/j.combustflame.2013.05.011
- Experimental Study of Initial Diameter Effects on Convection-free Droplet Combustion in the Standard Atmosphere for n-Heptane, n-Octane, and n-Decane: International Space Station and Ground-based Experiments — doi:10.2514/6.2014-1019
- Isolated n-heptane droplet combustion in microgravity: “Cool Flames” – Two-stage combustion — doi:10.1016/j.combustflame.2013.09.011
- Theory of the propagation dynamics of spiral edges of diffusion flames in von Kármán swirling flows — doi:10.1016/j.combustflame.2010.08.015
- Analysis of the melt phase of a rotating polymer disc supporting a diffusion flame — doi:10.1017/jfm.2011.349
- Partial-Burning Regime for Quasi-Steady Droplet Combustion Supported by Cool Flames — doi:10.2514/1.j054437

<!-- AUTO:END -->

## Evaluación (manual — DE/PHY)

> Primera pasada DE-04 (2026-11-14) basada en el bloque automático y en las muestras L2. La clasificación
> Medida / Calculada / Log es **propuesta DE — pendiente de validación PHY (PHY-02)**.

### Resumen propio
FLEX: combustión de gotas de metanol y heptano en el MDCA. Varía O₂, CO₂, He y presión (0–2320 mmHg) para mapear límites de
inflamabilidad y la **eficacia de supresores**.

### Granularidad y variables clave
| Archivo | Fila = … | Condición | Resultado (medido) | Calculadas | Notas |
|---|---|---|---|---|---|
| ET FLEX (274) | 1 prueba | combustible, presión (mmHg), fracciones molares de O₂, N₂, CO₂ y He, D₀ | **D de extinción visible**, **tasa de quemado**, **tiempo de quemado**, **`Test end`** (Extinction 186 / Disruption 61 / Completion 27) | — | CO₂ > 0 en 123 pruebas; He > 0 en 50 |

### Problemas de calidad / acceso
- Archivo en **cp1252**. Los encabezados perdieron los subíndices en la fuente ("O", "N", "CO" en vez de O₂, N₂, CO₂): renombrar explícitamente.
- La unidad de `Burning rate` dice "mm"; físicamente debería ser mm²/s (constante K de la ley d²). Hay que confirmarlo con la publicación.
- El token `–` (raya) significa "sin dato" en D₀ y D de extinción. Hay `~6` y `~9` en el tiempo de quemado (valores aproximados → flag).
- Una prueba con presión 0 mmHg: es físicamente imposible, así que se marca como error.
- `experimental_table_only`: el archivo crudo (924 GB registrados) no está expuesto.

### Valor para el proyecto
- **Pilar:** supresión. **Entornos:** todos (diseño de extintores por dilución, cabinas a baja presión).
- **RQ:** RQ2 y M2 (extinción vs. diluyente y presión). También sirve como clasificación (`Test end`).
- **Triage (borrador):** R1 3 · R2 2 · R3 3 · R4 3 · R5 3 · R6 2 → **Tier 1**.
