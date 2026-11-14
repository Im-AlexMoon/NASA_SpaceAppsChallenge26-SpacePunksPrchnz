# PSI-23 — ACME s-Flame · Advanced Combustion via Microgravity Experiments-Structure and Response of Spherical Diffusion Flames

<!-- AUTO:BEGIN — generado por `flamesafe profile`; no editar a mano dentro de este bloque -->

| Campo | Valor (PSI) |
|---|---|
| DOI de datos | 10.60555/k57n-p030 |
| Tipo | Microgravity Investigation |
| Sub-área | Flames of gaseous fuels |
| Programa / plataforma | International Space Station (ISS) / International Space Station (ISS) |
| Hardware | Combustion Integrated Rack (CIR), ACME |
| Centro | Glenn Research Center (GRC) |
| Periodo | 2015-02-05 → 2019-11-24 |
| Licencia | Creative Commons Zero v1.0 Universal |
| Investigaciones relacionadas | — |
| Snapshot | snapshot_2026-11-14 |

### Inventario (L1)

| Archivos `added` | Tablas exp. (fuera de `added`) | `removed` | Publicaciones (con DOI) | GB expuestos | GB registrados | Acceso |
|---:|---:|---:|---:|---:|---:|---|
| 4,163 | 1 (1) | 6,814 | 44 (37) | 782.17 | 782.17 | `available` |

Categorías: Raw Data 4,058.0 (780.80 GB) · Reference Data 50.0 (1.12 GB) · Engineering Documents 29.0 (0.19 GB) · Presentations 17.0 (0.05 GB) · Science Documents 7.0 (0.01 GB) · Reports 2.0 (0.00 GB)
Extensiones: `.zip` 2,037 · `.txt` 963 · `.csv` 576 · `.mp4` 290 · `.asc` 170 · `.log` 68 · `.pdf` 38 · `.mdipsug` 16

**Objetivo (texto PSI):**

> A series of experiments is proposed with the following specific objectives, in both soot-free and sooty flames, to compare with detailed computational simulation to assess transport properties and detailed chemical kinetics (including chemiluminescence):     Objective A. Measure and characterize the transient structure (such as temperature and species distribution) of diffusion flames established at initially non-steady, spherical flame structures for mixtures of different H2/CH4/diluent ratios   (soot-free) and different C2H4/diluent ratios (sooty), for different flow rates.     Objective B. Determine the quasi-steady convective/chemical-kinetic extinction limits (low system Damköhler …

**Hipótesis (texto PSI):**

> The transient numerical simulation of spherical flames developed as part of this program includes detailed chemistry and transport models, especially radiation mechanisms. Each description of the flames obtained from the experiment, including measurements of aspects of the flame structure, growth or flame front velocities, and the specific test conditions where steady state flames, flame extinctions, flame front instabilities, soot suppression limits, etc., comprise a rigorous test of the detailed model. Together they provide a measure of the comprehensiveness of the chemical kinetic and transport models. The numerical simulation is also being used as a predictive tool to develop the …

### Archivos perfilados (L2)

#### `PSI-23_Experimental table_ACME s-Flame.csv`

- Lista: `experimentalTable` · 2,456 bytes · sha256 `16cd10f50bd2e962…` · HTTP 200
- CSV · encoding `utf-8` · delimitador `,` · encabezado en fila 1 · filas no vacías **18** / físicas 18 · **9** columnas · bloques lado a lado: 1

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Test Type |  | text | 18 | 2 | First round of tests with nitrogen-dilu…, Second round of tests with helium-dilut… |  |
| 2 | Test Day* |  | numeric | 18 | 18 | 1.925e+04 … 2.019e+04 |  |
| 3 | Year |  | numeric | 18 | 2 | 2019 … 2020 |  |
| 4 | Month |  | text | 18 | 8 | Sept., Oct., Nov. |  |
| 5 | Date |  | numeric | 18 | 13 | 3 … 31 |  |
| 6 | Atmosphere* |  | text | 18 | 9 | ~21% O2 with N2, ~21% O2 with N3, ~21% O2 with N4 |  |
| 7 | Fuel Bottle |  | text | 18 | 16 | 50% C2H4 with N2, 50% C2H4 with N3, 45% CH4 with N2 |  |
| 8 | Flames Ignited* |  | numeric | 18 | 12 | 7 … 23 |  |
| 9 | Notes |  | text | 3 | 3 | *Test Day is formatted YYDDD where YY i…, *Atmosphere is ~1 atm but pressure incr…, *Flames Ignited is the number ignited o… |  |

#### `PSI-23_Raw Data_ACME Daily Test Point Log 1.xlsx`

- Lista: `added` · 127,261 bytes · sha256 `173dc8ec7d15d5d9…` · HTTP 200
- XLSX · **2** hojas

<details><summary>Hoja <b>ACME</b> — encabezado fila 2, 27 filas no vacías × 12 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Test Point Name (enter all test points) | enter all test points | text | 1 | 1 | PD: |  |
| 2 | Script Aborts Before IPSUs Open |  | text | 1 | 1 | ____________________________________ |  |
| 3 | IPSU1/HiBMS |  | text | 1 | 1 | Archived Images |  |
| 4 | <col 4> |  | text | 26 | 2 | D/L?, False |  |
| 5 | ACME Camera |  | text | 1 | 1 | Archived Images |  |
| 6 | <col 6> |  | text | 27 | 3 | D/L?, False, Date: |  |
| 7 | Intensified Camera |  | text | 2 | 2 | Archived Images, __________________ |  |
| 8 | <col 8> |  | text | 26 | 2 | D/L?, False |  |
| 9 | <col 9> |  | numeric | 26 | 2 | 0 … 0 | `IPSU1 data`×1 |
| 10 | <col 10> |  | numeric | 26 | 2 | 0 … 0 | `ACME data`×1 |
| 11 | <col 11> |  | numeric | 26 | 2 | 0 … 0 | `Intens data`×1 |
| 12 | Downlink Data (MB) | MB | numeric | 25 | 1 | 0 … 0 |  |

</details>

<details><summary>Hoja <b>WITH IPSU2</b> — encabezado fila 2, 27 filas no vacías × 17 columnas</summary>

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Test Point Name (enter all test points) | enter all test points | text | 26 | 26 | 20164A1, 20164A2, 20164B1 |  |
| 2 | Script Aborts Before IPSUs Open |  | text | 1 | 1 | ____________________________________ |  |
| 3 | IPSU1/HiBMS |  | numeric | 26 | 25 | 333 … 656 | `Archived Images`×1 |
| 4 | <col 4> |  | text | 25 | 3 | D/L?, True, False |  |
| 5 | IPSU2/LLL-UV |  | numeric | 26 | 25 | 25 … 656 | `Archived Images`×1 |
| 6 | <col 6> |  | text | 26 | 3 | D/L?, True, False |  |
| 7 | ACME Camera |  | numeric | 26 | 21 | 144 … 204 | `Archived Images`×1 |
| 8 | <col 8> |  | text | 27 | 4 | D/L?, True, False |  |
| 9 | Intensified Camera |  | numeric | 27 | 27 | 517 … 888 | `Archived Images`×1, `__________________`×1 |
| 10 | <col 10> |  | text | 26 | 3 | D/L?, True, False |  |
| 11 | <col 11> |  | numeric | 26 | 16 | 0 … 1376 | `IPSU1 data`×1 |
| 12 | <col 12> |  | numeric | 26 | 16 | 0 … 344 | `IPSU2 data`×1 |
| 13 | <col 13> |  | numeric | 26 | 15 | 0 … 569.5 | `ACME data`×1 |
| 14 | <col 14> |  | numeric | 26 | 16 | 0 … 2575 | `Intens data`×1 |
| 15 | Downlink Data (MB) | MB | numeric | 25 | 15 | 0 … 4687 |  |
| 16 | <col 16> |  | empty | 0 | 0 |  |  |
| 17 | <col 17> |  | empty | 0 | 0 |  |  |

</details>

### Publicaciones con DOI (primeras 8)

- Opportunities and challenges of combustion in microgravity — doi:10.1016/0360-1285(94)90006-x
- On burner-stabilized cylindrical premixed flames in microgravity — doi:10.1016/s0082-0784(06)80819-2
- On the structure, stabilization, and dual response of flat-burner flames — doi:10.1016/0010-2180(94)00102-x
- Extinction mechanisms of near-limit premixed flames and extended limits of flammability — doi:10.1016/s0082-0784(96)80296-7
- On the spreading of unsteady cylindrical diffusion flames — doi:10.1016/s0010-2180(97)00069-2
- On the response of spherical premixed flames under rotation — doi:10.1016/s0010-2180(97)00051-5
- Role of flamefront motion and criterion for global quasi-steadiness in droplet burning — doi:10.1016/s0082-0784(98)80038-6
- On micro-buoyancy spherical diffusion flames and a double luminous zone structure of the hydrogen/methane flame — doi:10.1016/s0082-0784(98)80108-2

<!-- AUTO:END -->

## Evaluación (manual — DE/PHY)

> Primera pasada DE-04 (2026-11-14) basada en el bloque automático y en las muestras L2. La clasificación
> Medida / Calculada / Log es **propuesta DE — pendiente de validación PHY (PHY-02)**.

### Resumen propio
ACME s-Flame: llamas esféricas de etileno y metano diluidos. Tiene un archivo crudo grande (4,163 archivos).

### Variables clave
ET (18) = resumen por día de prueba (atmósfera aproximada "~21% O₂", botella de combustible, llamas encendidas). El
`Daily Test Point Log` (27 filas por hoja) da puntos de prueba. **No hay resultados medidos en tablas.**

### Valor para el proyecto
- **RQ:** ninguna directa en el MVP. **Triage (borrador):** R1 2 · R2 2 · R3 1 · R4 1 · R5 2 · R6 2 → **Tier 3**.
