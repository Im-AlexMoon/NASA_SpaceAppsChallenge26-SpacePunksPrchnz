# PSI-25 — BASS-II · Burning and Suppression of Solids - II

<!-- AUTO:BEGIN — generado por `flamesafe profile`; no editar a mano dentro de este bloque -->

| Campo | Valor (PSI) |
|---|---|
| DOI de datos | 10.60555/4qc4-de67 |
| Tipo | Microgravity Investigation |
| Sub-área | Spacecraft Fire Safety |
| Programa / plataforma | International Space Station (ISS) / International Space Station (ISS) |
| Hardware | Microgravity Science Glovebox (MSG) |
| Centro | Glenn Research Center (GRC) |
| Periodo | 2010-01-01 → 2022-12-31 |
| Licencia | Creative Commons Zero v1.0 Universal |
| Investigaciones relacionadas | PSI-26 |
| Snapshot | snapshot_2026-11-14 |

### Inventario (L1)

| Archivos `added` | Tablas exp. (fuera de `added`) | `removed` | Publicaciones (con DOI) | GB expuestos | GB registrados | Acceso |
|---:|---:|---:|---:|---:|---:|---|
| 694 | 1 (1) | 131 | 17 (9) | 274.63 | 274.63 | `available` |

Categorías: Raw Data 685.0 (274.58 GB) · Science Documents 3.0 (0.00 GB) · Engineering Documents 2.0 (0.00 GB) · Reference Data 1.0 (0.00 GB) · Reports 1.0 (0.05 GB) · Representative Image(s) 1.0 (0.00 GB) · metadata 1.0 (0.00 GB)
Extensiones: `.mp4` 296 · `.zip` 265 · `.pdf` 127 · `.xlsx` 2 · `.docx` 2 · `.pptx` 1 · `.jpg` 1

**Objetivo (texto PSI):**

> BASS-II results contribute to the combustion computational models used in the design of fire detection and suppression systems in microgravity and on Earth. Objectives Include:   1) Study the ignition, flame growth, flame spread, and extinction limits for solid fuels burning in low-velocity forced flows in microgravity.   2) Begin to bridge the gap between the normal gravity NASA-STD-6001 Test #1 method, ground-based microgravity tests, and actual material flammability in microgravity.   3) Provide SoFIE PIs with preliminary data to refine Science Requirements.   4)  Practical, realistic (thicker) fuels in typical geometries will be examined, including slabs, cylinders, and spherical …

**Hipótesis (texto PSI):**

> BASS–II tests the hypothesis that materials in microgravity, with adequate ventilation, burn as well if not better than the same material in normal gravity with other conditions being identical (pressure, O2 concentration, temperature, etc.). NASA tests and controls materials from a flammability perspective using an upward burning test in normal gravity, which is considered to be the worst-case geometry for flammability of the material on Earth. However, it may not be conservative for flammability in space. Testing at constant O2 mole fractions permits studying flame spread and extinction at low and high flow speed. We are interested in finding the fundamental limit for a given material.

### Archivos perfilados (L2)

#### `PSI-25_Experimental table_BASS-II.csv`

- Lista: `experimentalTable` · 16,590 bytes · sha256 `71e792bf6b5fb5ea…` · HTTP 200
- CSV · encoding `utf-8-bom` · delimitador `,` · encabezado en fila 1 · filas no vacías **129** / físicas 129 · **17** columnas · bloques lado a lado: 1

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | PI |  | text | 129 | 6 | Bhattacharjee, Ferkul, Miller |  |
| 2 | Test # |  | text | 129 | 129 | B1, B2, B3 |  |
| 3 | Date |  | text | 129 | 30 | 2/19/2014, 7/7/2014, 7/2/2014 |  |
| 4 | GMT |  | numeric | 129 | 29 | 45 … 216 |  |
| 5 | Sample # |  | text | 129 | 107 | 147, 155, 148 |  |
| 6 | Fuel Sample Material |  | text | 129 | 51 | 100 micron PMMA film   2 cm wide, 200 micron PMMA film   2 cm wide, 100 micron film   2 cm wide |  |
| 7 | Flow restrictor |  | numeric | 129 | 3 | 0 … 2 |  |
| 8 | Fan display |  | text | 116 | 99 | 62, 47, 61 |  |
| 9 | Air display |  | text | 125 | 90 | 5, 2, 3   5   approaching 10 |  |
| 10 | Radiometer gain   (1000   250   50   10) | 1000   250   50   10 | mixed | 129 | 14 | 10 … 1000 | `250>50`×6, `250>50>250`×2, `50>250`×2, `250  50  250`×2, `250   50`×2, `50   250`×1 |
| 11 | Total Frames Shot |  | numeric | 129 | 110 | 2 … 316 | `video`×3, `none`×1, `300+   +102`×1, `10 postburn only`×1 |
| 12 | Calibrated  initial O2 % by vol |  | numeric | 129 | 50 | 13.6 … 22.2 |  |
| 13 | Calibrated final O2 % by vol |  | numeric | 129 | 66 | 0.6 … 40.4 | `none`×2 |
| 14 | Initial CO2 % by vol |  | numeric | 129 | 53 | 0 … 1.85 | `none`×2 |
| 15 | Final CO2 % by vol |  | numeric | 128 | 81 | 0.2 … 3.22 | `none`×5 |
| 16 | Initial CO (ppm) | ppm | numeric | 129 | 67 | -3 … 950 | `none`×2, `OR`×1 |
| 17 | Final CO (ppm) | ppm | numeric | 128 | 100 | 0.3 … 950 | `none`×4, `OR`×2, `>500`×1, `over`×1 |

#### `PSI-25_Reference Data_Fan calibration data.xlsx`

- Lista: `added` · 23,973 bytes · sha256 `bc0dca3efdef44a7…` · HTTP 200
- XLSX · **1** hojas

<details><summary>Hoja <b>Fan Calibration data</b> — encabezado fila 4, 30 filas no vacías × 109 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | GMT |  | mixed | 23 | 10 | 0 … 10 | `Pot`×1, `*U =1.0066(AIR)`×1, `Based on SPICE fan calibration data at …`×1 |
| 2 | 2014-043 |  | numeric | 21 | 9 | 38 … 122 | `Fan Display`×1 |
| 3 | <col 3> |  | mixed | 24 | 18 | 0 … 29 | `decr`×2, `Air`×2, `decr pot`×1, `Air Display`×1 |
| 4 | no restrictor |  | mixed | 25 | 11 | 3.8 … 12.2 | `Fan V`×3, `1 restrictor`×1, `2 resrictor`×1 |
| 5 | <col 5> |  | numeric | 20 | 16 | 0 … 29.19 | `test section`×1, `U cm/s*`×1 |
| 6 | <col 6> |  | empty | 0 | 0 |  |  |
| 7 | GMT |  | numeric | 19 | 7 | 0 … 10 | `Pot`×1 |
| 8 | 2014-45 |  | numeric | 19 | 8 | 38 … 122 | `Fan Display`×1 |
| 9 | <col 9> |  | mixed | 12 | 10 | 0 … 22 | `decr`×2, `Air`×2, `decr pot`×1, `Air Display`×1 |
| 10 | <col 10> |  | empty | 0 | 0 |  |  |
| 11 | GMT |  | numeric | 19 | 7 | 0 … 10 | `Pot`×1 |
| 12 | 2014-49 - post soot cleaning |  | numeric | 19 | 8 | 38 … 122 | `Fan Display`×1 |
| 13 | <col 13> |  | mixed | 24 | 17 | 0 … 59 | `decr`×2, `Air`×2, `decr pot`×1, `Air Display`×1 |
| 14 | <col 14> |  | empty | 0 | 0 |  |  |
| 15 | GMT |  | numeric | 21 | 8 | 0 … 10 | `Pot`×1 |
| 16 | 2014-50- post soot cleaning |  | numeric | 21 | 9 | 38 … 122 | `Fan Display`×1 |
| 17 | <col 17> |  | mixed | 26 | 21 | 0 … 59 | `decr`×2, `Air`×2, `decr pot`×1, `Air Display`×1 |
| 18 | <col 18> |  | empty | 0 | 0 |  |  |
| 19 | GMT |  | numeric | 21 | 8 | 0 … 10 | `Pot`×1 |
| 20 | 2014-091 - door repair |  | numeric | 21 | 9 | 38 … 122 | `Fan Display`×1 |
| 21 | <col 21> |  | mixed | 20 | 17 | 0 … 54 | `decr`×2, `Air`×2, `decr pot`×1, `Air Display`×1 |
| 22 | <col 22> |  | empty | 0 | 0 |  |  |
| 23 | GMT |  | numeric | 21 | 8 | 0 … 10 | `Pot`×1 |
| 24 | 2014-100 |  | numeric | 21 | 9 | 38 … 122 | `Fan Display`×1 |
| 25 | <col 25> |  | mixed | 19 | 16 | 0 … 55 | `decr`×2, `Air`×2, `decr pot`×1, `Air Display`×1 |
| 26 | <col 26> |  | empty | 0 | 0 |  |  |
| 27 | GMT |  | numeric | 22 | 9 | 0 … 10 | `Pot`×1 |
| 28 | 2014-174 |  | numeric | 22 | 10 | 38 … 122 | `Fan Display`×1 |
| 29 | <col 29> |  | mixed | 20 | 16 | 0 … 55 | `decr`×2, `Air`×2, `decr pot`×1, `Air Display`×1 |
| 30 | <col 30> |  | empty | 0 | 0 |  |  |
| 31 | GMT |  | numeric | 22 | 9 | 0 … 10 | `Pot`×1 |
| 32 | 2014-175 |  | numeric | 22 | 10 | 38 … 122 | `Fan Display`×1 |
| 33 | <col 33> |  | mixed | 15 | 12 | 0 … 38 | `decr`×2, `Air`×2, `decr pot`×1, `Air Display`×1 |
| 34 | <col 34> |  | empty | 0 | 0 |  |  |
| 35 | GMT |  | numeric | 22 | 9 | 0 … 10 | `Pot`×1 |
| 36 | 2014-177 |  | numeric | 22 | 10 | 38 … 122 | `Fan Display`×1 |
| 37 | <col 37> |  | mixed | 13 | 10 | 0 … 37 | `decr`×2, `Air`×2, `decr pot`×1, `Air Display`×1 |
| 38 | <col 38> |  | empty | 0 | 0 |  |  |
| 39 | GMT |  | numeric | 22 | 9 | 0 … 10 | `Pot`×1 |
| 40 | 2014-178 |  | numeric | 22 | 10 | 38 … 122 | `Fan Display`×1 |
| … | _69 columnas más_ | | | | | | |

</details>

#### `PSI-25_Science Documents_BASS-II_Test.Matrices.xlsx`

- Lista: `added` · 28,956 bytes · sha256 `1a3b283dd0adec86…` · HTTP 200
- XLSX · **6** hojas

<details><summary>Hoja <b>Bhattacharjee</b> — encabezado fila 1, 22 filas no vacías × 16 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Actual Date  (for Video Display Date, add 1 for Leap Year) |  | datetime | 22 | 4 | 2014-02-19T00:00:00, 2014-07-07T00:00:00, 2014-07-02T00:00:00 |  |
| 2 | GMT 2014- |  | numeric | 22 | 4 | 50 … 216 |  |
| 3 | Test no. |  | text | 22 | 22 | B1, B2, B3 |  |
| 4 | Sample no. |  | text | 22 | 20 | 147, 155, 148 |  |
| 5 | Material |  | text | 22 | 14 | 100 micron pmma film, 2 cm wide, 200 micron pmma film, 2 cm wide, 100 micron film, 2 cm wide |  |
| 6 | Flow restrictor |  | numeric | 22 | 3 | 0 … 2 |  |
| 7 | Fan display |  | text | 22 | 20 | 62, 47, 61 |  |
| 8 | Air display |  | text | 22 | 15 | 5, 2, 3, 5, approaching 10 |  |
| 9 | Radiometer gain   (1000, 250, 50, 10) | 1000, 250, 50, 10 | numeric | 22 | 3 | 10 … 250 |  |
| 10 | total frames shot |  | numeric | 22 | 22 | 44 … 311 | `none`×1 |
| 11 | calibrated  initial O2 % by vol |  | numeric | 22 | 8 | 15 … 22.2 |  |
| 12 | calibrated final O2 % by vol |  | numeric | 22 | 13 | 1.6 … 22.2 | `none`×1 |
| 13 | Initial CO2 % by vol |  | numeric | 22 | 12 | 0 … 0.51 |  |
| 14 | Final CO2 % by vol |  | numeric | 21 | 14 | 0.34 … 0.65 | `none`×1 |
| 15 | Initial CO (ppm) | ppm | numeric | 22 | 11 | -1 … 119 |  |
| 16 | Final CO (ppm) | ppm | numeric | 21 | 18 | 0.3 … 131 | `none`×1 |

</details>

<details><summary>Hoja <b>Ferkul</b> — encabezado fila 1, 4 filas no vacías × 16 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Actual Date  (for Video Display Date, add 1 for Leap Year) |  | datetime | 4 | 4 | 2014-02-19T00:00:00, 2014-07-28T00:00:00, 2014-08-01T00:00:00 |  |
| 2 | GMT 2014- |  | numeric | 4 | 4 | 50 … 213 |  |
| 3 | Test no. |  | text | 4 | 4 | F1, F2, F3 |  |
| 4 | Sample no. |  | text | 4 | 4 | 227, 228m, 229m |  |
| 5 | Material |  | text | 4 | 2 | Nomex natural (nomex III), Japan Wax candle |  |
| 6 | Flow restrictor |  | numeric | 4 | 2 | 1 … 2 |  |
| 7 | Fan display |  | mixed | 4 | 4 | 61 … 92 | `see notes`×1 |
| 8 | Air display |  | mixed | 4 | 4 | 8 … 15 | `3 ign`×1 |
| 9 | Radiometer gain   (1000, 250, 50, 10) | 1000, 250, 50, 10 | numeric | 4 | 2 | 50 … 250 |  |
| 10 | total frames shot |  | numeric | 4 | 4 | 46 … 270 |  |
| 11 | calibrated  initial O2 % by vol |  | numeric | 4 | 4 | 17.4 … 22.2 |  |
| 12 | calibrated final O2 % by vol |  | mixed | 4 | 4 | 17.4 … 22.2 | `none`×1 |
| 13 | Initial CO2 % by vol |  | numeric | 4 | 4 | 0.36 … 0.46 |  |
| 14 | Final CO2 % by vol |  | mixed | 4 | 4 | 0.39 … 0.48 | `none`×1 |
| 15 | Initial CO (ppm) | ppm | numeric | 4 | 4 | 0 … 105 |  |
| 16 | Final CO (ppm) | ppm | mixed | 4 | 4 | 2 … 82 | `none`×1 |

</details>

<details><summary>Hoja <b>Miller</b> — encabezado fila 1, 20 filas no vacías × 16 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Actual Date  (for Video Display Date, add 1 for Leap Year) |  | datetime | 20 | 7 | 2014-02-20T00:00:00, 2014-07-11T00:00:00, 2014-07-31T00:00:00 |  |
| 2 | GMT 2014- |  | numeric | 20 | 7 | 51 … 213 |  |
| 3 | Test no. |  | text | 20 | 20 | M1, M2, M3 |  |
| 4 | Sample no. |  | text | 20 | 20 | 222, 224, 226m |  |
| 5 | Material |  | text | 20 | 18 | 1 mm thick pmma, 1 sided, 2 cm, 3 mm thick pmma 1 sided , 2 cm wide, 2 cm wide, 5 mm thick 1 sided pmma |  |
| 6 | Flow restrictor |  | numeric | 20 | 3 | 0 … 2 |  |
| 7 | Fan display |  | text | 19 | 18 | 58, 54, 116 (pot 9.3),  89, 80, 84, 3.0,3.1,3.2,6.4,5.5,5.4 |  |
| 8 | Air display |  | text | 20 | 19 | 10,8, 20,15,13, 14, 10, 20,18 |  |
| 9 | Radiometer gain   (1000, 250, 50, 10) | 1000, 250, 50, 10 | text | 20 | 9 | 50, 250>50>250, 250>50 |  |
| 10 | total frames shot |  | numeric | 20 | 19 | 153 … 309 | `300+   +102`×1 |
| 11 | calibrated  initial O2 % by vol |  | numeric | 20 | 14 | 17.9 … 22.2 |  |
| 12 | calibrated final O2 % by vol |  | numeric | 20 | 18 | 16.8 … 21.9 |  |
| 13 | Initial CO2 % by vol |  | numeric | 20 | 15 | 0.26 … 1.42 |  |
| 14 | Final CO2 % by vol |  | numeric | 20 | 19 | 0.54 … 3.22 |  |
| 15 | Initial CO (ppm) | ppm | numeric | 20 | 14 | -1 … 398 |  |
| 16 | Final CO (ppm) | ppm | numeric | 20 | 20 | 60 … 612 | `>500`×1 |

</details>

<details><summary>Hoja <b>Olson</b> — encabezado fila 1, 27 filas no vacías × 16 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Actual Date  (for Video Display Date, add 1 for Leap Year) |  | datetime | 27 | 10 | 2014-02-18T00:00:00, 2014-06-13T00:00:00, 2014-07-08T00:00:00 |  |
| 2 | GMT 2014- (except last 3 tests from 2016) | except last 3 tests from 2016 | numeric | 27 | 10 | 49 … 213 |  |
| 3 | Test no. |  | text | 27 | 27 | O1, O2, O3a |  |
| 4 | Sample no. |  | text | 27 | 20 | 207, 204, 205M |  |
| 5 | Material |  | text | 27 | 6 | 1/4" clear rod, 3/8"clear rod, 1/2" clear pmma rod |  |
| 6 | Flow restrictor |  | numeric | 27 | 3 | 0 … 2 |  |
| 7 | Fan display |  | text | 25 | 24 | 89,62,50,41, .54 pot, 0.45 pot, 5, 0.7, 0.5, 0.4, 0.36 ext |  |
| 8 | Air display |  | text | 23 | 22 | 20,10,5,2,1, 0, 5,3 |  |
| 9 | Radiometer gain   (1000, 250, 50, 10) | 1000, 250, 50, 10 | numeric | 27 | 4 | 50 … 1000 | `1000, 250`×1 |
| 10 | total frames shot |  | mixed | 27 | 25 | 2 … 316 | `video`×3, `10 postburn only`×1 |
| 11 | calibrated  initial O2 % by vol |  | numeric | 27 | 20 | 13.6 … 22.2 |  |
| 12 | calibrated final O2 % by vol |  | numeric | 27 | 23 | 13.5 … 21.9 |  |
| 13 | Initial CO2 % by vol |  | numeric | 27 | 23 | 0.2 … 1.85 |  |
| 14 | Final CO2 % by vol |  | numeric | 27 | 27 | 0.28 … 2.1 |  |
| 15 | Initial CO (ppm) | ppm | numeric | 27 | 24 | -3 … 950 | `OR`×1 |
| 16 | Final CO (ppm) | ppm | mixed | 27 | 26 | 22 … 950 | `OR`×2, `over`×1 |

</details>

<details><summary>Hoja <b>Fernandez-Pello</b> — encabezado fila 1, 27 filas no vacías × 16 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Actual Date  (for Video Display Date, add 1 for Leap Year) |  | datetime | 27 | 8 | 2014-06-16T00:00:00, 2014-07-03T00:00:00, 2014-07-14T00:00:00 |  |
| 2 | GMT 2014- |  | numeric | 27 | 8 | 167 … 211 |  |
| 3 | Test no. |  | text | 27 | 27 | P1, P2, P3a |  |
| 4 | Sample no. |  | text | 27 | 21 | 185M, 188M, 215M |  |
| 5 | Material |  | text | 27 | 9 | 1/4" black rod, 1/4" clear rod, 1/4 clear rod |  |
| 6 | Flow restrictor |  | numeric | 27 | 1 | 2 … 2 |  |
| 7 | Fan display |  | text | 23 | 15 | 48, 41, Fan pot 1.5 (5cm/s), 0.9, 0.4, 0.36, 0.…, 48, 62, 75 |  |
| 8 | Air display |  | text | 27 | 18 | 5,2, slow decr to ext, 5, 2.5, 2 (pot .9, .5, .35.,.33), 5, 2.5 (1.15, .5, .35, .33. .32, .315, … |  |
| 9 | Radiometer gain   (1000, 250, 50, 10) | 1000, 250, 50, 10 | mixed | 27 | 5 | 50 … 250 | `250>50`×3, `250, 50`×2, `250,50`×1 |
| 10 | total frames shot |  | numeric | 27 | 25 | 14 … 313 |  |
| 11 | calibrated  initial O2 % by vol |  | numeric | 27 | 20 | 16.3 … 20.9 |  |
| 12 | calibrated final O2 % by vol |  | numeric | 27 | 19 | 0.6 … 39.1 |  |
| 13 | Initial CO2 % by vol |  | numeric | 27 | 20 | 0.27 … 1.67 | `none`×1 |
| 14 | Final CO2 % by vol |  | numeric | 27 | 23 | 0.44 … 2.24 | `none`×2 |
| 15 | Initial CO (ppm) | ppm | numeric | 27 | 21 | 0 … 525 | `none`×1 |
| 16 | Final CO (ppm) | ppm | numeric | 27 | 25 | 14 … 535 | `none`×1 |

</details>

<details><summary>Hoja <b>T'ien</b> — encabezado fila 1, 29 filas no vacías × 16 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Actual Date  (for Video Display Date, add 1 for Leap Year) |  | datetime | 29 | 7 | 2014-02-14T00:00:00, 2014-06-27T00:00:00, 2014-04-10T00:00:00 |  |
| 2 | GMT 2014- |  | numeric | 29 | 6 | 45 … 216 |  |
| 3 | Test no. |  | text | 29 | 29 | T1, T2, T3 |  |
| 4 | Sample no. |  | text | 29 | 23 | 128, 129, 182m |  |
| 5 | Material |  | text | 29 | 6 | SIBAL 2 cm, 4 cm spherical section, 2 cm SIBAL |  |
| 6 | Flow restrictor |  | numeric | 29 | 3 | 0 … 2 |  |
| 7 | Fan display |  | text | 23 | 19 | 80, 80, 59, 55, 63 |  |
| 8 | Air display |  | text | 29 | 19 | 10, 9, 5, 4, 9,1 |  |
| 9 | Radiometer gain   (1000, 250, 50, 10) | 1000, 250, 50, 10 | numeric | 29 | 2 | 50 … 250 |  |
| 10 | total frames shot |  | numeric | 29 | 26 | 19 … 299 |  |
| 11 | calibrated  initial O2 % by vol |  | numeric | 29 | 15 | 16.4 … 20.8 |  |
| 12 | calibrated final O2 % by vol |  | numeric | 29 | 21 | 0.9 … 40.4 |  |
| 13 | Initial CO2 % by vol |  | numeric | 29 | 19 | 0.19 … 0.72 | `none`×1 |
| 14 | Final CO2 % by vol |  | numeric | 29 | 22 | 0.2 … 0.75 | `none`×1 |
| 15 | Initial CO (ppm) | ppm | numeric | 29 | 20 | -1 … 152 | `none`×1 |
| 16 | Final CO (ppm) | ppm | numeric | 29 | 26 | 2 … 190 | `none`×1 |

</details>

### Publicaciones con DOI (primeras 8)

- Microgravity flammability boundary for PMMA rods in axial stagnation flow: Experimental results and energy balance analyses — doi:10.1016/j.combustflame.2017.03.001
- Temperature and CO2 fields of a downward spreading flame over thin cellulose: A comparison of experimental and computational results — doi:10.1016/j.proci.2014.05.093
- Opposed-flow flame spread: A comparison of microgravity and normal gravity experiments to establish the thermal regime — doi:10.1016/j.firesaf.2015.11.011
- The critical flow velocity for radiative extinction in opposed-flow flame spread in a microgravity environment: A comparison of experimental, computational, and theoretical results — doi:10.1016/j.combustflame.2015.10.023
- Experimental validation of a correlation capturing the boundary layer effect on spread rate in the kinetic regime of opposed-flow flame spread — doi:10.1016/j.proci.2014.06.125
- Radiative, thermal, and kinetic regimes of opposed-flow flame spread: A comparison between experiment and theory — doi:10.1016/j.proci.2016.06.025
- Concurrent flame growth, spread, and quenching over composite fabric samples in low speed purely forced flow in microgravity — doi:10.1016/j.proci.2016.06.028
- A Study of the Effectiveness of a Narrow Channel Apparatus in Simulating Microgravity Flame Spread over Thin Fuels — doi:10.2514/6.2012-3493

<!-- AUTO:END -->

## Evaluación (manual — DE/PHY)

> Primera pasada DE-04 (2026-11-14) basada en el bloque automático y en las muestras L2. La clasificación
> Medida / Calculada / Log es **propuesta DE — pendiente de validación PHY (PHY-02)**.

### Resumen propio
BASS-II: inflamabilidad de sólidos (PMMA, Nomex, SIBAL, velas, barras) en el MSG con flujo forzado por ventilador y O₂
reducido. Hay 6 PIs con matrices de prueba separadas.

### Granularidad y variables clave
| Archivo | Fila = … | Condición | Resultado (medido) | Calculadas | Notas |
|---|---|---|---|---|---|
| ET BASS-II (129) | 1 prueba | PI, material (texto libre, 51 valores), restrictor de flujo, display de ventilador/aire, O₂ % vol inicial calibrado | O₂ final, CO₂ y CO inicial/final (producto de combustión), frames | — | `OR`, `>500`, `over`, `none` en CO |
| Test.Matrices.xlsx (6 hojas) | 1 prueba por PI | las mismas | las mismas | — | otra vista de la misma campaña: elegir una canónica |
| Fan calibration (30×109) | punto de calibración | display del ventilador | velocidad de flujo | — | permite convertir el display del ventilador a cm/s ⚠️ |

### Problemas de calidad / acceso
- **No hay tabla de propagación de llama.** Las tasas están en video (296 MP4), fuera del alcance.
- `Air display` es una lectura lenta del ducto (no es la velocidad instantánea). El material va en texto libre con espesor y ancho embebidos.

### Valor para el proyecto
- **Pilar:** prevención (O₂ límite vs. flujo en sólidos). **Entornos:** naves y hábitats con ventilación.
- **RQ:** RQ3 (cualitativo/semicuantitativo). Con la calibración del ventilador se puede obtener flujo en cm/s.
- **Triage (borrador):** R1 3 · R2 3 · R3 2 · R4 2 · R5 2 · R6 2 → **Tier 2**.
