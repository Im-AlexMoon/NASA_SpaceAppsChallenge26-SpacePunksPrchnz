# PSI-10 — ACME/Flame Design · Advanced Combustion via Microgravity Experiments / Flame Design

<!-- AUTO:BEGIN — generado por `flamesafe profile`; no editar a mano dentro de este bloque -->

| Campo | Valor (PSI) |
|---|---|
| DOI de datos | 10.60555/w4zy-bt45 |
| Tipo | Microgravity Investigation |
| Sub-área | Flames of Gaseous Fuels |
| Programa / plataforma | International Space Station (ISS) / International Space Station (ISS) |
| Hardware | Advanced Combustion via Microgravity Experiments (ACME), Combustion Integrated Rack (CIR), Reconfiguration of Combustion Integrated Rack (CIR) |
| Centro | Glenn Research Center (GRC) |
| Periodo | 1999-01-14 → 2025-04-30 |
| Licencia | — |
| Investigaciones relacionadas | — |
| Snapshot | snapshot_2026-11-14 |

### Inventario (L1)

| Archivos `added` | Tablas exp. (fuera de `added`) | `removed` | Publicaciones (con DOI) | GB expuestos | GB registrados | Acceso |
|---:|---:|---:|---:|---:|---:|---|
| 3,807 | 2 (0) | 0 | 33 (33) | 2,180.44 | 2,180.44 | `available` |

Categorías: Raw Data 3,792.0 (2,180.42 GB) · Representative Image(s) 5.0 (0.00 GB) · Reports 3.0 (0.00 GB) · Science Documents 3.0 (0.00 GB) · Experimental table 2.0 (0.00 GB) · Engineering Documents 1.0 (0.01 GB) · metadata 1.0 (0.00 GB)
Extensiones: `.zip` 1,184 · `.txt` 993 · `.csv` 636 · `.mdipsug` 490 · `.ts` 317 · `.pdf` 76 · `.asc` 66 · `.log` 35

**Objetivo (texto PSI):**

> The primary objectives of this flight experiment are: A. Obtain soot-inception limits of quasi-steady normal and inverse spherical diffusion flames as functions of flow rate, Zst, amount of inert (N2 or CO2), and pressure for C2H4 and CH4 flames. Identify the corresponding temperatures in hot regions. Obtain similar limits and temperatures for inverse and normal coflow flames. B. Obtain detailed measurements in quasi-steady normal and inverse spherical diffusion flames for C2H4 and CH4. Determine the effects of flow rate, Zst, amount of N2, and pressure on flame temperature, size, color, and soot volume fraction. Evaluate the possible existence of steady flames. C. Obtain extinction limits …

**Hipótesis (texto PSI):**

> 1. Soot formation requires a region where local C/O ratio and T exceed their critical values, and where strain rate is sufficiently low. 2. Microgravity spherical diffusion flames extinguish when the peak temperature first decreases below 1130 K. 3. Steady-state spherical diffusion flames are possible.

### Archivos perfilados (L2)

#### `PSI-10_Experimental table_Flame Design_Inverse Flame.csv`

- Lista: `experimentalTable` · 17,314 bytes · sha256 `97933ee9ae0b9ebc…` · HTTP 200
- CSV · encoding `utf-8` · delimitador `,` · encabezado en fila 1 · filas no vacías **120** / físicas 120 · **14** columnas · bloques lado a lado: 1

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Flame Type |  | text | 120 | 1 | Inverse |  |
| 2 | Day |  | numeric | 120 | 8 | 1 … 8 |  |
| 3 | Test |  | text | 120 | 120 | 21328A1, 21328A2, 21328D1 |  |
| 4 | XO2 |  | numeric | 120 | 60 | 0.212 … 0.85 | `RAMP`×9, `LOW O2`×2 |
| 5 | mO2 (mg/s) | mg/s | numeric | 120 | 114 | 1.524 … 9.799 | `RAMP`×6, `LOW O2`×2 |
| 6 | mN2 (mg/s) | mg/s | numeric | 120 | 111 | 0.2354 … 9.611 | `RAMP`×9, `LOW O2`×2 |
| 7 | mtot (mg/s) | mg/s | numeric | 120 | 111 | 1.759 … 13.76 | `RAMP`×9, `LOW O2`×2 |
| 8 | XC2H4 initial |  | numeric | 120 | 120 | 0.08031 … 0.6581 |  |
| 9 | XC2H4 final |  | numeric | 120 | 120 | 0.08009 … 0.6571 |  |
| 10 | pinit (atm) | atm | numeric | 120 | 69 | 0.4246 … 3.008 |  |
| 11 | pfinal (atm) | atm | numeric | 120 | 72 | 0.4273 … 3.029 |  |
| 12 | pmean (atm) | atm | numeric | 120 | 89 | 0.426 … 3.018 |  |
| 13 | mean Zst |  | numeric | 120 | 111 | 0.09532 … 0.7585 | `RAMP`×9, `LOW O2`×2 |
| 14 | Tad (K) | K | numeric | 120 | 111 | 2074 … 2974 | `RAMP`×9, `LOW O2`×2 |

#### `PSI-10_Experimental table_Flame Design_Normal Flame.csv`

- Lista: `experimentalTable` · 26,933 bytes · sha256 `4a663292bd3f6520…` · HTTP 200
- CSV · encoding `utf-8` · delimitador `,` · encabezado en fila 1 · filas no vacías **207** / físicas 207 · **15** columnas · bloques lado a lado: 1

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Flame Type |  | text | 207 | 1 | Normal |  |
| 2 | Day |  | numeric | 207 | 14 | 0 … 13 |  |
| 3 | Fuel |  | text | 207 | 2 | C2H4, C3H8 |  |
| 4 | Test |  | text | 207 | 207 | 19115A1, 19115D2, 19115B1 |  |
| 5 | Xfuel |  | mixed | 207 | 98 | 0.04984 … 1 | `RAMP`×57, `RAMPED`×3 |
| 6 | mfuel (mg/s) | mg/s | mixed | 207 | 142 | 0.3127 … 2.521 | `RAMP`×57, `RAMPED`×3 |
| 7 | mN2 (mg/s) | mg/s | mixed | 207 | 99 | 0 … 20.24 | `RAMP`×57, `RAMPED`×3 |
| 8 | mtot (mg/s) | mg/s | mixed | 207 | 144 | 0.3127 … 21.54 | `RAMP`×57, `RAMPED`×3 |
| 9 | XO2 (init) | init | numeric | 207 | 188 | 0.198 … 0.4 |  |
| 10 | XO2 (final) | final | numeric | 187 | 187 | 0.1975 … 0.3972 |  |
| 11 | pinit (atm) | atm | numeric | 207 | 80 | 0.932 … 1.297 |  |
| 12 | pfinal (atm) | atm | numeric | 187 | 91 | 0.9928 … 1.324 |  |
| 13 | pmean (atm) | atm | numeric | 187 | 112 | 0.9921 … 1.311 |  |
| 14 | mean Zst |  | mixed | 207 | 135 | 0.06092 … 0.7154 | `RAMP`×57, `RAMPED`×3 |
| 15 | Tad (K) | K | mixed | 207 | 135 | 1683 … 2831 | `RAMP`×57, `RAMPED`×3 |

#### `PSI-10_Raw Data_19196B1_data.csv`

- Lista: `added` · 3,401,632 bytes · sha256 `fff7cbc314135b38…` · HTTP 200
- CSV · encoding `utf-8` · delimitador `,` · encabezado en fila 2 · filas no vacías **9879** / físicas 9879 · **36** columnas · bloques lado a lado: 1
- Preámbulo de metadatos (fila 1): 2019-07-15 196 18=02:46:866, Experiment=0, Test Point=19196B1, MFCA1 Gas=2, MFCA1 Full Scale=20.000000, MFCA2 Gas=0, MFCA2 Full Scale=0.500000, MFCA3 Gas=4…

<details><summary>Columnas (36)</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Time |  | text | 9879 | 9879 | 18:03:27:902, 18:03:27:910, 18:03:27:919 |  |
| 2 | MFCA1StaticMixerFlow |  | numeric | 9879 | 52 | -0.005841 … -0.001489 |  |
| 3 | MFCA2BypassFlow |  | numeric | 9879 | 773 | -0.01987 … 1.591 |  |
| 4 | MFCA3FuelFlow |  | numeric | 9879 | 958 | -0.03109 … 2.195 |  |
| 5 | IonCurrent |  | numeric | 9879 | 1714 | -0.926 … 0.9578 |  |
| 6 | PTA1 |  | numeric | 9879 | 30 | 0.497 … 0.4992 |  |
| 7 | PTA2 |  | numeric | 9879 | 238 | 1.024 … 1.043 |  |
| 8 | PTA3 |  | numeric | 9879 | 105 | 1.021 … 1.029 |  |
| 9 | EfieldVoltage |  | numeric | 9879 | 188 | 0.1047 … 0.1197 |  |
| 10 | PMT1 |  | numeric | 9879 | 3707 | -0.0008011 … 4.554 |  |
| 11 | PMT2 |  | numeric | 9879 | 3162 | 0.001183 … 4.575 |  |
| 12 | PMT3 |  | numeric | 9879 | 3512 | -0.0008774 … 4.574 |  |
| 13 | TCA |  | numeric | 9879 | 1771 | 0.000157 … 0.0004432 |  |
| 14 | TCB |  | numeric | 9879 | 678 | -2.272e-05 … 8.605e-05 |  |
| 15 | TCC |  | numeric | 9879 | 293 | -2.347e-05 … 2.511e-05 |  |
| 16 | TCD |  | numeric | 9879 | 2101 | 1.855e-05 … 0.0007724 |  |
| 17 | TC200A |  | numeric | 9879 | 271 | 2.392e-05 … 6.787e-05 |  |
| 18 | TC200B |  | numeric | 9879 | 197 | -1.855e-05 … 1.572e-05 |  |
| 19 | TCBurner |  | numeric | 9879 | 6375 | 5.461e-05 … 0.01307 |  |
| 20 | Radiometer+60 |  | numeric | 9879 | 6343 | 1.246 … 2.408 |  |
| 21 | Radiometer+60CJ |  | numeric | 9879 | 106 | 1.573 … 1.574 |  |
| 22 | Radiometer+30 |  | numeric | 9879 | 6606 | 1.247 … 4.336 |  |
| 23 | Radiometer+30CJ |  | numeric | 9879 | 120 | 1.57 … 1.571 |  |
| 24 | RadiometerCenter |  | numeric | 9879 | 6433 | 1.243 … 4.852 |  |
| 25 | RadiometerCenterCJ |  | numeric | 9879 | 136 | 1.57 … 1.572 |  |
| 26 | Radiometer-30 |  | numeric | 9879 | 4561 | 1.246 … 4.866 |  |
| 27 | Radiometer-30CJ |  | numeric | 9879 | 110 | 1.562 … 1.564 |  |
| 28 | Radiometer-60 |  | numeric | 9879 | 6306 | 1.252 … 2.671 |  |
| 29 | Radiometer-60CJ |  | numeric | 9879 | 93 | 1.571 … 1.572 |  |
| 30 | RadiometerOffset |  | numeric | 9879 | 6701 | 1.224 … 4.868 |  |
| 31 | RadiometerOffsetCJ |  | numeric | 9879 | 53 | 1.571 … 1.571 |  |
| 32 | TCE |  | numeric | 9879 | 55 | -0.1342 … -0.1341 |  |
| 33 | Ch20 |  | numeric | 9879 | 182 | -2.526e-05 … 3.055e-06 |  |
| 34 | Ch21 |  | numeric | 9879 | 179 | -2.511e-05 … 7.376e-06 |  |
| 35 | TCCJ |  | numeric | 9879 | 168 | 0.8753 … 0.8756 |  |
| 36 | EfieldSetpointOut |  | numeric | 9879 | 1 | 9.99 … 9.99 |  |

</details>

#### `PSI-10_Raw Data_19196B1_mfcSetpoints.csv`

- Lista: `added` · 1,966 bytes · sha256 `727afcadef22ed2f…` · HTTP 200
- CSV · encoding `utf-8` · delimitador `,` · encabezado en fila 2 · filas no vacías **38** / físicas 38 · **4** columnas · bloques lado a lado: 1
- Preámbulo de metadatos (fila 1): 2019-07-15 196 18=02:46:866, Experiment=0, Test Point=19196B1, MFCA1 Gas=2, MFCA1 Full Scale=20.000000, MFCA2 Gas=0, MFCA2 Full Scale=0.500000, MFCA3 Gas=4…

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Time |  | text | 38 | 7 | 18:03:17:272, 18:03:17:273, 18:03:50:545 |  |
| 2 | MFCA1Setpoint(V) | V | numeric | 38 | 1 | 0 … 0 |  |
| 3 | MFCA2Setpoint(V) | V | numeric | 38 | 2 | 0 … 1.17 |  |
| 4 | MFCA3Setpoint(V) | V | numeric | 38 | 2 | 0 … 1.95 |  |

#### `PSI-10_Raw Data_Final ACME Chamber Calculator - 2019-04-09 to 2019-08-13.xlsx`

- Lista: `added` · 534,510 bytes · sha256 `0b0fd61b6811a55c…` · HTTP 200
- XLSX · **10** hojas

<details><summary>Hoja <b>Notes</b> — encabezado fila 1, 4 filas no vacías × 1 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Completing Burn Fraction on "EventData" Sheet |  | text | 4 | 4 | This version of the ACME Chamber Calcul…, Protecting/Unprotecting Data, The file is protected to prevent accide… |  |

</details>

<details><summary>Hoja <b>EventData</b> — encabezado fila 3, 350 filas no vacías × 112 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | OP |  | text | 339 | 7 | Cabin Air, Vent, GN2 Fill |  |
| 2 | Ignite |  | text | 223 | 2 | No, Yes |  |
| 3 | TPID |  | text | 223 | 223 | 19112MFCA2_01-03, 19112MFCA2_04-15, 19115A1 |  |
| 4 | <col 4> |  | empty | 0 | 0 |  |  |
| 5 | Diluent |  | text | 339 | 1 | 67212MFAM70100 |  |
| 6 | <col 6> |  | numeric | 339 | 1 | 2001 … 2001 |  |
| 7 | Oxygen |  | text | 339 | 2 | 67212MFAM70001, 67212MFAM70002 |  |
| 8 | <col 8> |  | numeric | 339 | 9 | 2001 … 2040 |  |
| 9 | Fuel |  | text | 339 | 1 | 67212MFAM70300 |  |
| 10 | <col 10> |  | numeric | 339 | 3 | 2003 … 2008 |  |
| 11 | Adsorber |  | numeric | 339 | 1 | 2007 … 2007 |  |
| 12 | <col 12> |  | empty | 0 | 0 |  |  |
| 13 | Tstart (GMT) | GMT | text | 339 | 339 | 2019-04-09 08:43:00, 2019-04-22 14:12:22, 2019-04-22 14:42:49 |  |
| 14 | Tend (GMT) | GMT | text | 339 | 339 | 2019-04-09 13:45:00, 2019-04-22 14:22:33, 2019-04-22 14:48:11 |  |
| 15 | Diluent |  | empty | 0 | 0 |  |  |
| 16 | Oxygen |  | empty | 0 | 0 |  |  |
| 17 | Nitrogen |  | numeric | 159 | 157 | 0 … 8.937 |  |
| 18 | Fuel |  | numeric | 214 | 214 | 0.001889 … 0.349 |  |
| 19 | Pstart (psia) | psia | numeric | 324 | 143 | 0.2 … 40.01 | `FCU_MP_PT28`×1 |
| 20 | Pend (psia) | psia | numeric | 331 | 151 | 0.2 … 40 | `FCU_MP_PT28`×1 |
| 21 | <col 21> |  | empty | 0 | 0 |  |  |
| 22 | Source-ID (SID) | SID | text | 349 | 13 | Cabin Air, Vent, GN2 Fill |  |
| 23 | Type |  | text | 339 | 5 | Set, Vent, Add |  |
| 24 | Fuel Type |  | text | 223 | 1 | Ethylene |  |
| 25 | Igniter Wattage |  | text | 1 | 1 | TP_PARAMETER_IGNITER_WATTAGE |  |
| 26 | Igniter On Time (ms) | ms | text | 1 | 1 | TP_PARAMETER_IGNITER_ON_TIME |  |
| 27 | Ign_1 Pos (counts) | counts | text | 1 | 1 | TP_PARAMETER_IGNITER_IGNITION_POSITION_1 |  |
| 28 | Ign_2 Pos (counts) | counts | text | 1 | 1 | TP_PARAMETER_IGNITER_IGNITION_POSITION_2 |  |
| 29 | TM1start  (°C) | °C | text | 1 | 1 | FCU_MP_TM1 |  |
| 30 | TM2start (°C) | °C | text | 1 | 1 | FCU_MP_TM2 |  |
| 31 | TM3start (°C) | °C | text | 1 | 1 | FCU_MP_TM3 |  |
| 32 | TM4start (°C) | °C | text | 1 | 1 | FCU_MP_TM4 |  |
| 33 | TM1end (°C) | °C | text | 1 | 1 | FCU_MP_TM1 |  |
| 34 | TM2end (°C) | °C | text | 1 | 1 | FCU_MP_TM2 |  |
| 35 | TM3end (°C) | °C | text | 1 | 1 | FCU_MP_TM3 |  |
| 36 | TM4end (°C) | °C | text | 1 | 1 | FCU_MP_TM4 |  |
| 37 | <col 37> |  | empty | 0 | 0 |  |  |
| 38 | Burn Fraction |  | numeric | 349 | 2 | 0 … 1 |  |
| 39 | <col 39> |  | empty | 0 | 0 |  |  |
| 40 | _O2 |  | numeric | 340 | 277 | 0.002057 … 61.59 | `-`×7 |
| … | _72 columnas más_ | | | | | | |

</details>

<details><summary>Hoja <b>SourceTable</b> — encabezado fila 2, 132 filas no vacías × 31 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Source |  | text | 132 | 16 | Vlookup Constants, ISS Sources, Cabin Air |  |
| 2 | ID |  | numeric | 126 | 55 | 2001 … 2053 | `ISS`×3, `N/A`×3 |
| 3 | Source-ID |  | text | 126 | 124 | Cabin Air, Vent, GN2 Fill |  |
| 4 | _O2 |  | numeric | 66 | 6 | 0 … 2 |  |
| 5 | _He |  | numeric | 24 | 8 | 0 … 3 |  |
| 6 | _CO2 |  | numeric | 6 | 3 | -1 … 4 |  |
| 7 | _N2 |  | numeric | 68 | 8 | 0.15 … 5 |  |
| 8 | _H20 |  | numeric | 6 | 3 | -1 … 6 |  |
| 9 | _Ethylene |  | numeric | 18 | 6 | 0.2 … 7 |  |
| 10 | _Methane |  | numeric | 12 | 11 | 0.15 … 8 |  |
| 11 | _Propane |  | numeric | 7 | 3 | 0.3 … 9 |  |
| 12 | _Butane |  | numeric | 8 | 4 | 0.3 … 10 |  |
| 13 | _Ethane |  | numeric | 7 | 3 | 0.3 … 11 |  |
| 14 | _H2 |  | numeric | 9 | 9 | 0.2 … 12 |  |
| 15 | _Fuel |  | text | 57 | 28 | 13, Oxygen / Nitrogen (85/15), Methane |  |
| 16 | _GCF |  | numeric | 120 | 35 | 0.2622 … 14 |  |
| 17 | Carrier |  | text | 121 | 18 | 15, OA-5, SpX-6 |  |
| 18 | Note |  | text | 3 | 1 | (Molecular Sieve) |  |
| 19 | <col 19> |  | empty | 0 | 0 |  |  |
| 20 | _O2 |  | numeric | 120 | 6 | 0 … 0.9779 |  |
| 21 | _He |  | numeric | 120 | 8 | 0 … 1.401 |  |
| 22 | _CO2 |  | numeric | 120 | 2 | 0 … 0.7526 |  |
| 23 | _N2 |  | numeric | 120 | 8 | 0 … 1 |  |
| 24 | _H20 |  | numeric | 120 | 2 | 0 … 0.7992 |  |
| 25 | _Ethylene |  | numeric | 120 | 7 | 0 … 1.65 |  |
| 26 | _Methane |  | numeric | 120 | 12 | 0 … 1.284 |  |
| 27 | _Propane |  | numeric | 120 | 4 | 0 … 2.858 |  |
| 28 | _Butane |  | numeric | 120 | 5 | 0 … 3.814 |  |
| 29 | _Ethane |  | numeric | 120 | 4 | 0 … 2.001 |  |
| 30 | _H2 |  | numeric | 120 | 10 | 0 … 1.004 |  |
| 31 | Mixture |  | numeric | 120 | 35 | 0.2622 … 1.401 | `GCF`×1 |

</details>

<details><summary>Hoja <b>Property Table</b> — encabezado fila 3, 14 filas no vacías × 14 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Fuel |  | text | 14 | 14 | Units, 1, Ethylene |  |
| 2 | _Atomic Mass |  | numeric | 11 | 11 | 2 … 58.12 | `(gram/mole) @ 298.15 Deg K, 101 Kpa (1a…`×1 |
| 3 | MolecularFormula |  | text | 12 | 12 | 5, C2H4, CH4 |  |
| 4 | <col 4> |  | text | 6 | 2 | note (1), note (1), retrieved March 30, 2020 |  |
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

</details>

<details><summary>Hoja <b>Stoich Table</b> — encabezado fila 3, 30 filas no vacías × 14 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Fuel Type |  | text | 29 | 29 | Ethylene, Methane, Hydrogen |  |
| 2 | _O2 |  | numeric | 26 | 20 | -5 … 2 |  |
| 3 | _He |  | numeric | 9 | 5 | 0.55 … 3 |  |
| 4 | _CO2 |  | numeric | 29 | 22 | 0 … 4 |  |
| 5 | _N2 |  | numeric | 14 | 6 | 0.15 … 5 |  |
| 6 | _H20 |  | numeric | 30 | 23 | 0.4 … 6 |  |
| 7 | _Ethylene |  | numeric | 2 | 2 | -0.283 … 7 |  |
| 8 | _Methane |  | numeric | 1 | 1 | 8 … 8 |  |
| 9 | _Propane |  | numeric | 2 | 2 | -0.17 … 9 |  |
| 10 | _Butane |  | numeric | 2 | 2 | -0.131 … 10 |  |
| 11 | _Ethane |  | numeric | 2 | 2 | -0.243 … 11 |  |
| 12 | _H2 |  | numeric | 1 | 1 | 12 … 12 |  |
| 13 | _Fuel |  | numeric | 1 | 1 | 13 … 13 |  |
| 14 | <col 14> |  | text | 29 | 29 | Ethylene:  C2H4   →   - 3 O2  +  2 H2O …, Methane:  CH4   →   -  2 O2  +  2 H2O  …, Hydrogen:  2 H2   →   -  O2  +  2 H2O |  |

</details>

<details><summary>Hoja <b>Mass Fraction Table</b> — encabezado fila 4, 34 filas no vacías × 28 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | 1st component |  | numeric | 27 | 8 | 0.25 … 1 |  |
| 2 | 2nd component |  | numeric | 27 | 8 | 0 … 0.75 |  |
| 3 | 1st component |  | numeric | 27 | 11 | 0.688 … 0.8622 |  |
| 4 | 2nd component |  | numeric | 17 | 9 | 0.688 … 1.261 |  |
| 5 | <col 5> |  | text | 34 | 30 | Decane, Decane / Propylbenzene (25/75), Decane / Propylbenzene (50/50) |  |
| 6 | RESERVED |  | empty | 0 | 0 |  |  |
| 7 | RESERVED |  | empty | 0 | 0 |  |  |
| 8 | RESERVED |  | empty | 0 | 0 |  |  |
| 9 | RESERVED |  | empty | 0 | 0 |  |  |
| 10 | RESERVED |  | empty | 0 | 0 |  |  |
| 11 | RESERVED |  | empty | 0 | 0 |  |  |
| 12 | RESERVED |  | empty | 0 | 0 |  |  |
| 13 | _Decane |  | numeric | 5 | 5 | 0.2195 … 1 |  |
| 14 | _Ethanol |  | numeric | 2 | 2 | 0.5297 … 1 |  |
| 15 | _Dodecane |  | numeric | 4 | 4 | 0.4 … 1 |  |
| 16 | _Farnesane |  | numeric | 1 | 1 | 1 … 1 |  |
| 17 | _Isododecane |  | numeric | 3 | 3 | 0.25 … 0.6 |  |
| 18 | _Glycerol |  | numeric | 2 | 2 | 0.07634 … 0.2819 |  |
| 19 | _Hexadecane |  | numeric | 2 | 2 | 0.05468 … 0.2155 |  |
| 20 | _Iso_Octane |  | numeric | 4 | 4 | 0.2466 … 1 |  |
| 21 | _Propanol |  | numeric | 2 | 2 | 0.7181 … 0.9237 |  |
| 22 | _Propylbenzene |  | numeric | 4 | 4 | 0.2832 … 1 |  |
| 23 | _Hexanol |  | numeric | 1 | 1 | 0.5278 … 0.5278 |  |
| 24 | _Octane |  | numeric | 2 | 2 | 0.4992 … 1 |  |
| 25 | _Toluene |  | numeric | 2 | 2 | 0.5517 … 1 |  |
| 26 | _Heptane |  | numeric | 9 | 9 | 0.2534 … 1 |  |
| 27 | _Methanol |  | numeric | 1 | 1 | 1 … 1 |  |
| 28 | <col 28> |  | numeric | 27 | 2 | 1 … 1 |  |

</details>

<details><summary>Hoja <b>Equations & Constants</b> — encabezado fila 2, 112 filas no vacías × 20 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | <col 1> |  | text | 4 | 4 | Defined Name: Column/Cell Refernces, Defined Name: Tables, Defined Name: Procedures |  |
| 2 | Chamber Volume |  | text | 76 | 24 | TYPE, SID, FuelType |  |
| 3 | _Vc |  | text | 73 | 71 | =EventData!C3, =EventData!RC28, =Sources!C3:C13 |  |
| 4 | 88 |  | text | 15 | 12 | ID for source used to modify the chambe…, Where:, R |  |
| 5 | Liters |  | text | 14 | 12 | R, 8.314462618, = 32 DegF |  |
| 6 | <col 6> |  | mixed | 18 | 18 | 0.9829 … 8314 | `m3 Pa K-1 mol-1`×1, `n is # of moles`×1, `P is in (Pa)`×1, `V is in m3`×1, `T is in Kelvin`×1, `=760 torr`×1 |
| 7 | <col 7> |  | text | 12 | 6 | 8.314 462 618, Vm = 22.41397, standard liter gas per mole |  |
| 8 | <col 8> |  | text | 3 | 3 | J mol-1 K-1, m3 Pa K-1 mol-1, L Pa K-1 mol-1 |  |
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

</details>

<details><summary>Hoja <b>Pick List</b> — encabezado fila 1, 36 filas no vacías × 9 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | PickOp |  | text | 25 | 9 | Cabin Air, Vent, O2 Fill |  |
| 2 | Type |  | text | 25 | 6 | Set, Vent, Add |  |
| 3 | PickDiluent |  | text | 2 | 2 | No Bottle Installed, 67212MFAM70100 |  |
| 4 | PickOxygen |  | text | 4 | 4 | No Bottle Installed, 67212MFAM70001, 67212MFAM70002 |  |
| 5 | PickFuel |  | text | 2 | 2 | No Bottle Installed, 67212MFAM70300 |  |
| 6 | PickIgnition |  | text | 2 | 2 | Yes, No |  |
| 7 | <col 7> |  | empty | 0 | 0 |  |  |
| 8 | FuelBottles |  | numeric | 22 | 22 | 2022 … 2050 |  |
| 9 | <col 9> |  | text | 22 | 4 | Ethylene, Propane, Butane |  |

</details>

<details><summary>Hoja <b>Hastings GCF</b> — encabezado fila 5, 195 filas no vacías × 17 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Rec # |  | numeric | 194 | 194 | 1 … 194 |  |
| 2 | Gas |  | text | 192 | 192 | Acetic Acid, Acetic Acid, Anhydride, Acetone |  |
| 3 | Symbol |  | text | 192 | 159 | C2H4F2, C4H6O3, C3H6O |  |
| 4 | GCF |  | numeric | 193 | 184 | 0.1224 … 1.405 | `(NIST)`×1, `NA`×1 |
| 5 | Derived |  | numeric | 192 | 5 | 1 … 5 | `NA`×1 |
| 6 | Density (g/L) | g/L | numeric | 193 | 159 | 0.0824 … 14.39 | `25° C / 1 atm`×1, `NA`×1 |
| 7 | <col 7> |  | text | 194 | 1 | - |  |
| 8 | Density (g/L) | g/L | numeric | 193 | 159 | 0.08994 … 15.71 | `0° C / 1 atm`×1, `NA`×1 |
| 9 | <col 9> |  | text | 194 | 1 | - |  |
| 10 | Synonyms |  | text | 192 | 105 | Ethanoic Acid, Aceticanhydride, 2-propanone |  |
| 11 | Gamma |  | numeric | 193 | 16 | 1.09 … 1.66 | `(Cp/Cv)25`×1 |
| 12 | R |  | numeric | 193 | 159 | 23.62 … 4125 | `J/gm*K`×1, `NA`×1 |
| 13 | <col 13> |  | empty | 0 | 0 |  |  |
| 14 | Derived |  | mixed | 6 | 5 | 3 … 5 | `Derived`×2, `SUM`×1 |
| 15 | <col 15> |  | numeric | 4 | 4 | 0 … 191 |  |
| 16 | <col 16> |  | empty | 0 | 0 |  |  |
| 17 | <col 17> |  | numeric | 1 | 1 | 5 … 5 |  |

</details>

<details><summary>Hoja <b>Changelog</b> — encabezado fila 2, 98 filas no vacías × 4 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Completed |  | datetime | 19 | 13 | 2017-10-13T00:00:00, 2018-07-27T00:00:00, 2019-03-27T00:00:00 |  |
| 2 | Request |  | text | 98 | 98 | Created version for ACME based on MDCA …, Added bottles from OA-9, SpX-15, Correc…, Corrected Stoic Table for 100% ethylene… |  |
| 3 | <col 3> |  | text | 78 | 78 | =SourceTable!$L$3, =SourceTable!$F$3, =EventData!B$1 |  |
| 4 | <col 4> |  | empty | 0 | 0 |  |  |

</details>

### Publicaciones con DOI (primeras 8)

- The kinetics and warm flame chemistry associated with radiative extinction of spherical diffusion flames — doi:10.1080/13647830.2024.2326830
- Soot Formation in Spherical Diffusion Flames — doi:10.3390/math11020261
- On the existence of steady-state gaseous microgravity spherical diffusion flames in the presence of radiation heat loss — doi:10.1016/j.proci.2022.07.049
- Critical temperature and reactant mass flux for radiative extinction of ethylene microgravity spherical diffusion flames at 1 bar — doi:10.1016/j.proci.2022.07.043
- An investigation of thermal radiation from laminar diffusion flames in a tri-coflow burner with central oxygen — doi:10.1016/j.combustflame.2022.112158
- SPHERICAL DIFFUSION FLAME IN MICROGRAVITY CONDITIONS: FIRST RESULTS OF JOINT RUSSIAN-AMERICAN SPACE EXPERIMENT FLAME DESIGN - ADAMANT — doi:10.30826/nepcap9b-13
- Observations of long duration microgravity spherical diffusion flames aboard the International Space Station — doi:10.1016/j.combustflame.2021.02.019
- Double blue zones in inverse and normal laminar jet diffusion flames — doi:10.1016/j.combustflame.2019.09.014

<!-- AUTO:END -->

## Evaluación (manual — DE/PHY)

> Primera pasada DE-04 (2026-11-14) basada en el bloque automático y en las muestras L2. La clasificación
> Medida / Calculada / Log es **propuesta DE — pendiente de validación PHY (PHY-02)**.

### Resumen propio
ACME Flame Design: llamas esféricas de etileno y propano, normales e inversas, con XO₂ de 0.20–0.40 (normal) y 0.21–0.85
(inversa) y presión de 0.42–3 atm (inversa). Estudia la extinción radiativa y el diseño de llamas con hollín y sin hollín.

### Granularidad y variables clave
| Archivo | Fila = … | Condición | Resultado (medido) | Calculadas | Notas |
|---|---|---|---|---|---|
| ET Normal (207) / Inverse (120) | 1 prueba | XO₂, Xfuel, caudales (mg/s), p inicial/final/media | **ninguno en la tabla** | `mean Zst`, `Tad` | `RAMP`/`RAMPED`/`LOW O2` dentro de columnas numéricas |
| Chamber Calculator `EventData` (350) | 1 evento de cámara (TP, Add, Vent…) | composición de gases por etapa, P inicio/fin (psia) | **`Ignite` Sí/No** (192/31 en eventos TP), `Burn Fraction` | fracciones de composición | une con ET por `TPID` = `Test` |
| Raw `*_data.csv` | muestra temporal | MFC | radiómetros, PMT, termopares, corriente iónica | — | preámbulo de metadatos |

### Problemas de calidad / acceso
- La tabla experimental **no trae resultado**. El resultado de ignición está en el Chamber Calculator (2 archivos) y hay que unirlo por ID.
- Los tokens `RAMP`/`RAMPED` (60 filas normales) y `RAMP`/`LOW O2` (11 inversas) son calificadores, no faltantes: van a una columna `__flag`.
- La licencia está vacía en el registro (los demás son CC0).

### Valor para el proyecto
- **Pilar:** prevención. **Entornos:** base lunar y Marte (O₂ alto, presión variable).
- **RQ:** RQ1 y M1, solo si se une con `EventData` (ignición). Sin esa unión solo sirve para describir condiciones.
- **Triage (borrador):** R1 3 · R2 3 · R3 2 · R4 2 (3 con EventData) · R5 3 · R6 3 → **Tier 1** si la unión funciona; si no, Tier 2.
