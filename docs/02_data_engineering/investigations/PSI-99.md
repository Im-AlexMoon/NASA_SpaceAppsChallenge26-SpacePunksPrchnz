# PSI-99 — SAFFIRE-II · Spacecraft Fire Experiment-II

<!-- AUTO:BEGIN — generado por `flamesafe profile`; no editar a mano dentro de este bloque -->

| Campo | Valor (PSI) |
|---|---|
| DOI de datos | 10.60555/2chp-m469 |
| Tipo | Microgravity Investigation |
| Sub-área | Surface Combustion |
| Programa / plataforma | Cygnus Spacecraft / Cygnus Spacecraft |
| Hardware | Cygnus Pressurized Cargo Module, SAFFIRE |
| Centro | Glenn Research Center (GRC) |
| Periodo | 2016-09-30 → 2017-04-01 |
| Licencia | Creative Commons Zero v1.0 Universal |
| Investigaciones relacionadas | — |
| Snapshot | snapshot_2026-11-14 |

### Inventario (L1)

| Archivos `added` | Tablas exp. (fuera de `added`) | `removed` | Publicaciones (con DOI) | GB expuestos | GB registrados | Acceso |
|---:|---:|---:|---:|---:|---:|---|
| 0 | 1 (1) | 0 | 7 (5) | 0.00 | 16.93 | `experimental_table_only` |

**Objetivo (texto PSI):**

> The objectives of SAFFIRE-II are to determine how rapidly a large scale fire grows in low-gravity and to investigate the low-g flammability limits compared to those obtained in NASA’s normal gravity material flammability screening test.

**Hipótesis (texto PSI):**

> This investigation hypothesizes that due to large differences between fire behavior in normal and reduced gravity, the use of terrestrial fires and fire standards to design spacecraft fire safety systems presents an inherent risk to the vehicle because of the significant level of uncertainty. While this approach has been successful thus far, the uncertainty and risk will increase as exploration missions venture further from earth with considerably longer transit times for a safe return. There is a significant lack of microgravity data available for spacecraft designers on which to base their fire safety designs and procedures. To address this knowledge gap, this investigation proposed to …

### Archivos perfilados (L2)

#### `PSI-99_Experimental table_SAFFIRE-2.csv`

- Lista: `experimentalTable` · 1,973 bytes · sha256 `3c24390b9ef86f3d…` · HTTP 200
- CSV · encoding `utf-8` · delimitador `,` · encabezado en fila 1 · filas no vacías **15** / físicas 15 · **17** columnas · bloques lado a lado: 1

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Sample Number |  | text | 15 | 15 | 2-1, 2-2, 2-3 |  |
| 2 | Material |  | text | 9 | 6 | Silicone, Cotton-Fiberglass (SIBAL), PMMA & Nomex |  |
| 3 | Samle Thickness |  | text | 9 | 7 | 0.27 mm, 0.61 mm, 1.03 mm |  |
| 4 | Sample Length |  | text | 9 | 2 | 29 cm, 5 and 24 cm |  |
| 5 | Sample Width (cm) | cm | text | 9 | 1 | 5 cm |  |
| 6 | Air Flow (cm/s) | cm/s | text | 9 | 1 | 20 cm/s |  |
| 7 | Percent O2 (Note 1) | Note 1 | text | 9 | 4 | ~ 21.5, ~ 22.1, 22.1 to 22.0 |  |
| 8 | Ignition Power (W) | W | text | 9 | 2 | 80 W, 97 W |  |
| 9 | Ignition Time (s) | s | text | 9 | 2 | 9.2 s, 30 s |  |
| 10 | Burn Time (s) | s | text | 9 | 6 | Insignificant, 145 s, 115 s |  |
| 11 | Flow Direction |  | text | 9 | 2 | Concurrent, Opposed |  |
| 12 | ?-g Burn Length |  | text | 9 | 5 | ~ 0, 29 cm, 5 cm & 0 (note 2) |  |
| 13 | ?-g Spread Length |  | text | 9 | 5 | n/a, 2.1 mm/s, 2.6 mm/s |  |
| 14 | 1-g Burn Length |  | text | 9 | 4 | Complete, 7.6 cm, ~ 0 |  |
| 15 | 1-g Spread Rate |  | text | 9 | 5 | Acceleratory, 1.2 mm/s, n/a |  |
| 16 | Camera 1 |  | text | 8 | 8 | S1C1, n/a, S4C1 |  |
| 17 | Camera 2 |  | text | 9 | 7 | S1C2, S2C2, S3C2 |  |

### Publicaciones con DOI (primeras 8)

- Flame spread: Effects of microgravity and scale — doi:10.1016/j.combustflame.2018.10.012
- Buoyancy effects on concurrent flame spread over thick PMMA — doi:10.1016/j.combustflame.2018.10.016
- Concurrent Flame Spread Over Two-Sided Thick PMMA Slabs in Microgravity — doi:10.1007/s10694-019-00863-3
- Transient flame growth and spread processes over a large solid fabric in concurrent low-speed flows in microgravity – Model versus experiment — doi:10.1016/j.proci.2018.05.168
- Evaluation of gas and particle sensors for detecting spacecraft-relevant fire emissions — doi:10.1016/j.firesaf.2020.102977

<!-- AUTO:END -->

## Evaluación (manual — DE/PHY)

> Primera pasada DE-04 (2026-11-14) basada en el bloque automático y en las muestras L2. La clasificación
> Medida / Calculada / Log es **propuesta DE — pendiente de validación PHY (PHY-02)**.

### Resumen propio
SAFFIRE-II: 9 muestras de distintos materiales (silicona, SIBAL, PMMA, Nomex) en Cygnus, con flujo concurrente y opuesto.

### Granularidad y variables clave
| Archivo | Fila = … | Condición | Resultado | Notas |
|---|---|---|---|---|
| ET SAFFIRE-2 (15 filas, 9 con datos) | 1 muestra | material, espesor, flujo, % O₂, ignición, dirección | longitud quemada y tasa de propagación **en µg y en 1 g** | todo como texto con unidad (`2.1 mm/s`, `~ 0`, `n/a`, `Acceleratory`) |

### Problemas de calidad / acceso
- El encabezado `?-g` es casi seguro "µ-g" con el carácter perdido en la fuente. Hay un error tipográfico en `Samle Thickness`.
- Es la **única tabla de PSI con tasas de propagación en µg** (pocas y con texto). Separar µg de 1 g sin mezclarlas.

### Valor para el proyecto
- **Pilar:** prevención. **RQ:** RQ3. Es una comparación µg vs 1 g muy valiosa para la narrativa (cota de gravedad).
- **Triage (borrador):** R1 3 · R2 2 · R3 1 · R4 2 · R5 1 · R6 2 → **Tier 2** por singularidad (ajuste PHY).
