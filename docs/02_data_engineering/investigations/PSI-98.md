# PSI-98 — SAFFIRE-I · Spacecraft Fire Safety Experiment-I

<!-- AUTO:BEGIN — generado por `flamesafe profile`; no editar a mano dentro de este bloque -->

| Campo | Valor (PSI) |
|---|---|
| DOI de datos | 10.60555/0t15-1z43 |
| Tipo | Microgravity Investigation |
| Sub-área | Spacecraft Fire, Smoke Distribution |
| Programa / plataforma | International Space Station (ISS) / International Space Station (ISS) |
| Hardware | Saffire 1 enclosure in Cygnus |
| Centro | Glenn Research Center (GRC) |
| Periodo | 2001-03-02 → 2008-02-28 |
| Licencia | Creative Commons Zero v1.0 Universal |
| Investigaciones relacionadas | PSI-26, PSI-99, PSI-100 |
| Snapshot | snapshot_2026-11-14 |

### Inventario (L1)

| Archivos `added` | Tablas exp. (fuera de `added`) | `removed` | Publicaciones (con DOI) | GB expuestos | GB registrados | Acceso |
|---:|---:|---:|---:|---:|---:|---|
| 74 | 1 (1) | 85 | 6 (3) | 12.25 | 12.25 | `available` |

Categorías: Raw Data 68.0 (12.24 GB) · Science Documents 4.0 (0.01 GB) · Engineering Documents 2.0 (0.00 GB)
Extensiones: `.zip` 61 · `.pdf` 6 · `.xlsx` 4 · `.docx` 3

**Objetivo (texto PSI):**

> The objectives of this investigation were to: (1) determine how rapidly a large scale fire grows in low-gravity and (2) investigate the low-g flammability limits compared to those obtained in NASA’s normal gravity material flammability screening test.

**Hipótesis (texto PSI):**

> This investigation hypothesizes that due to large differences between fire behavior in normal and reduced gravity, the use of terrestrial fires and fire standards to design spacecraft fire safety systems presents an inherent risk to the vehicle because of the significant level of uncertainty. While this approach has been successful thus far, the uncertainty and risk will increase as exploration missions venture further from earth with considerably longer transit times for a safe return. There is a significant lack of microgravity data available for spacecraft designers on which to base their fire safety designs and procedures. To address this knowledge gap, this investigation proposed to …

### Archivos perfilados (L2)

#### `PSI-98_Experimental table_SAFFIRE-1.csv`

- Lista: `experimentalTable` · 469 bytes · sha256 `c01f29c62455f0a3…` · HTTP 200
- CSV · encoding `utf-8` · delimitador `,` · encabezado en fila 1 · filas no vacías **4** / físicas 4 · **13** columnas · bloques lado a lado: 1

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Sample Number |  | text | 4 | 4 | S1, S2, F1C1/F1C2 |  |
| 2 | Material |  | text | 4 | 3 | SIBAL Fabric, Pre-test flow visulation data for sampl…, Pre-test flow visulation data for sampl… |  |
| 3 | Sample Thickness (cm) | cm | numeric | 2 | 1 | 0.37 … 0.37 |  |
| 4 | Sample Length (cm) | cm | numeric | 2 | 1 | 40.6 … 40.6 |  |
| 5 | Sample Width (cm) | cm | numeric | 2 | 1 | 94 … 94 |  |
| 6 | Air Flow (cm/s) | cm/s | numeric | 2 | 1 | 20 … 20 |  |
| 7 | Percent O2 |  | text | 2 | 2 | 21.5 - 21.7, ~ 21.5 |  |
| 8 | Ignition Power (W) | W | numeric | 2 | 1 | 182 … 182 |  |
| 9 | Ignition Time (s) | s | numeric | 2 | 1 | 8 … 8 |  |
| 10 | Burn Time (s) | s | numeric | 2 | 2 | 70 … 420 |  |
| 11 | Flow Direction |  | text | 2 | 2 | Concurrent, Opposed |  |
| 12 | Camera 1 |  | text | 2 | 2 | S1C1, S2C1 |  |
| 13 | Camera 2 |  | text | 2 | 2 | S1C2, S2C2 |  |

#### `PSI-98_Raw Data_Saffire-I Telemetry Data Good Process Version.xlsx`

- Lista: `added` · 2,775,737 bytes · sha256 `2e6657842266b80d…` · HTTP 200
- XLSX · **6** hojas

<details><summary>Hoja <b>RawData</b> — encabezado fila 1, 9749 filas no vacías × 48 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | RelativeSeconds |  | numeric | 2645 | 2645 | 9.273e+06 … 1.597e+07 |  |
| 2 | CygnusTimestamp |  | numeric | 2645 | 2645 | 1.466e+12 … 1.466e+12 |  |
| 3 | SaffireTimestamp |  | numeric | 2645 | 106 | 0 … 1.466e+12 |  |
| 4 | Cyg-Saf TS (ms) | ms | numeric | 9749 | 2644 | -6527 … 1.466e+12 |  |
| 5 | Radiometer1Value |  | numeric | 2645 | 24 | -4078 … 128.1 |  |
| 6 | Radiometer2Value |  | numeric | 2645 | 23 | -4061 … 121.9 |  |
| 7 | Radiometer3Value |  | numeric | 2645 | 21 | -3867 … 136.8 |  |
| 8 | Radiometer4Value |  | numeric | 2645 | 25 | -3954 … 131.9 |  |
| 9 | Anemometer1 |  | numeric | 2645 | 36 | -72.12 … 32.75 |  |
| 10 | Anemometer2 |  | numeric | 2645 | 37 | -65.9 … 29.8 |  |
| 11 | FanTachometer |  | numeric | 2645 | 45 | -6.989e+04 … 8139 |  |
| 12 | SmokeWireV |  | numeric | 2645 | 5 | -161.7 … -80.84 |  |
| 13 | SmokeWireI |  | numeric | 2645 | 5 | -25.17 … -0.0009603 |  |
| 14 | Sample1IgniterV |  | numeric | 2645 | 4 | -161.7 … -80.84 |  |
| 15 | Sample1IgniterI |  | numeric | 2645 | 4 | -25.17 … -0.001729 |  |
| 16 | Sample2IgniterV |  | numeric | 2645 | 4 | -161.7 … -80.84 |  |
| 17 | Sample2IgniterI |  | numeric | 2645 | 4 | -25.17 … -12.59 |  |
| 18 | Sample3IgniterV |  | numeric | 2645 | 1 | -80.84 … -80.84 |  |
| 19 | Sample3IgniterI |  | numeric | 2645 | 1 | -12.59 … -12.59 |  |
| 20 | Sample4IgniterV |  | numeric | 2645 | 1 | -80.84 … -80.84 |  |
| 21 | Sample4IgniterI |  | numeric | 2645 | 1 | -12.59 … -12.59 |  |
| 22 | Sample5IgniterV |  | numeric | 2645 | 1 | -80.84 … -80.84 |  |
| 23 | Sample5IgniterI |  | numeric | 2645 | 1 | -12.59 … -12.59 |  |
| 24 | Sample6IgniterV |  | numeric | 2645 | 1 | -80.84 … -80.84 |  |
| 25 | Sample6IgniterI |  | numeric | 2645 | 1 | -12.59 … -12.59 |  |
| 26 | Sample7IgniterV |  | numeric | 2645 | 1 | -80.84 … -80.84 |  |
| 27 | Sample7IgniterI |  | numeric | 2645 | 1 | -12.59 … -12.59 |  |
| 28 | Sample8IgniterV |  | numeric | 2645 | 1 | -80.84 … -80.84 |  |
| 29 | Sample8IgniterI |  | numeric | 2645 | 1 | -12.59 … -12.59 |  |
| 30 | Sample9IgniterV |  | numeric | 2645 | 1 | -80.84 … -80.84 |  |
| 31 | Sample9IgniterI |  | numeric | 2645 | 1 | -12.59 … -12.59 |  |
| 32 | PCM Air Temp (degC) | degC | numeric | 2645 | 7 | 0 … 20.18 |  |
| 33 | PCM Press (psi) | psi | numeric | 2645 | 6 | 0 … 14.54 |  |
| 34 | PCM Press/Temp (psi/K) | psi/K | numeric | 2645 | 25 | 0 … 0.04957 |  |
| 35 | FIZ1 Smoke Detector Obscuration  (V) | V | numeric | 2645 | 2 | -0.005 … 0 |  |
| 36 | FIZ 2 Smoke Detector Obscuration (V) | V | numeric | 2645 | 11 | -4.395 … 3.845 |  |
| 37 | FIZ 1 Smoke Detector Scatterometer (V) | V | numeric | 2645 | 1 | 0 … 0 |  |
| 38 | FIZ 2 Smoke Detector Scatterometer (V) | V | numeric | 2645 | 80 | 0 … 2.9 |  |
| 39 | FIZ 1 Cabin Fan delta P (Pa) | Pa | numeric | 2645 | 3 | -126.4 … 0 |  |
| 40 | FIZ 2 Cabin Fan Delta P (Pa) | Pa | numeric | 2645 | 11 | -126.4 … 97.98 |  |
| … | _8 columnas más_ | | | | | | |

</details>

<details><summary>Hoja <b>CygnusData</b> — encabezado fila 1, 8072 filas no vacías × 23 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | CygnusTimestamp |  | numeric | 2540 | 2540 | 1.466e+12 … 1.466e+12 |  |
| 2 | Relative Time (ms) | ms | numeric | 2540 | 2540 | 9.275e+06 … 1.597e+07 |  |
| 3 | Relative Time (s) | s | numeric | 8072 | 2541 | 0 … 1.597e+04 |  |
| 4 | PCM Air Temp (degC) | degC | numeric | 2540 | 7 | 0 … 20.18 |  |
| 5 | PCM Press (psi) | psi | numeric | 2540 | 6 | 0 … 14.54 |  |
| 6 | PCM Press/Temp (psi/K) | psi/K | numeric | 2540 | 24 | 0 … 0.04957 |  |
| 7 | FIZ1 Smoke Detector Obscuration  (V) | V | numeric | 2540 | 2 | -0.005 … 0 |  |
| 8 | FIZ 2 Smoke Detector Obscuration (V) | V | numeric | 2540 | 11 | -4.395 … 3.845 |  |
| 9 | FIZ 1 Smoke Detector Scatterometer (V) | V | numeric | 2540 | 1 | 0 … 0 |  |
| 10 | FIZ 2 Smoke Detector Scatterometer (V) | V | numeric | 2540 | 80 | 0 … 2.9 |  |
| 11 | FIZ 1 Cabin Fan delta P (Pa) | Pa | numeric | 2540 | 3 | -126.4 … 0 |  |
| 12 | FIZ 2 Cabin Fan Delta P (Pa) | Pa | numeric | 2540 | 11 | -126.4 … 97.98 |  |
| 13 | body rate x axis (rad/s) | rad/s | numeric | 2540 | 190 | -0.006091 … 0.0001949 |  |
| 14 | body rate y axis (rad/s) | rad/s | numeric | 2540 | 518 | -0.0002604 … 0.008961 |  |
| 15 | body rate z axis (rad/s) | rad/s | numeric | 2540 | 515 | -0.0004287 … 0.01245 |  |
| 16 | acceleration x axis (m/s^2) | m/s^2 | numeric | 2540 | 634 | -0.0006923 … 0.0002728 |  |
| 17 | acceleration y axis (m/s^2) | m/s^2 | numeric | 2540 | 634 | -0.0005973 … 0.0003053 |  |
| 18 | acceleration z axis (m/s^2) | m/s^2 | numeric | 2540 | 634 | -0.0006174 … 0.0005304 |  |
| 19 | <col 19> |  | empty | 0 | 0 |  |  |
| 20 | Cygnus-Saffire Time Stamp (ms) | ms | numeric | 105 | 103 | -6527 … -3978 |  |
| 21 | <col 21> |  | empty | 0 | 0 |  |  |
| 22 | <col 22> |  | empty | 0 | 0 |  |  |
| 23 | Saffire timestamp row-to-row delta t (ms) | ms | numeric | 105 | 9 | 0 … 1.455e+06 |  |

</details>

<details><summary>Hoja <b>CygnusSmokeDetectorData</b> — encabezado fila 2, 289 filas no vacías × 9 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | CygnusTimestamp |  | numeric | 289 | 289 | 1.466e+12 … 1.466e+12 |  |
| 2 | Relative Time (ms) | ms | numeric | 289 | 289 | 9.283e+06 … 1.596e+07 |  |
| 3 | Relative Time (s) | s | numeric | 289 | 289 | 9283 … 1.596e+04 |  |
| 4 | FIZ 2 Smoke Detector Obscuration (V) | V | numeric | 289 | 10 | -4.395 … 3.845 |  |
| 5 | <col 5> |  | empty | 0 | 0 |  |  |
| 6 | CygnusTimestamp |  | numeric | 272 | 272 | 1.466e+12 … 1.466e+12 |  |
| 7 | Relative Time (ms) | ms | numeric | 272 | 272 | 1.093e+07 … 1.597e+07 |  |
| 8 | Relative Time (s) | s | numeric | 272 | 272 | 1.093e+04 … 1.597e+04 |  |
| 9 | FIZ 2 Smoke Detector Scatterometer (V) | V | numeric | 272 | 79 | 0.01 … 2.9 |  |

</details>

<details><summary>Hoja <b>CygnusPressureData</b> — encabezado fila 1, 332 filas no vacías × 10 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | CygnusTimestamp |  | numeric | 332 | 332 | 1.466e+12 … 1.466e+12 |  |
| 2 | Relative Time (ms) | ms | numeric | 332 | 332 | 9.276e+06 … 1.597e+07 |  |
| 3 | Relative Time (s) | s | numeric | 332 | 332 | 9276 … 1.597e+04 |  |
| 4 | PCM Press (psi) | psi | numeric | 332 | 5 | 14.47 … 14.54 |  |
| 5 | <col 5> |  | empty | 0 | 0 |  |  |
| 6 | <col 6> |  | empty | 0 | 0 |  |  |
| 7 | <col 7> |  | empty | 0 | 0 |  |  |
| 8 | Igniter data for line |  | mixed | 3 | 2 | 1.517e+04 … 1.517e+04 | `Relative Time (s)`×1 |
| 9 | <col 9> |  | mixed | 3 | 3 | -5 … -0.001729 | `Igniter Current`×1 |
| 10 | <col 10> |  | text | 2 | 2 | Real, A, Dummy data for line |  |

</details>

<details><summary>Hoja <b>CygnusTemperatureData</b> — encabezado fila 1, 322 filas no vacías × 4 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | CygnusTimestamp |  | numeric | 322 | 322 | 1.466e+12 … 1.466e+12 |  |
| 2 | Relative Time (ms) | ms | numeric | 322 | 322 | 9.278e+06 … 1.597e+07 |  |
| 3 | Relative Time (s) | s | numeric | 322 | 322 | 9278 … 1.597e+04 |  |
| 4 | PCM Air Temp (degC) | degC | numeric | 322 | 6 | 19.67 … 20.18 |  |

</details>

<details><summary>Hoja <b>SaffireData</b> — encabezado fila 1, 6083 filas no vacías × 33 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | SaffireTimestamp |  | numeric | 105 | 105 | 1.466e+12 … 1.466e+12 |  |
| 2 | delta timestamp (ms) | ms | numeric | 6083 | 10 | -1.466e+12 … 1.455e+06 |  |
| 3 | Relative Time (ms) | ms | numeric | 105 | 105 | 9.273e+06 … 1.595e+07 |  |
| 4 | Relative Time (s) | s | numeric | 105 | 105 | 9273 … 1.595e+04 |  |
| 5 | Radiometer1Value |  | numeric | 105 | 24 | -4078 … 128.1 |  |
| 6 | Radiometer2Value |  | numeric | 105 | 23 | -4061 … 121.9 |  |
| 7 | Radiometer3Value |  | numeric | 105 | 21 | -3867 … 136.8 |  |
| 8 | Radiometer4Value |  | numeric | 105 | 25 | -3954 … 131.9 |  |
| 9 | Anemometer1 |  | numeric | 105 | 36 | -72.12 … 32.75 |  |
| 10 | Anemometer2 |  | numeric | 105 | 37 | -65.9 … 29.8 |  |
| 11 | FanTachometer |  | numeric | 105 | 45 | -6.989e+04 … 8139 |  |
| 12 | SmokeWireV |  | numeric | 105 | 5 | -161.7 … -80.84 |  |
| 13 | SmokeWireI |  | numeric | 105 | 5 | -25.17 … -0.0009603 |  |
| 14 | Sample1IgniterV |  | numeric | 105 | 4 | -161.7 … -80.84 |  |
| 15 | Sample1IgniterI |  | numeric | 105 | 4 | -25.17 … -0.001729 |  |
| 16 | Sample2IgniterV |  | numeric | 105 | 4 | -161.7 … -80.84 |  |
| 17 | Sample2IgniterI |  | numeric | 105 | 4 | -25.17 … -12.59 |  |
| 18 | Sample3IgniterV |  | numeric | 105 | 1 | -80.84 … -80.84 |  |
| 19 | Sample3IgniterI |  | numeric | 105 | 1 | -12.59 … -12.59 |  |
| 20 | Sample4IgniterV |  | numeric | 105 | 1 | -80.84 … -80.84 |  |
| 21 | Sample4IgniterI |  | numeric | 105 | 1 | -12.59 … -12.59 |  |
| 22 | Sample5IgniterV |  | numeric | 105 | 1 | -80.84 … -80.84 |  |
| 23 | Sample5IgniterI |  | numeric | 105 | 1 | -12.59 … -12.59 |  |
| 24 | Sample6IgniterV |  | numeric | 105 | 1 | -80.84 … -80.84 |  |
| 25 | Sample6IgniterI |  | numeric | 105 | 1 | -12.59 … -12.59 |  |
| 26 | Sample7IgniterV |  | numeric | 105 | 1 | -80.84 … -80.84 |  |
| 27 | Sample7IgniterI |  | numeric | 105 | 1 | -12.59 … -12.59 |  |
| 28 | Sample8IgniterV |  | numeric | 105 | 1 | -80.84 … -80.84 |  |
| 29 | Sample8IgniterI |  | numeric | 105 | 1 | -12.59 … -12.59 |  |
| 30 | Sample9IgniterV |  | numeric | 105 | 1 | -80.84 … -80.84 |  |
| 31 | Sample9IgniterI |  | numeric | 105 | 1 | -12.59 … -12.59 |  |
| 32 | Rel-to-Cygnus Time (s) | s | numeric | 6083 | 106 | -1.466e+09 … 6682 |  |
| 33 | Tach/100 |  | numeric | 6083 | 46 | -698.9 … 81.39 |  |

</details>

#### `PSI-98_Science Documents_SAFFIRE-1_MergeResult-jpeg_Update_Final_v2.xlsx`

- Lista: `added` · 12,325,177 bytes · sha256 `9bfeb80f921d9669…` · HTTP 200
- XLSX · **12** hojas

<details><summary>Hoja <b>PreFlowVis - TimeSort</b> — encabezado fila 1, 1619 filas no vacías × 9 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Timestamp |  | numeric | 1619 | 1314 | 1.466e+12 … 1.466e+12 |  |
| 2 | Time delta |  | datetime | 1618 | 1314 | 1970-01-01T00:00:00, 1970-01-01T00:00:00.033000, 1970-01-01T00:00:00.034000 |  |
| 3 | Jpeg File Name |  | text | 1619 | 1619 | F1C1-1465936971405.jpeg, F1C2-1465936971405.jpeg, F1C2-1465936971438.jpeg |  |
| 4 | Pre FV Received |  | text | 1418 | 1418 | F1C1-1465936971405.jpeg, F1C2-1465936971405.jpeg, F1C1-1465936971439.jpeg |  |
| 5 | Pre FV Rec'd Corrupt |  | text | 111 | 111 | F1C2-1465936971438.jpeg, F1C2-1465936971532.jpeg, F1C2-1465936971566.jpeg |  |
| 6 | Jpeg File size (bytes) | bytes | numeric | 1619 | 1170 | 4.411e+04 … 8.609e+04 |  |
| 7 | Zip File Name |  | text | 54 | 54 | F1C1-1465936971405.zip, F1C2-1465936971438.zip, F1C1-1465936972398.zip |  |
| 8 | Zips Received |  | text | 52 | 52 | F1C1-1465936971405.zip, F1C2-1465936971438.zip, F1C1-1465936972398.zip |  |
| 9 | Zip File size (bytes) | bytes | numeric | 54 | 54 | 2.073e+06 … 2.523e+06 |  |

</details>

<details><summary>Hoja <b>PostFlowVis - jpeg TimeSort</b> — encabezado fila 1, 1619 filas no vacías × 9 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Timestamp |  | numeric | 1619 | 1222 | 1.466e+12 … 1.466e+12 |  |
| 2 | Time delta |  | datetime | 1618 | 1221 | 1970-01-01T00:00:00, 1970-01-01T00:00:00.034000, 1970-01-01T00:00:00.067000 |  |
| 3 | Jpeg File Name |  | text | 1619 | 1619 | F2C2-1465938488551.jpeg, F2C1-1465938488552.jpeg, F2C1-1465938488585.jpeg |  |
| 4 | Post FV Received |  | text | 1556 | 1556 | F2C2-1465938488551.jpeg, F2C1-1465938488552.jpeg, F2C1-1465938488585.jpeg |  |
| 5 | Post FV Rec'd Corrupt |  | text | 63 | 63 | F2C1-1465938489052.jpeg, F2C1-1465938489385.jpeg, F2C2-1465938489851.jpeg |  |
| 6 | Jpeg File size (bytes) | bytes | numeric | 1619 | 450 | 5.368e+04 … 7.33e+04 |  |
| 7 | Zip File Name |  | text | 54 | 54 | F2C1-1465938488552.zip, F2C2-1465938488585.zip, F2C1-1465938489551.zip |  |
| 8 | Zips Received |  | text | 54 | 54 | F2C1-1465938488552.zip, F2C2-1465938488585.zip, F2C1-1465938489551.zip |  |
| 9 | Zip File size (bytes) | bytes | numeric | 54 | 54 | 1.484e+06 … 1.835e+06 |  |

</details>

<details><summary>Hoja <b>Sample1 - jpeg TimeSort</b> — encabezado fila 1, 36233 filas no vacías × 9 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Timestamp |  | numeric | 36233 | 35412 | 1.466e+12 … 1.466e+12 |  |
| 2 | Time delta |  | datetime | 36232 | 35411 | 1970-01-01T00:00:00.001000, 1970-01-01T00:00:00.033000, 1970-01-01T00:00:00.034000 |  |
| 3 | Jpeg File Name |  | text | 36233 | 36233 | S1C1-1465937098442.jpeg, S1C2-1465937098443.jpeg, S1C1-1465937098475.jpeg |  |
| 4 | S1 Received |  | text | 28941 | 28941 | S1C2-1465937098443.jpeg, S1C2-1465937098476.jpeg, S1C2-1465937098523.jpeg |  |
| 5 | S1 Rec'd Corrupt |  | text | 97 | 97 | S1C1-1465937110806.jpeg, S1C1-1465937111210.jpeg, S1C2-1465937124539.jpeg |  |
| 6 | Jpeg File size (bytes) | bytes | numeric | 36233 | 10902 | 1.925e+04 … 1.102e+05 |  |
| 7 | Zip File Name |  | text | 1208 | 1208 | S1C1-1465937098442.zip, S1C2-1465937099323.zip, S1C1-1465937099457.zip |  |
| 8 | Zips Received |  | text | 969 | 969 | S1C1-1465937101465.zip, S1C2-1465937102330.zip, S1C1-1465937102465.zip |  |
| 9 | Zip File size (bytes) | bytes | numeric | 1208 | 1205 | 6.042e+04 … 1.371e+06 |  |

</details>

<details><summary>Hoja <b>Sample2 - jpeg TimeSort</b> — encabezado fila 1, 36300 filas no vacías × 9 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Timestamp |  | numeric | 36300 | 28811 | 1.466e+12 … 1.466e+12 |  |
| 2 | Time delta |  | datetime | 36299 | 28811 | 1970-01-01T00:00:00, 1970-01-01T00:00:00.033000, 1970-01-01T00:00:00.034000 |  |
| 3 | Jpeg File Name |  | text | 36300 | 36300 | S2C1-1465937793510.jpeg, S2C2-1465937793510.jpeg, S2C2-1465937793543.jpeg |  |
| 4 | S2 Received |  | text | 9164 | 9164 | S2C1-1465937796510.jpeg, S2C2-1465937796510.jpeg, S2C1-1465937796543.jpeg |  |
| 5 | S2 Rec'd Corrupt |  | text | 76 | 76 | S2C1-1465937797543.jpeg, S2C1-1465937797577.jpeg, S2C1-1465937799843.jpeg |  |
| 6 | Jpeg File size (bytes) | bytes | numeric | 36300 | 4536 | 1.928e+04 … 1.763e+05 |  |
| 7 | Zip File Name |  | text | 1210 | 1210 | S2C1-1465937793510.zip, S2C2-1465937793510.zip, S2C1-1465937794510.zip |  |
| 8 | Zips Received |  | text | 308 | 308 | S2C1-1465937796510.zip, S2C2-1465937796510.zip, S2C1-1465937797510.zip |  |
| 9 | Zip File size (bytes) | bytes | numeric | 1210 | 1184 | 4.476e+04 … 1.157e+06 |  |

</details>

<details><summary>Hoja <b>BIT - jpeg</b> — encabezado fila 1, 1800 filas no vacías × 10 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Timestamp |  | numeric | 1800 | 1800 | 1.466e+12 … 1.466e+12 |  |
| 2 | Time delta |  | datetime | 1799 | 1799 | 1970-01-01T00:00:00.033000, 1970-01-01T00:00:00.067000, 1970-01-01T00:00:00.100000 |  |
| 3 | Jpeg File ID (hex) | hex | text | 1800 | 1800 | 0x0c000000, 0x0c000001, 0x0c000002 |  |
| 4 | Jpeg File ID (decimal) | decimal | numeric | 1800 | 1800 | 2.013e+08 … 2.013e+08 |  |
| 5 | Jpeg File Name |  | text | 1800 | 1800 | F1C1-1465931237120.jpeg, F1C1-1465931237153.jpeg, F1C1-1465931237187.jpeg |  |
| 6 | Jpeg File size (bytes) | bytes | numeric | 1800 | 1083 | 2.254e+04 … 8.383e+04 |  |
| 7 | Zip File ID (hex) | hex | text | 60 | 60 | 0x10000000, 0x10000001, 0x10000002 |  |
| 8 | Zip File ID (decimal) | decimal | numeric | 60 | 60 | 2.684e+08 … 2.684e+08 |  |
| 9 | Zip File Name |  | text | 60 | 60 | F1C1-1465931237120.zip, F1C1-1465931238120.zip, F1C1-1465931239120.zip |  |
| 10 | Zip File size (bytes) | bytes | numeric | 60 | 60 | 7.062e+04 … 2.368e+06 |  |

</details>

<details><summary>Hoja <b>PreFlowVis - jpeg</b> — encabezado fila 1, 1619 filas no vacías × 13 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Timestamp |  | numeric | 1619 | 1314 | 1.466e+12 … 1.466e+12 |  |
| 2 | Time delta |  | datetime | 1618 | 1314 | 1970-01-01T00:00:00.034000, 1970-01-01T00:00:00.064000, 1970-01-01T00:00:00.097000 |  |
| 3 | Jpeg File ID (hex) | hex | text | 1619 | 1619 | 0x18000000, 0x18000001, 0x18000002 |  |
| 4 | Jpeg File ID (decimal) | decimal | numeric | 1619 | 1619 | 4.027e+08 … 4.027e+08 |  |
| 5 | Jpeg File Name |  | text | 1619 | 1619 | F1C1-1465936971405.jpeg, F1C1-1465936971439.jpeg, F1C1-1465936971469.jpeg |  |
| 6 | Pre FV Received |  | text | 1418 | 1418 | F1C1-1465936971405.jpeg, F1C1-1465936971439.jpeg, F1C1-1465936971469.jpeg |  |
| 7 | Pre FV Rec'd Corrupt |  | text | 111 | 111 | F1C1-1465936972265.jpeg, F1C1-1465936972602.jpeg, F1C1-1465936972999.jpeg |  |
| 8 | Jpeg File size (bytes) | bytes | numeric | 1619 | 1170 | 4.411e+04 … 8.609e+04 |  |
| 9 | Zip File ID (hex) | hex | text | 54 | 54 | 0x1c000000, 0x1c000001, 0x1c000002 |  |
| 10 | Zip File ID (decimal) | decimal | numeric | 54 | 54 | 4.698e+08 … 4.698e+08 |  |
| 11 | Zip File Name |  | text | 54 | 54 | F1C1-1465936971405.zip, F1C1-1465936972398.zip, F1C1-1465936973398.zip |  |
| 12 | Zips Received |  | text | 52 | 52 | F1C1-1465936971405.zip, F1C1-1465936972398.zip, F1C1-1465936973398.zip |  |
| 13 | Zip File size (bytes) | bytes | numeric | 54 | 54 | 2.073e+06 … 2.523e+06 |  |

</details>

<details><summary>Hoja <b>PostFlowVis - jpeg</b> — encabezado fila 1, 1619 filas no vacías × 13 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Timestamp |  | numeric | 1619 | 1222 | 1.466e+12 … 1.466e+12 |  |
| 2 | Time delta |  | datetime | 1618 | 1221 | 1970-01-01T00:00:00.033000, 1970-01-01T00:00:00.066000, 1970-01-01T00:00:00.100000 |  |
| 3 | Jpeg File ID (hex) | hex | text | 1619 | 1619 | 0x24000000, 0x24000001, 0x24000002 |  |
| 4 | Jpeg File ID (decimal) | decimal | numeric | 1619 | 1619 | 6.04e+08 … 6.04e+08 |  |
| 5 | Jpeg File Name |  | text | 1619 | 1619 | F2C1-1465938488552.jpeg, F2C1-1465938488585.jpeg, F2C1-1465938488618.jpeg |  |
| 6 | Post FV Received |  | text | 1556 | 1556 | F2C1-1465938488552.jpeg, F2C1-1465938488585.jpeg, F2C1-1465938488618.jpeg |  |
| 7 | Post FV Rec'd Corrupt |  | text | 63 | 63 | F2C1-1465938489052.jpeg, F2C1-1465938489385.jpeg, F2C1-1465938489853.jpeg |  |
| 8 | Jpeg File size (bytes) | bytes | numeric | 1619 | 450 | 5.368e+04 … 7.33e+04 |  |
| 9 | Zip File ID (hex) | hex | text | 54 | 54 | 0x28000000, 0x28000001, 0x28000002 |  |
| 10 | Zip File ID (decimal) | decimal | numeric | 54 | 54 | 6.711e+08 … 6.711e+08 |  |
| 11 | Zip File Name |  | text | 54 | 54 | F2C1-1465938488552.zip, F2C1-1465938489551.zip, F2C1-1465938490551.zip |  |
| 12 | Zips Received |  | text | 54 | 54 | F2C1-1465938488552.zip, F2C1-1465938489551.zip, F2C1-1465938490551.zip |  |
| 13 | Zip File size (bytes) | bytes | numeric | 54 | 54 | 1.484e+06 … 1.835e+06 |  |

</details>

<details><summary>Hoja <b>Sample1 - jpeg</b> — encabezado fila 1, 36233 filas no vacías × 13 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Timestamp |  | numeric | 36233 | 35412 | 1.466e+12 … 1.466e+12 |  |
| 2 | Time delta |  | datetime | 36232 | 35411 | 1970-01-01T00:00:00.033000, 1970-01-01T00:00:00.082000, 1970-01-01T00:00:00.115000 |  |
| 3 | Jpeg File ID (hex) | hex | text | 36233 | 36233 | 0x30000000, 0x30000001, 0x30000002 |  |
| 4 | Jpeg File ID (decimal) | decimal | numeric | 36233 | 36233 | 8.053e+08 … 8.053e+08 |  |
| 5 | Jpeg File Name |  | text | 36233 | 36233 | S1C1-1465937098442.jpeg, S1C1-1465937098475.jpeg, S1C1-1465937098524.jpeg |  |
| 6 | S1 Received |  | text | 28941 | 28941 | S1C1-1465937101465.jpeg, S1C1-1465937101499.jpeg, S1C1-1465937101532.jpeg |  |
| 7 | S1 Rec'd Corrupt |  | text | 97 | 97 | S1C1-1465937110806.jpeg, S1C1-1465937111210.jpeg, S1C1-1465937126648.jpeg |  |
| 8 | Jpeg File size (bytes) | bytes | numeric | 36233 | 10902 | 1.925e+04 … 1.102e+05 |  |
| 9 | Zip File ID (hex) | hex | text | 1208 | 1208 | 0x34000000, 0x34000001, 0x34000002 |  |
| 10 | Zip File ID (decimal) | decimal | numeric | 1208 | 1208 | 8.724e+08 … 8.724e+08 |  |
| 11 | Zip File Name |  | text | 1208 | 1208 | S1C1-1465937098442.zip, S1C1-1465937099457.zip, S1C1-1465937100457.zip |  |
| 12 | Zips Received |  | text | 969 | 969 | S1C1-1465937101465.zip, S1C1-1465937102465.zip, S1C1-1465937103474.zip |  |
| 13 | Zip File size (bytes) | bytes | numeric | 1208 | 1205 | 6.042e+04 … 1.371e+06 |  |

</details>

<details><summary>Hoja <b>Sample2 - jpeg</b> — encabezado fila 1, 36300 filas no vacías × 13 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Timestamp |  | numeric | 36300 | 28811 | 1.466e+12 … 1.466e+12 |  |
| 2 | Time delta |  | datetime | 36299 | 28811 | 1970-01-01T00:00:00.034000, 1970-01-01T00:00:00.067000, 1970-01-01T00:00:00.101000 |  |
| 3 | Jpeg File ID (hex) | hex | text | 36300 | 36300 | 0x3c000000, 0x3c000001, 0x3c000002 |  |
| 4 | Jpeg File ID (decimal) | decimal | numeric | 36300 | 36300 | 1.007e+09 … 1.007e+09 |  |
| 5 | Jpeg File Name |  | text | 36300 | 36300 | S2C1-1465937793510.jpeg, S2C1-1465937793544.jpeg, S2C1-1465937793577.jpeg |  |
| 6 | S2 Received |  | text | 9164 | 9164 | S2C1-1465937796510.jpeg, S2C1-1465937796543.jpeg, S2C1-1465937796577.jpeg |  |
| 7 | S2 Rec'd Corrupt |  | text | 76 | 76 | S2C1-1465937797543.jpeg, S2C1-1465937797577.jpeg, S2C1-1465937799843.jpeg |  |
| 8 | Jpeg File size (bytes) | bytes | numeric | 36300 | 4536 | 1.928e+04 … 1.763e+05 |  |
| 9 | Zip File ID (hex) | hex | text | 1210 | 1210 | 0x40000000, 0x40000001, 0x40000002 |  |
| 10 | Zip File ID (decimal) | decimal | numeric | 1210 | 1210 | 1.074e+09 … 1.074e+09 |  |
| 11 | Zip File Name |  | text | 1210 | 1210 | S2C1-1465937793510.zip, S2C1-1465937794510.zip, S2C1-1465937795510.zip |  |
| 12 | Zips Received |  | text | 308 | 308 | S2C1-1465937796510.zip, S2C1-1465937797510.zip, S2C1-1465937798510.zip |  |
| 13 | Zip File size (bytes) | bytes | numeric | 1210 | 1184 | 4.476e+04 … 1.157e+06 |  |

</details>

<details><summary>Hoja <b>Received - jpeg</b> — encabezado fila 1, 28941 filas no vacías × 4 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | S1 Received |  | text | 28941 | 28941 | S1C1-1465937101465.jpeg, S1C1-1465937101499.jpeg, S1C1-1465937101532.jpeg |  |
| 2 | S2 Received |  | text | 9164 | 9164 | S2C1-1465937796510.jpeg, S2C1-1465937796543.jpeg, S2C1-1465937796577.jpeg |  |
| 3 | F1 Received |  | text | 1418 | 1418 | F1C1-1465936971405.jpeg, F1C1-1465936971439.jpeg, F1C1-1465936971469.jpeg |  |
| 4 | F2 Received |  | text | 1556 | 1556 | F2C1-1465938488552.jpeg, F2C1-1465938488585.jpeg, F2C1-1465938488618.jpeg |  |

</details>

<details><summary>Hoja <b>Received - jpeg Corrupted</b> — encabezado fila 1, 111 filas no vacías × 4 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | S1 Received Corrupted |  | text | 97 | 97 | S1C1-1465937110806.jpeg, S1C1-1465937111210.jpeg, S1C1-1465937126648.jpeg |  |
| 2 | S2 Received Corrupted |  | text | 76 | 76 | S2C1-1465937797543.jpeg, S2C1-1465937797577.jpeg, S2C1-1465937799843.jpeg |  |
| 3 | F1 Received Corrupted |  | text | 111 | 111 | F1C1-1465936972265.jpeg, F1C1-1465936972602.jpeg, F1C1-1465936972999.jpeg |  |
| 4 | F2 Received Corrupted |  | text | 63 | 63 | F2C1-1465938489052.jpeg, F2C1-1465938489385.jpeg, F2C1-1465938489853.jpeg |  |

</details>

<details><summary>Hoja <b>Received - jpeg Zips</b> — encabezado fila 1, 969 filas no vacías × 4 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | S1-zip Received |  | text | 969 | 969 | S1C1-1465937101465.zip, S1C1-1465937102465.zip, S1C1-1465937103474.zip |  |
| 2 | S2-zip Received |  | text | 308 | 308 | S2C1-1465937796510.zip, S2C1-1465937797510.zip, S2C1-1465937798510.zip |  |
| 3 | F1-zip Received |  | text | 52 | 52 | F1C1-1465936971405.zip, F1C1-1465936972398.zip, F1C1-1465936973398.zip |  |
| 4 | F2-zip Received |  | text | 54 | 54 | F2C1-1465938488552.zip, F2C1-1465938489551.zip, F2C1-1465938490551.zip |  |

</details>

### Publicaciones con DOI (primeras 8)

- Flame spread: Effects of microgravity and scale — doi:10.1016/j.combustflame.2018.10.012
- Transient flame growth and spread processes over a large solid fabric in concurrent low-speed flows in microgravity – Model versus experiment — doi:10.1016/j.proci.2018.05.168
- Fire safety in space – beyond flammability testing of small samples — doi:10.1016/j.actaastro.2014.11.025

<!-- AUTO:END -->

## Evaluación (manual — DE/PHY)

> Primera pasada DE-04 (2026-11-14) basada en el bloque automático y en las muestras L2. La clasificación
> Medida / Calculada / Log es **propuesta DE — pendiente de validación PHY (PHY-02)**.

### Resumen propio
SAFFIRE-I: incendio a gran escala de tela SIBAL (94 × 40.6 cm) en el módulo Cygnus tras salir de la ISS. Flujo de 20 cm/s y
O₂ ≈ 21.5%.

### Granularidad y variables clave
| Archivo | Fila = … | Condición | Resultado (medido) | Calculadas | Notas |
|---|---|---|---|---|---|
| ET SAFFIRE-1 (4) | 1 muestra (2 reales + 2 filas de visualización de flujo) | material, dimensiones, flujo, % O₂, potencia y tiempo de ignición, dirección | tiempo de quemado | — | `21.5 - 21.7` como rango |
| Telemetría XLSX `RawData` (2,645 válidas) | 1 instante (~1 Hz) | ventilador, anemómetros | **radiómetros ×4, detectores de humo FIZ (oscurecimiento/dispersión), presión y T de cabina** | — | **antes 404, ahora disponible** |
| MergeResult-jpeg | 1 imagen | — | índice de imágenes (exposición, ganancia) | — | **no** son tasas de propagación |

### Problemas de calidad / acceso
- La plataforma dice ISS, pero el hardware es un recinto en Cygnus. Las filas de visualización de flujo están mezcladas con las muestras en el ET.

### Valor para el proyecto
- **Pilar:** detección (respuesta de detectores de humo de la nave a un incendio real) y prevención.
- **RQ:** RQ4 (detección) y como serie temporal de incendio a escala (stretch).
- **Triage (borrador):** R1 3 · R2 3 · R3 3 · R4 2 · R5 3 · R6 2 → **Tier 2** (sube desde "Supporting" sin telemetría).
