# PSI-39 — CFI · Cool Flames Investigation

<!-- AUTO:BEGIN — generado por `flamesafe profile`; no editar a mano dentro de este bloque -->

| Campo | Valor (PSI) |
|---|---|
| DOI de datos | 10.60555/m6pj-a914 |
| Tipo | Microgravity Investigation |
| Sub-área | Droplets |
| Programa / plataforma | International Space Station (ISS) / International Space Station (ISS) |
| Hardware | Multi-User Droplet Combustion Apparatus (MDCA), Combustion Integrated Rack (CIR) |
| Centro | Glenn Research Center (GRC) |
| Periodo | 2020-10-01 → 2021-10-20 |
| Licencia | Creative Commons Zero v1.0 Universal |
| Investigaciones relacionadas | PSI-69 |
| Snapshot | snapshot_2026-11-14 |

### Inventario (L1)

| Archivos `added` | Tablas exp. (fuera de `added`) | `removed` | Publicaciones (con DOI) | GB expuestos | GB registrados | Acceso |
|---:|---:|---:|---:|---:|---:|---|
| 2,831 | 1 (1) | 2,698 | 7 (6) | 718.89 | 718.89 | `available` |

Categorías: Raw Data 2,791.0 (718.85 GB) · Analyzed Data 32.0 (0.01 GB) · Science Documents 3.0 (0.02 GB) · Presentations 2.0 (0.01 GB) · Engineering Documents 1.0 (0.00 GB) · Reports 1.0 (0.00 GB) · metadata 1.0 (0.00 GB)
Extensiones: `.txt` 1,793 · `.zip` 338 · `.meta` 236 · `.mp4` 126 · `.ts` 120 · `.metadata` 117 · `.pdf` 48 · `.pxp` 29

**Objetivo (texto PSI):**

> The objectives of this investigation are to:     1) Examine the combustion behavior of n-dodecane and mixtures of n-dodecane/iso-dodecane at pressures ranging from 0.25 atm to 5 atm.     2) Analyze the effects of helium dilution on cool flame behavior.     3) Examine the behavior of combustion characteristics.     4) Investigate the relationship between droplet size, pressure, and flame extinction, and (5) understand the consequence of soot formation during cool flame combustion.

**Hipótesis (texto PSI):**

> Flame combustion of liquid hydrocarbon fuels such as n-dodecane, n-dodecane/iso-dodecane mixtures, and faresane in microgravity can provide insights into low-temperature chemical kinetics, revealing critical parameters like droplet extinction diameters and flame dynamics that are not observable on Earth.

### Archivos perfilados (L2)

#### `PSI-39_Experimental table_CFI.csv`

- Lista: `experimentalTable` · 7,792 bytes · sha256 `fb898e28762353aa…` · HTTP 200
- CSV · encoding `utf-8` · delimitador `,` · encabezado en fila 1 · filas no vacías **87** / físicas 87 · **10** columnas · bloques lado a lado: 1

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Flex Number |  | numeric | 87 | 79 | 1206 … 1387 |  |
| 2 | Test Date |  | text | 87 | 23 | 9-Mar-17, 21-Mar-17, 27-Mar-17 |  |
| 3 | Local Time |  | text | 87 | 79 | 02:03:08 pm est, 03:53:26 pm est, 04:25:22 pm est |  |
| 4 | CIR |  | text | 87 | 79 | f068a03, f068a07, f068a08 |  |
| 5 | Pressure |  | text | 87 | 7 | 1 atm, 1.25 atm, 2 atm |  |
| 6 | Oxygen |  | numeric | 87 | 2 | 0.17 … 0.21 |  |
| 7 | Nitrogen |  | numeric | 87 | 5 | 0.2 … 0.83 |  |
| 8 | Helium |  | numeric | 87 | 3 | 0 … 0.59 |  |
| 9 | Fiber |  | text | 78 | 2 | No, Yes |  |
| 10 | Fuel |  | text | 87 | 3 | C12H26, [.75]/[.25] C12H26/iso-dodecane, [.60]/[.40] C12H26/iso-dodecane |  |

#### `PSI-39_Science Documents_CFI_DataSummary_Spreadsheet_Jan2021.xlsx`

- Lista: `added` · 208,743 bytes · sha256 `a5b04b6a32bda764…` · HTTP 200
- XLSX · **6** hojas

<details><summary>Hoja <b>Master Sheet</b> — encabezado fila 1, 227 filas no vacías × 10 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Flex Number |  | numeric | 227 | 227 | 1206 … 1431 | `1274A`×1 |
| 2 | Test Date |  | datetime | 227 | 53 | 2017-03-09T00:00:00, 2017-03-21T00:00:00, 2017-03-27T00:00:00 |  |
| 3 | Local Time |  | text | 227 | 226 | 02:03:08 pm est, 03:53:26 pm est, 04:25:22 pm est |  |
| 4 | CIR |  | text | 227 | 226 | f068a03, f068a07, f068a08 |  |
| 5 | Pressure |  | text | 227 | 9 | 1 atm, 1.25 atm, 2 atm |  |
| 6 | Oxygen |  | numeric | 227 | 2 | 0.17 … 0.21 |  |
| 7 | Nitrogen |  | numeric | 227 | 5 | 0.2 … 0.83 |  |
| 8 | Helium |  | numeric | 227 | 3 | 0 … 0.59 |  |
| 9 | Fiber |  | text | 158 | 2 | No, Yes |  |
| 10 | Fuel |  | text | 227 | 4 | C12H26, [.75]/[.25] C12H26/iso-dodecane, [.60]/[.40] C12H26/iso-dodecane |  |

</details>

<details><summary>Hoja <b>DATA</b> — encabezado fila 1, 227 filas no vacías × 20 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Flex Number |  | numeric | 227 | 227 | 1206 … 1431 | `1274A`×1 |
| 2 | D0 ( mm ) | mm | numeric | 148 | 143 | 3.793 … 6.447 |  |
| 3 | Dext, hot ( mm ) | mm | numeric | 144 | 133 | 2.773 … 6.415 |  |
| 4 | khot ( mm^2/s ) | mm^2/s | numeric | 148 | 135 | 0.001 … 1.703 |  |
| 5 | kcool ( mm^2/s ) | mm^2/s | numeric | 127 | 108 | 0.021 … 0.806 |  |
| 6 | Dext,cool ( mm ) | mm | numeric | 122 | 72 | 0 … 6.219 | `NaN`×2 |
| 7 | Pressure (atm) | atm | numeric | 227 | 7 | 0.5 … 5 |  |
| 8 | Reignitions |  | numeric | 151 | 8 | 0 … 7 |  |
| 9 | Extrap CF? |  | numeric | 149 | 2 | 0 … 1 |  |
| 10 | HF Burn Time |  | numeric | 147 | 130 | 1.904 … 21.62 |  |
| 11 | Peak HF Rad |  | numeric | 145 | 143 | 9.103 … 49.99 |  |
| 12 | Peak Water Vapor Rad |  | numeric | 145 | 144 | 3.5 … 27.55 |  |
| 13 | Rad Ratio |  | numeric | 145 | 145 | 0.2522 … 0.7987 |  |
| 14 | 2.5mm rad |  | numeric | 88 | 88 | 1.317 … 18.09 |  |
| 15 | 2.5mm narrow |  | numeric | 88 | 88 | 0.7233 … 12.54 |  |
| 16 | CF Rad Ratio |  | numeric | 88 | 88 | 0.3856 … 1.395 |  |
| 17 | 2.5mm CF |  | numeric | 65 | 65 | 36.01 … 7196 |  |
| 18 | 2.5mm time |  | numeric | 96 | 96 | 0.4128 … 2.693 |  |
| 19 | Actual D |  | numeric | 96 | 40 | 2.129 … 2.937 |  |
| 20 | Completed Analysis? |  | text | 227 | 2 | Yes, No |  |

</details>

<details><summary>Hoja <b>Camera Settings</b> — encabezado fila 1, 227 filas no vacías × 26 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Flex Number |  | numeric | 227 | 227 | 1206 … 1431 | `1274A`×1 |
| 2 | llumination |  | numeric | 227 | 1 | 70 … 70 |  |
| 3 | HF Gain |  | numeric | 227 | 2 | 2.5e+04 … 3e+04 |  |
| 4 | CF Gain |  | numeric | 227 | 3 | 3e+04 … 7.8e+04 |  |
| 5 | HIBMS |  | text | 227 | 2 | yes, no |  |
| 6 | LLL |  | text | 227 | 2 | yes, no |  |
| 7 | HIBMS-2 |  | text | 227 | 2 | yes, no |  |
| 8 | IPSU-4 |  | text | 227 | 2 | yes, no |  |
| 9 | Downlink Video |  | text | 227 | 2 | yes, no |  |
| 10 | <col 10> |  | empty | 0 | 0 |  |  |
| 11 | <col 11> |  | empty | 0 | 0 |  |  |
| 12 | <col 12> |  | empty | 0 | 0 |  |  |
| 13 | <col 13> |  | empty | 0 | 0 |  |  |
| 14 | <col 14> |  | empty | 0 | 0 |  |  |
| 15 | <col 15> |  | empty | 0 | 0 |  |  |
| 16 | <col 16> |  | empty | 0 | 0 |  |  |
| 17 | <col 17> |  | empty | 0 | 0 |  |  |
| 18 | <col 18> |  | empty | 0 | 0 |  |  |
| 19 | <col 19> |  | empty | 0 | 0 |  |  |
| 20 | <col 20> |  | empty | 0 | 0 |  |  |
| 21 | <col 21> |  | empty | 0 | 0 |  |  |
| 22 | <col 22> |  | empty | 0 | 0 |  |  |
| 23 | <col 23> |  | empty | 0 | 0 |  |  |
| 24 | <col 24> |  | empty | 0 | 0 |  |  |
| 25 | <col 25> |  | empty | 0 | 0 |  |  |
| 26 | <col 26> |  | empty | 0 | 0 |  |  |

</details>

<details><summary>Hoja <b>Igniter</b> — encabezado fila 1, 227 filas no vacías × 26 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Flex Number |  | numeric | 227 | 227 | 1206 … 1431 | `1274A`×1 |
| 2 | Ignition Power ( W ) | W | text | 227 | 8 | 12 w, 13 w, 14 w |  |
| 3 | Ignition Time ( ms ) | ms | text | 227 | 17 | 3700 ms, 4000 ms, 4200 ms |  |
| 4 | <col 4> |  | empty | 0 | 0 |  |  |
| 5 | <col 5> |  | empty | 0 | 0 |  |  |
| 6 | <col 6> |  | empty | 0 | 0 |  |  |
| 7 | <col 7> |  | empty | 0 | 0 |  |  |
| 8 | <col 8> |  | empty | 0 | 0 |  |  |
| 9 | <col 9> |  | empty | 0 | 0 |  |  |
| 10 | <col 10> |  | empty | 0 | 0 |  |  |
| 11 | <col 11> |  | empty | 0 | 0 |  |  |
| 12 | <col 12> |  | empty | 0 | 0 |  |  |
| 13 | <col 13> |  | empty | 0 | 0 |  |  |
| 14 | <col 14> |  | empty | 0 | 0 |  |  |
| 15 | <col 15> |  | empty | 0 | 0 |  |  |
| 16 | <col 16> |  | empty | 0 | 0 |  |  |
| 17 | <col 17> |  | empty | 0 | 0 |  |  |
| 18 | <col 18> |  | empty | 0 | 0 |  |  |
| 19 | <col 19> |  | empty | 0 | 0 |  |  |
| 20 | <col 20> |  | empty | 0 | 0 |  |  |
| 21 | <col 21> |  | empty | 0 | 0 |  |  |
| 22 | <col 22> |  | empty | 0 | 0 |  |  |
| 23 | <col 23> |  | empty | 0 | 0 |  |  |
| 24 | <col 24> |  | empty | 0 | 0 |  |  |
| 25 | <col 25> |  | empty | 0 | 0 |  |  |
| 26 | <col 26> |  | empty | 0 | 0 |  |  |

</details>

<details><summary>Hoja <b>Comments</b> — encabezado fila 1, 227 filas no vacías × 26 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Flex Number |  | numeric | 227 | 227 | 1206 … 1431 | `1274A`×1 |
| 2 | Comments |  | text | 227 | 227 | Excellent deployment. Ignition just bef…, Good deployment on fiber. Only a little…, IPSUG did not switch to continuous mode… |  |
| 3 | <col 3> |  | empty | 0 | 0 |  |  |
| 4 | <col 4> |  | empty | 0 | 0 |  |  |
| 5 | <col 5> |  | empty | 0 | 0 |  |  |
| 6 | <col 6> |  | empty | 0 | 0 |  |  |
| 7 | <col 7> |  | empty | 0 | 0 |  |  |
| 8 | <col 8> |  | empty | 0 | 0 |  |  |
| 9 | <col 9> |  | empty | 0 | 0 |  |  |
| 10 | <col 10> |  | empty | 0 | 0 |  |  |
| 11 | <col 11> |  | empty | 0 | 0 |  |  |
| 12 | <col 12> |  | empty | 0 | 0 |  |  |
| 13 | <col 13> |  | empty | 0 | 0 |  |  |
| 14 | <col 14> |  | empty | 0 | 0 |  |  |
| 15 | <col 15> |  | empty | 0 | 0 |  |  |
| 16 | <col 16> |  | empty | 0 | 0 |  |  |
| 17 | <col 17> |  | empty | 0 | 0 |  |  |
| 18 | <col 18> |  | empty | 0 | 0 |  |  |
| 19 | <col 19> |  | empty | 0 | 0 |  |  |
| 20 | <col 20> |  | empty | 0 | 0 |  |  |
| 21 | <col 21> |  | empty | 0 | 0 |  |  |
| 22 | <col 22> |  | empty | 0 | 0 |  |  |
| 23 | <col 23> |  | empty | 0 | 0 |  |  |
| 24 | <col 24> |  | empty | 0 | 0 |  |  |
| 25 | <col 25> |  | empty | 0 | 0 |  |  |
| 26 | <col 26> |  | empty | 0 | 0 |  |  |

</details>

<details><summary>Hoja <b>Graphs</b> — encabezado fila —, 0 filas no vacías × 0 columnas</summary>

_vacía_

</details>

### Publicaciones con DOI (primeras 8)

- Can cool flames support quasi-steady alkane droplet burning? — doi:10.1016/j.combustflame.2012.07.012
- Cool-flame extinction during n-alkane droplet combustion in microgravity — doi:10.1016/j.combustflame.2015.01.012
- Partial-Burning Regime for Quasi-Steady Droplet Combustion Supported by Cool Flames — doi:10.2514/1.j054437
- The role of cool-flame chemistry in quasi-steady combustion and extinction of n-heptane droplets — doi:10.1080/13647830.2014.934296
- Asymptotic analysis of quasi-steady n-heptane droplet combustion supported by cool-flame chemistry — doi:10.1080/13647830.2016.1248494
- Low Temperature n-Dodecane Droplet Combustion Experiments Aboard the International Space Station — doi:10.1007/s12217-024-10115-x

<!-- AUTO:END -->

## Evaluación (manual — DE/PHY)

> Primera pasada DE-04 (2026-11-14) basada en el bloque automático y en las muestras L2. La clasificación
> Medida / Calculada / Log es **propuesta DE — pendiente de validación PHY (PHY-02)**.

### Resumen propio
CFI: llamas frías de gotas de n-dodecano y mezclas con iso-dodecano en el MDCA, con dilución por He y presión de 0.5–5 atm.
**Hallazgo DE-04:** la hoja de cálculo `CFI_DataSummary` trae **resultados procesados y medidos**, no solo condiciones.

### Granularidad y variables clave
| Archivo | Fila = … | Condición | Resultado (medido) | Calculadas | Notas |
|---|---|---|---|---|---|
| ET CFI (87) | 1 prueba | presión (texto "1 atm"), XO₂, XN₂, XHe, fibra, combustible | — | — | subconjunto de la `Master Sheet` |
| DataSummary `Master Sheet` (227) | 1 prueba | mismas condiciones para **todas** las pruebas | — | — | une con DATA por `Flex Number` |
| DataSummary `DATA` (227; 146 con análisis completo) | 1 prueba | D₀ | **Dext caliente y frío**, **k caliente y frío (mm²/s)**, reigniciones, tiempo de llama caliente, radiancias pico | cocientes de radiancia | `1274A` como ID; `NaN` literal |

### Problemas de calidad / acceso
- La presión viene como texto con unidad ("1 atm") en el ET y como numérica (atm) en DATA.
- 146 pruebas tienen análisis completo; las otras 81 no tienen resultados.
- Hay 2,698 archivos en `removed` y un `.metadata` muestreado devolvió 404 según la referencia. No afecta a la hoja de resumen.

### Valor para el proyecto
- **Pilar:** prevención (llamas frías: peligro poco visible) y supresión (efecto del He).
- **RQ:** RQ2 (diluyente He y presión → k y Dext) y RQ1 (llamas frías); M2.
- **Triage (borrador):** R1 2 · R2 3 · R3 3 · R4 3 · R5 3 · R6 3 → **Tier 1** (sube desde "Future" en la referencia).
