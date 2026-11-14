# PSI-26 — BASS · Burning and Suppression of Solids

<!-- AUTO:BEGIN — generado por `flamesafe profile`; no editar a mano dentro de este bloque -->

| Campo | Valor (PSI) |
|---|---|
| DOI de datos | 10.60555/58h4-dy80 |
| Tipo | Microgravity Investigation |
| Sub-área | Spacecraft Fire Safety |
| Programa / plataforma | International Space Station (ISS) / International Space Station (ISS) |
| Hardware | Microgravity Science Glovebox |
| Centro | Glenn Research Center (GRC) |
| Periodo | 2009-10-01 → 2013-06-30 |
| Licencia | Creative Commons Zero v1.0 Universal |
| Investigaciones relacionadas | PSI-25, PSI-107 |
| Snapshot | snapshot_2026-11-14 |

### Inventario (L1)

| Archivos `added` | Tablas exp. (fuera de `added`) | `removed` | Publicaciones (con DOI) | GB expuestos | GB registrados | Acceso |
|---:|---:|---:|---:|---:|---:|---|
| 211 | 1 (1) | 24 | 10 (7) | 163.55 | 163.55 | `available` |

Categorías: Raw Data 173.0 (163.51 GB) · Engineering Documents 24.0 (0.01 GB) · Presentations 6.0 (0.01 GB) · Science Documents 5.0 (0.01 GB) · Reports 2.0 (0.00 GB) · metadata 1.0 (0.00 GB)
Extensiones: `.mp4` 114 · `.zip` 60 · `.pdf` 32 · `.xlsx` 2 · `.pptx` 2 · `.docx` 1

**Objetivo (texto PSI):**

> The two main objectives for BASS are to:     1.) Begin to bridge the gap between the normal gravity NASA-STD-6001 Test#1 method, ground-based microgravity tests, and actual material flammability in microgravity. The relation between these can be investigated by observing flames burning for the longer times available in flight. Practical, realistic (thicker) fuels in typical geometries will be examined, including wake flames which have characteristics of a fire burning behind another object (for example, a fire burning in tight area which may not be easily accessible).     2.) Assess the effectiveness of an inert, gaseous extinguishing agent (similar to that used on ISS) in putting out …

**Hipótesis (texto PSI):**

> BASS experiments were based on the hypothesis that materials in microgravity, with adequate ventilation, burn as well if not better than the same material in normal gravity with other conditions being identical (pressure, oxygen concentration, temperature, etc.) To test this hypothesis with any but the thinnest materials requires extended microgravity time – longer than available in drop towers or parabolic aircraft.

### Archivos perfilados (L2)

#### `PSI-26_Experimental table_BASS.csv`

- Lista: `experimentalTable` · 4,726 bytes · sha256 `ccfc3c54d948b64a…` · HTTP 200
- CSV · encoding `utf-8-bom` · delimitador `,` · encabezado en fila 1 · filas no vacías **122** / físicas 122 · **6** columnas · bloques lado a lado: 1

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Date |  | text | 122 | 33 | 3/30/2012, 4/5/2012, 4/9/2012 |  |
| 2 | GMT |  | numeric | 122 | 31 | 90 … 234 |  |
| 3 | As Run Test # |  | numeric | 121 | 116 | 1 … 116 |  |
| 4 | Test # |  | mixed | 121 | 117 | 1 … 119 | `12-R`×1, `12-R2`×1, `5b`×1, `82a`×1, `82b`×1, `83a`×1 |
| 5 | Sample # |  | numeric | 121 | 40 | 2 … 44 |  |
| 6 | Fuel Sample Material |  | text | 122 | 34 | SIBAL 2 cm, PMMA sphere 2 cm, PMMA sphere 1 cm |  |

#### `PSI-26_Science Documents_As Run_Test Matrix.xlsx`

- Lista: `added` · 111,886 bytes · sha256 `850910541fc9c802…` · HTTP 200
- XLSX · **5** hojas

<details><summary>Hoja <b>as run matrix</b> — encabezado fila 3, 130 filas no vacías × 30 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Actual Date  (for SPICE Display Date, add 1 for Leap Year) |  | text | 125 | 35 | 2012-03-30T00:00:00, 2012-04-05T00:00:00, 2012-04-09T00:00:00 |  |
| 2 | Approx Start Time ( with GMT) | with GMT | text | 124 | 123 | 90 - 11:10, 90 - 12:02, 90 - 14:41 |  |
| 3 | As run test no. |  | numeric | 129 | 124 | 1 … 116 | `STOW`×1, `SETUP`×1, `Dilution test with CSA-CP`×1, `remember to turn off auto iso when don'…`×1, `still in this mode at end of ops on 234.`×1, `actual data for 234 is const iso at 1000`×1 |
| 4 | Test no. |  | mixed | 121 | 117 | 1 … 119 | `12-R`×1, `12-R2`×1, `5b`×1, `82a`×1, `82b`×1, `83a`×1 |
| 5 | Sample no. |  | numeric | 121 | 40 | 2 … 44 |  |
| 6 | material |  | text | 122 | 34 | SIBAL 2 cm, PMMA sphere 2 cm, PMMA sphere 1 cm |  |
| 7 | Igniter |  | text | 122 | 33 | pre-wired, 2-1, 2-6 |  |
| 8 | Flow restrictor |  | numeric | 121 | 2 | 0 … 2 |  |
| 9 | Sample distance |  | text | 101 | 29 | farthest downstream, 2, 4, 25 mm from downstream most position |  |
| 10 | Fan display |  | text | 120 | 97 | 66 > 52, 66 > 52 > 45, 66 > 47 |  |
| 11 | Air display |  | text | 109 | 71 | 10, 5, 10, 5, 3, 10, 3-4 |  |
| 12 | Radiometer gain ( 1000, 250, 50, 10) | 1000, 250, 50, 10 | numeric | 121 | 6 | 50 … 1000 | `250?`×2, `50?`×1, `250, 1000 (18:20:07)`×1 |
| 13 | Radiometer display |  | text | 27 | 25 | saturated, ~ 1.2 max, 2.37 max |  |
| 14 | GN2 Pot |  | mixed | 99 | 13 | 0 … 10 | `n/a`×7, `8, 10`×5, `8.0 > max`×2, `1 to max`×2, `1 to max increments`×2, `4.0 > 8.0 > max`×1 |
| 15 | GN2 display |  | text | 79 | 9 | n/a, 198 to 497, 398 check only |  |
| 16 | Filter y/n |  | text | 121 | 2 | N, Y |  |
| 17 | Release Mode (CH/CL) | CH/CL | text | 121 | 2 | CH, CL |  |
| 18 | Exposure Mode (M/A) | M/A | text | 120 | 3 | A, M, P |  |
| 19 | Exposure compensation   (-#EV) | -#EV | mixed | 121 | 14 | -5 … -2 | `shutter 1/2 s`×5, `1/30 s shutter`×3, `shutter 1/8 s`×2, `1/8 s shutter`×2, `1/4 s shutter`×2, `shutter 1/20 s`×1 |
| 20 | Bracket frames and exposure bracket (#F/ 1.0) | #F/ 1.0 | text | 107 | 13 | 9F  1.0, n/a, 9F 1.0 |  |
| 21 | shutter speed (1/s) | 1/s | mixed | 114 | 10 | 0.548 … 1 | `n/a`×8, `9f1.0`×6, `tbd best`×2, `best 1/25s 10 cm/s,    1/10s 5 cm/s`×1 |
| 22 | F stop |  | text | 121 | 4 | 2, 4, F2 |  |
| 23 | ISO |  | numeric | 121 | 4 | 800 … 1e+04 |  |
| 24 | shutter hold s /cont |  | text | 121 | 6 | 7, cont, CONT |  |
| 25 | SD card S/N |  | numeric | 121 | 8 | 2 … 9 |  |
| 26 | total frames shot |  | mixed | 114 | 103 | 0 … 328 | `100 flame`×2, `264 total`×2, `5 brackets`×1, `6 brackets`×1, `9 brackets`×1, `47 flame`×1 |
| 27 | O2 % by volume |  | numeric | 123 | 45 | 0.159 … 0.2272 |  |
| 28 | pressure, atm |  | numeric | 123 | 26 | 0.97 … 1.009 |  |
| 29 | CO2, mm Hg |  | numeric | 118 | 26 | 1.37 … 3.51 | `?`×5 |
| 30 | Test Observations and Anomalies (ignited, spread, extinguished, burn time, color, etc.) |  | text | 124 | 124 | Nice symmetric burn, some soot at 10 cm…, Don noted significant vapor jetting.   …, Very bright sooty ball.   Lots of vapor… |  |

</details>

<details><summary>Hoja <b>2012</b> — encabezado fila 3, 82 filas no vacías × 31 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Actual Date  (for SPICE Display Date, add 1 for Leap Year) |  | text | 82 | 22 | 2012-03-30T00:00:00, 2012-04-05T00:00:00, 2012-04-09T00:00:00 |  |
| 2 | Date on videos and images |  | text | 82 | 21 | 03/31/2012, 04/06/2012, 04/10/2012 |  |
| 3 | Approx Start Time ( with GMT) | with GMT | text | 81 | 81 | 90 - 11:10, 90 - 12:02, 90 - 14:41 |  |
| 4 | As run test no. |  | numeric | 81 | 80 | 1 … 79 | `STOW`×1 |
| 5 | Test no. |  | mixed | 80 | 80 | 1 … 118 | `12-R`×1, `12-R2`×1, `5b`×1, `82a`×1, `82b`×1, `83a`×1 |
| 6 | Sample no. |  | numeric | 80 | 33 | 2 … 41 |  |
| 7 | material |  | text | 81 | 22 | SIBAL 2 cm, PMMA sphere 2 cm, PMMA sphere 1 cm |  |
| 8 | Igniter |  | text | 80 | 18 | pre-wired, 2-1, 2-6 |  |
| 9 | Flow restrictor |  | numeric | 80 | 2 | 0 … 2 |  |
| 10 | Sample distance |  | text | 79 | 24 | farthest downstream, 2, 4, 25 mm from downstream most position |  |
| 11 | Fan display |  | text | 80 | 65 | 66 > 52, 66 > 52 > 45, 66 > 47 |  |
| 12 | Air display |  | text | 79 | 50 | 10, 5, 10, 5, 3, 10, 3-4 |  |
| 13 | Radiometer gain ( 1000, 250, 50, 10) | 1000, 250, 50, 10 | numeric | 80 | 4 | 50 … 1000 | `50?`×1 |
| 14 | Radiometer display |  | text | 14 | 13 | saturated, ~ 1.2 max, 2.37 max |  |
| 15 | GN2 Pot |  | mixed | 80 | 12 | 4 … 10 | `n/a`×4, `8, 10`×4, `8.0 > max`×2, `1 to max`×2, `1 to max increments`×2, `4.0 > 8.0 > max`×1 |
| 16 | GN2 display |  | text | 67 | 9 | n/a, 198 to 497, 398 check only |  |
| 17 | Filter y/n |  | text | 80 | 2 | N, Y |  |
| 18 | Release Mode (CH/CL) | CH/CL | text | 80 | 2 | CH, CL |  |
| 19 | Exposure Mode (M/A) | M/A | text | 80 | 3 | A, M, P |  |
| 20 | Exposure compensation   (-#EV) | -#EV | mixed | 80 | 14 | -5 … -2 | `shutter 1/2 s`×5, `1/30 s shutter`×3, `shutter 1/8 s`×2, `1/8 s shutter`×2, `1/4 s shutter`×2, `shutter 1/20 s`×1 |
| 21 | Bracket frames and exposure bracket (#F/ 1.0) | #F/ 1.0 | text | 81 | 5 | 9F  1.0, n/a, 9F 1.0 |  |
| 22 | shutter speed (1/s) | 1/s | mixed | 73 | 9 | 0.548 … 1 | `n/a`×8, `tbd best`×2, `best 1/25s 10 cm/s,    1/10s 5 cm/s`×1 |
| 23 | F stop |  | text | 80 | 4 | 2, 4, F2 |  |
| 24 | ISO |  | numeric | 80 | 4 | 800 … 1e+04 |  |
| 25 | shutter hold s /cont |  | text | 80 | 5 | 7, cont, CONT |  |
| 26 | SD card S/N |  | numeric | 79 | 8 | 2 … 9 |  |
| 27 | total frames shot |  | mixed | 74 | 70 | 0 … 321 | `100 flame`×2, `5 brackets`×1, `6 brackets`×1, `9 brackets`×1, `47 flame`×1, `65 flame`×1 |
| 28 | O2 % by volume |  | numeric | 80 | 22 | 0.2089 … 0.2272 |  |
| 29 | pressure, atm |  | numeric | 80 | 20 | 0.97 … 1.009 |  |
| 30 | CO2, mm Hg |  | numeric | 80 | 19 | 1.37 … 3.51 | `?`×5 |
| 31 | Test Observations and Anomalies (ignited, spread, extinguished, burn time, color, etc.) |  | text | 81 | 81 | Nice symmetric burn, some soot at 10 cm…, Don noted significant vapor jetting.   …, Very bright sooty ball.   Lots of vapor… |  |

</details>

<details><summary>Hoja <b>2013</b> — encabezado fila 2, 49 filas no vacías × 31 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Actual Date  (for SPICE Display Date, add 1 for Leap Year) |  | datetime | 43 | 13 | 2013-04-04T00:00:00, 2013-04-05T00:00:00, 2013-04-09T00:00:00 |  |
| 2 | Date on videos and images |  | datetime | 43 | 12 | 2013-04-05T00:00:00, 2013-04-06T00:00:00, 2013-04-10T00:00:00 |  |
| 3 | Approx Start Time ( with GMT) | with GMT | text | 43 | 42 | 13-94:  15:45, 13-95, 13-095:  14:20ish? |  |
| 4 | As run test no. |  | mixed | 48 | 44 | 80 … 116 | `SETUP`×1, `Dilution test with CSA-CP`×1, `remember to turn off auto iso when don'…`×1, `still in this mode at end of ops on 234.`×1, `actual data for 234 is const iso at 1000`×1, `down to 1/3 s`×1 |
| 5 | Test no. |  | numeric | 42 | 41 | 26 … 119 | `Setup`×1, `117a`×1, `53a`×1 |
| 6 | Sample no. |  | numeric | 41 | 13 | 17 … 44 |  |
| 7 | material |  | text | 41 | 16 | PMMA 2 cm, pmma 2 cm, candle,  paraffin, wake |  |
| 8 | Igniter |  | text | 42 | 15 | unknown, 15-11, 25-13 |  |
| 9 | Flow restrictor |  | numeric | 41 | 2 | 0 … 2 |  |
| 10 | Sample distance |  | text | 22 | 6 | n/a, 2, ? |  |
| 11 | Fan display |  | text | 41 | 35 | Expt settings, 68, 68, 51,  slowly to zero |  |
| 12 | Air display |  | text | 30 | 26 | 12, 7.5,  2, 7.5,  0 |  |
| 13 | Radiometer gain ( 1000, 250, 50, 10) | 1000, 250, 50, 10 | numeric | 41 | 4 | 50 … 250 | `250?`×2, `250, 1000 (18:20:07)`×1 |
| 14 | Radiometer display |  | mixed | 13 | 13 | 0.27 … 2.2 | `saturated`×1, `low`×1, `at 2 cm/s, incr;`×1, `<1`×1, `n/a`×1 |
| 15 | GN2 Pot |  | mixed | 19 | 5 | 0 … 10 | `n/a`×3, `8, 10`×1 |
| 16 | GN2 display |  | text | 12 | 1 | n/a |  |
| 17 | Filter y/n |  | text | 42 | 2 | Camera Settings, N |  |
| 18 | Release Mode (CH/CL) | CH/CL | text | 41 | 2 | CL, CH |  |
| 19 | Exposure Mode (M/A) | M/A | text | 40 | 1 | A |  |
| 20 | Exposure compensation   (-#EV) | -#EV | numeric | 41 | 2 | -5 … -4 |  |
| 21 | Bracket frames and exposure bracket (#F/ 1.0) | #F/ 1.0 | text | 26 | 9 | a number of random ones, n/a, 1 dark frame set |  |
| 22 | shutter speed (1/s) | 1/s | mixed | 41 | 2 | 1 … 1 | `9f1.0`×6 |
| 23 | F stop |  | text | 41 | 2 | F4, F2 |  |
| 24 | ISO |  | numeric | 41 | 2 | 1000 … 1600 |  |
| 25 | shutter hold s /cont |  | text | 41 | 4 | CONT, cont, 7 s |  |
| 26 | SD card S/N |  | numeric | 42 | 8 | 2 … 9 |  |
| 27 | total frames shot |  | mixed | 40 | 35 | 0 … 328 | `264 total`×2, `132 total`×1, `329 total (full)`×1, `163 total (incl 9 dark frames)`×1, `full, unknown number of frames`×1, `131 frames`×1 |
| 28 | O2 % by volume |  | numeric | 44 | 24 | 0.159 … 0.216 | `ISS environment`×1 |
| 29 | pressure, atm |  | numeric | 43 | 8 | 0.97 … 0.9963 |  |
| 30 | CO2, mm Hg |  | numeric | 38 | 8 | 1.9 … 3.4 |  |
| 31 | Test Observations and Anomalies (ignited, spread, extinguished, burn time, color, etc.) |  | text | 43 | 43 | Hardware install in the MSG.  Chris Cas…, initial reading 20.9% O2    fan on max …, 1st vititation test with CSA-CP.  N2 on… |  |

</details>

<details><summary>Hoja <b>Data without TP</b> — encabezado fila 1, 38 filas no vacías × 2 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Data Folder |  | numeric | 38 | 38 | 2.013e+07 … 2.014e+07 | `20130408(adj date)`×1, `20130415(adj date)`×1, `20130501(adj date)`×1 |
| 2 | Type of data |  | text | 38 | 8 | images dated 20130409, images dated 20130416, videos and images dated 20130502 |  |

</details>

<details><summary>Hoja <b>TP without Data</b> — encabezado fila 1, 6 filas no vacías × 30 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Actual Date  (for SPICE Display Date, add 1 for Leap Year) |  | text | 6 | 3 | NO DATA FOR ANY TESTPOINTS IN 2012, 2013-05-02T00:00:00, **NO DATA FOR THIS ADJUSTED DATE OF 5/3… |  |
| 2 | Approx Start Time ( with GMT) | with GMT | text | 4 | 3 | GMT-13 122  14:15-14:23, GMT-13 122 14:29:30-14:38, GMT-13 122 |  |
| 3 | As run test no. |  | numeric | 4 | 4 | 100 … 103 |  |
| 4 | Test no. |  | numeric | 4 | 4 | 78 … 95 |  |
| 5 | Sample no. |  | numeric | 4 | 3 | 40 … 44 |  |
| 6 | material |  | text | 4 | 4 | parrafin wax candle, paraffin wax candle, candle, Japan wax |  |
| 7 | Igniter |  | text | 4 | 1 | 20-14 |  |
| 8 | Flow restrictor |  | numeric | 4 | 1 | 2 … 2 |  |
| 9 | Sample distance |  | text | 4 | 2 | downstream, intermediate |  |
| 10 | Fan display |  | text | 4 | 3 | 51, pots 0.5, 0.4, 0.35, 0.33, 0.32, pot 1.5 ign, 3.5, Pots 1.5, 1 0.5, 0.4 |  |
| 11 | Air display |  | text | 3 | 3 | 5, 2, 1.5, etc, 5, 10, 5,3, 2, etc |  |
| 12 | Radiometer gain ( 1000, 250, 50, 10) | 1000, 250, 50, 10 | mixed | 4 | 3 | 50 … 250 | `250, 1000 (18:20:07)`×1 |
| 13 | Radiometer display |  | text | 2 | 2 | <1, n/a |  |
| 14 | GN2 Pot |  | text | 1 | 1 | n/a |  |
| 15 | GN2 display |  | text | 3 | 1 | n/a |  |
| 16 | Filter y/n |  | text | 4 | 1 | N |  |
| 17 | Release Mode (CH/CL) | CH/CL | text | 4 | 2 | CH, CL |  |
| 18 | Exposure Mode (M/A) | M/A | text | 4 | 1 | A |  |
| 19 | Exposure compensation   (-#EV) | -#EV | numeric | 4 | 1 | -5 … -5 |  |
| 20 | Bracket frames and exposure bracket (#F/ 1.0) | #F/ 1.0 | text | 3 | 3 | 14 bracket, 9 brackets, n/a |  |
| 21 | shutter speed (1/s) | 1/s | text | 4 | 2 | 9f1.0, 1 |  |
| 22 | F stop |  | text | 4 | 2 | F2, F4 |  |
| 23 | ISO |  | numeric | 4 | 2 | 1000 … 1600 |  |
| 24 | shutter hold s /cont |  | text | 4 | 2 | 7 s, cont |  |
| 25 | SD card S/N |  | numeric | 4 | 2 | 3 … 8 |  |
| 26 | total frames shot |  | numeric | 4 | 4 | 0 … 328 |  |
| 27 | O2 % by volume |  | numeric | 4 | 2 | 0.1605 … 0.163 |  |
| 28 | pressure, atm |  | numeric | 4 | 1 | 0.982 … 0.982 |  |
| 29 | CO2, mm Hg |  | numeric | 4 | 1 | 3.4 … 3.4 |  |
| 30 | Test Observations and Anomalies (ignited, spread, extinguished, burn time, color, etc.) |  | text | 4 | 4 | ignited 'concurrent' or stagnation.17:4…, no ignition, despite prolonged attempte…, nice blue flame with inner soot until l… |  |

</details>

#### `PSI-26_Science Documents_Planned_Test Matrix.xlsx`

- Lista: `added` · 20,976 bytes · sha256 `e0a06f81c110efc8…` · HTTP 200
- XLSX · **1** hojas

<details><summary>Hoja <b>BASS Test Matrix</b> — encabezado fila 5, 59 filas no vacías × 25 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Preferred Test Order |  | numeric | 16 | 16 | 1 … 16 |  |
| 2 | Sample Number |  | numeric | 17 | 16 | 17 … 44 | `Dark Frame Calibration`×1 |
| 3 | Test Point |  | numeric | 53 | 53 | 26 … 121 | `117a`×1 |
| 4 | Fuel  Descriptioin |  | text | 11 | 6 | 1 cm Sphere Sample (PMMA), 2 cm Sphere Sample (PMMA), Flat Wax Sample |  |
| 5 | Ignition Type |  | text | 9 | 2 | BASS IGNITER 015-13 FORWARD, BASS IGNITER 025-11 WAKE |  |
| 6 | Ignition time   -  seconds |  | text | 53 | 2 | 5 - 10, 10 - 20 |  |
| 7 | Extinguish ? |  | text | 53 | 1 | Y |  |
| 8 | Sample distance* |  | numeric | 57 | 7 | 1 … 3 | `*1`×1, `*2`×1, `*3`×1, `*4`×1 |
| 9 | Restricter |  | numeric | 53 | 1 | 2 … 2 |  |
| 10 | Nitrogen Fill GN2 Pot Setting |  | numeric | 57 | 11 | 2.5 … 10 | `Sample Holder Adjustable Bracket all th…`×2, `Front Edge of Frame at 10 mm position o…`×1, `Sample Holder Adjustable Bracket moved …`×1 |
| 11 | Still Camera Filter |  | text | 54 | 3 | n/a, N, Y |  |
| 12 | Release Mode |  | text | 54 | 2 | CH, CL |  |
| 13 | Exposure Mode |  | text | 54 | 2 | M, A |  |
| 14 | Exposure Compensation |  | text | 54 | 3 | 0 EV, -5 EV, -4 EV |  |
| 15 | Bracket Frames Exposure Bracket |  | text | 54 | 3 | 9F  1.0, -, 9F 1.0 |  |
| 16 | Shutter  Speed (1/sec) | 1/sec | text | 54 | 2 | 250, - |  |
| 17 | F-Stop Value |  | numeric | 54 | 2 | 2 … 4 |  |
| 18 | ISO |  | numeric | 54 | 2 | 1000 … 1600 |  |
| 19 | Shutter Button                                      Hold Time (sec) | sec | text | 53 | 2 | Con, 7 |  |
| 20 | Radiometer |  | numeric | 53 | 1 | 50 … 50 |  |
| 21 | GN2 Pot |  | numeric | 53 | 4 | 2 … 8 |  |
| 22 | FAN pot |  | numeric | 53 | 2 | 0.44 … 2.87 |  |
| 23 | FAN |  | numeric | 54 | 4 | 42 … 66 |  |
| 24 | <col 24> |  | empty | 0 | 0 |  |  |
| 25 | <col 25> |  | empty | 0 | 0 |  |  |

</details>

### Publicaciones con DOI (primeras 8)

- The Microgravity Science Glovebox as a Platform for Exploration Research on the International Space Station — doi:10.2514/6.2006-941
- Opposed-flow flame spread: A comparison of microgravity and normal gravity experiments to establish the thermal regime — doi:10.1016/j.firesaf.2015.11.011
- Simplified model for predicting difference between flammability limits of a thin material in normal gravity and microgravity environments — doi:10.1016/j.proci.2014.07.017
- A Correlation for an Effective Flow Velocity for Capturing the Boundary Layer Effect in Opposed-Flow Flame Spread over Thin Fuels — doi:10.1080/00102202.2014.900056
- Radiation signature in opposed-flow flame spread — doi:10.1504/pcfd.2012.048249
- OS24-1 The Effect of Boundary Layer on Blow-Off Extinction in Opposed-Flow Flame Spread: Results of Experiments and Simplified Analysis(invited,Scale modeling on solid combustion,OS24 Scale modeling,FLUID AND THERMODYNAMICS) — doi:10.1299/jsmeatem.2015.14.289
- A novel apparatus for flame spread study — doi:10.1016/j.proci.2012.05.076

<!-- AUTO:END -->

## Evaluación (manual — DE/PHY)

> Primera pasada DE-04 (2026-11-14) basada en el bloque automático y en las muestras L2. La clasificación
> Medida / Calculada / Log es **propuesta DE — pendiente de validación PHY (PHY-02)**.

### Resumen propio
BASS (primera campaña): sólidos (SIBAL, PMMA, Nomex, Ultem) en el MSG, 2012–2013.

### Granularidad y variables clave
| Archivo | Fila = … | Condición | Resultado | Calculadas | Notas |
|---|---|---|---|---|---|
| ET BASS (122) | 1 prueba | fecha, material | — | — | solo log |
| As Run Test Matrix `as run matrix` (130) | 1 prueba | material, ignitor, restrictor, displays de ventilador/aire, **O₂ % vol, presión (atm), CO₂ (mmHg)** | **observaciones en texto libre** (extinción, propagación…) | — | la fuente útil es esta, no el ET |

### Problemas de calidad / acceso
- El resultado solo está en texto libre. Extraer "se extinguió / propagó / no encendió" requiere codificación manual o asistida por LLM con verificación humana.

### Valor para el proyecto
- **Pilar:** prevención. **RQ:** RQ3 (contexto) y ranking.
- **Triage (borrador):** R1 3 · R2 3 · R3 2 · R4 2 · R5 2 · R6 2 → **Tier 2**.
