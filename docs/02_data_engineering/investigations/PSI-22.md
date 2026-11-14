# PSI-22 — ACME E-FIELD Flames · Advanced Combustion via Microgravity Experiments Electric-Field Effects on Laminar Diffusion Flames

<!-- AUTO:BEGIN — generado por `flamesafe profile`; no editar a mano dentro de este bloque -->

| Campo | Valor (PSI) |
|---|---|
| DOI de datos | 10.60555/se5a-8c73 |
| Tipo | Microgravity Investigation |
| Sub-área | Laminar Flames |
| Programa / plataforma | International Space Station (ISS) / International Space Station (ISS) |
| Hardware | Combustion Integrated Rack (CIR), ACME |
| Centro | Glenn Research Center (GRC) |
| Periodo | 2016-11-18 → 2020-11-17 |
| Licencia | Creative Commons Zero v1.0 Universal |
| Investigaciones relacionadas | PSI-23 |
| Snapshot | snapshot_2026-11-14 |

### Inventario (L1)

| Archivos `added` | Tablas exp. (fuera de `added`) | `removed` | Publicaciones (con DOI) | GB expuestos | GB registrados | Acceso |
|---:|---:|---:|---:|---:|---:|---|
| 0 | 1 (1) | 0 | 25 (22) | 0.00 | 950.21 | `experimental_table_only` |

**Objetivo (texto PSI):**

> The objective of this investigation is to better understand the relationship between electric field voltage and chemi-ion current, analyze the dynamic response of flames to electric field changes, evaluate soot formation, and characterize stabilized near-limit lifted flames.

**Hipótesis (texto PSI):**

> The application of electric fields in microgravity environments will significantly influence laminar diffusion flames by enabling precise manipulation of flame stability, soot behavior, and combustion dynamics through ion-driven convection and chemi-ionization processes.

### Archivos perfilados (L2)

#### `PSI-22_Experimental table_ACME E-FIELD Flames.csv`

- Lista: `experimentalTable` · 2,475 bytes · sha256 `69090c357b83ae38…` · HTTP 200
- CSV · encoding `utf-8` · delimitador `,` · encabezado en fila 1 · filas no vacías **32** / físicas 32 · **10** columnas · bloques lado a lado: 1

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Test Type |  | text | 21 | 2 | First round of tests with coflow burner, Second round of tests with gas-jet burn… |  |
| 2 | Test Day |  | numeric | 21 | 20 | 1.807e+04 … 1.832e+04 |  |
| 3 | Year |  | numeric | 21 | 1 | 2018 … 2018 |  |
| 4 | Month |  | numeric | 21 | 6 | 3 … 11 |  |
| 5 | Date |  | numeric | 21 | 18 | 1 … 29 |  |
| 6 | Mesh Polarity |  | text | 21 | 2 | negative, positive |  |
| 7 | Fuel Bottle |  | text | 21 | 4 | 100% CH4, 40% CH4, 100% C2H4 |  |
| 8 | Fuel Conc |  | text | 32 | 7 | 100%, 70%, 40% |  |
| 9 | Flames Ignited |  | numeric | 21 | 7 | 8 … 15 |  |
| 10 | Notes |  | text | 4 | 4 | Test day is formatted YYDDD where YY id…, Mesh polarity refers to the polarity of…, Fuel Conc. (diluted with nitrogen on a … |  |

### Publicaciones con DOI (primeras 8)

- Electric Field Induced Changes of a Diffusion Flame and Heat Transfer near an Impinging Surface — doi:10.3390/en11051235
- Ionization and chemiluminescence during the progressive aeration of methane flames — doi:10.1016/j.combustflame.2009.08.008
- Modelling electric field driven convection in small combustion plasmas and surrounding gases — doi:10.1080/13647830701383814
- Canceling buoyancy of gaseous fuel flames in a gravitational environment using an ion-driven wind. — doi:10.1196/annals.1362.038
- Detailed characterization of DC electric field effects on small non-premixed flames — doi:10.1016/j.combustflame.2015.03.019
- Microgravity burner-generated spherical diffusion flames: experiment and computation. Currently at Department of Mechanical and Aerospace Engineering, Case Western Reserve University, Cleveland, OH 44106. — doi:10.1016/s0010-2180(01)00247-4
- PLIF and chemiluminescence in a small laminar coflow methane-air diffusion flame at elevated pressures — doi:10.1016/j.combustflame.2022.112067
- Ion current and carbon monoxide release from an impinging methane/air coflow flame in an electric field — doi:10.1016/j.combustflame.2019.03.022

<!-- AUTO:END -->

## Evaluación (manual — DE/PHY)

> Primera pasada DE-04 (2026-11-14) basada en el bloque automático y en las muestras L2. La clasificación
> Medida / Calculada / Log es **propuesta DE — pendiente de validación PHY (PHY-02)**.

### Evaluación breve (contexto)
ACME E-FIELD Flames: ET de 32 filas por día de prueba (polaridad de malla, combustible); `experimental_table_only`. Es relevante como **proxy de gravedad parcial** (el campo eléctrico imita la flotabilidad) para la narrativa y el ranking. **Tier 3** (contexto PHY).
