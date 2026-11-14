# PSI-20 — ACME BRE · Advanced Combustion via Microgravity Experiments - Burning Rate Emulator

<!-- AUTO:BEGIN — generado por `flamesafe profile`; no editar a mano dentro de este bloque -->

| Campo | Valor (PSI) |
|---|---|
| DOI de datos | 10.60555/vb93-3y72 |
| Tipo | Microgravity Investigation |
| Sub-área | Flames of Gaseous Fuels |
| Programa / plataforma | International Space Station (ISS) / International Space Station (ISS) |
| Hardware | Combustion Integrated Rack (CIR), ACME |
| Centro | Glenn Research Center (GRC) |
| Periodo | 2010-01-01 → 2025-02-08 |
| Licencia | Creative Commons Zero v1.0 Universal |
| Investigaciones relacionadas | — |
| Snapshot | snapshot_2026-11-14 |

### Inventario (L1)

| Archivos `added` | Tablas exp. (fuera de `added`) | `removed` | Publicaciones (con DOI) | GB expuestos | GB registrados | Acceso |
|---:|---:|---:|---:|---:|---:|---|
| 1 | 1 (0) | 0 | 16 (15) | 0.00 | 2,035.57 | `available` |

Categorías: Experimental table 1.0 (0.00 GB)
Extensiones: `.csv` 1

**Objetivo (texto PSI):**

> The BRE flight program seeks to establish the burning conditions in a quiescent microgravity ambient in terms of material properties. The specific flight objectives are as follows.   1. Observe burning behavior in long-duration microgravity for CH4/N2 and C2H4/N2mixtures on porous circular burners of 25  and 50 mm diameter. Consider O2/N2 ambients with various pressures and ambient O2 concentrations and pressures. NASA - considered atmosphere for human space missions will be examined: 14.7 psia, 21 % oxygen: 10.2 psia, 26.5 %; and 8.2 psia, 34 % oxygen. Emphasize fuel conditions that can be related to a diverse range of condensed fuels.   2. Consider the conditions of Objective 1 for …

**Hipótesis (texto PSI):**

> The BRE investigation hypothesizes that there can exist a regime of quasi-steady burning in microgravity as a function of materials properties. Steady burning may never be achieved, and only slowly changing unsteady flames are possible. The proposed tests aboard the ISS aims to query this hypothesis by establishing a range of quasi-steady burning conditions for condensed fuels in the microgravity environment. It is hypothesized that BRE can determine a range of burning conditions in microgravity as a function of heat of gasification, reradiation heat flux, applied radiant heat flux, heat of combustion and smoke point. This could enable the Cone Calorimeter (NASA Test 2) test as a basis for …

### Archivos perfilados (L2)

#### `PSI-20_Experimental table_ACME BRE.csv`

- Lista: `experimentalTable` · 1,113 bytes · sha256 `4aa5d3f98708ceac…` · HTTP 200
- CSV · encoding `utf-8` · delimitador `,` · encabezado en fila 1 · filas no vacías **18** / físicas 18 · **8** columnas · bloques lado a lado: 1

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Year |  | numeric | 18 | 3 | 2019 … 2021 |  |
| 2 | Month |  | text | 18 | 7 | Feb, March, April |  |
| 3 | Date |  | numeric | 18 | 12 | 1 … 28 |  |
| 4 | Burner Size (mm) | mm | numeric | 18 | 2 | 25 … 50 |  |
| 5 | Fuel Bottle |  | text | 18 | 4 | 100% C2H4, 50% C2H4, 100%C2H4 |  |
| 6 | Oxygen Conc (percent) | percent | text | 18 | 10 | 21; 26.5; 40, 26.5; 34, 21; 26.5; 34; 40 |  |
| 7 | Flames Ignited |  | numeric | 18 | 12 | 0 … 21 |  |
| 8 | Notes |  | text | 2 | 2 | Oxygen Conc. (as diluted with nitrogen …, Flames Ignited is the number ignited on… |  |

### Publicaciones con DOI (primeras 8)

- Burning on flat wicks at various orientations — doi:10.1177/0734904113495650
- A Gas Burner to Emulate Condensed-Phase Burning — doi:10.3850/978-981-07-5936-0_03-01
- Burning in microgravity: Experimental results and analysis — doi:10.1016/j.combustflame.2021.01.035
- Transient dynamics of radiative extinction in low-momentum microgravity diffusion flames — doi:10.1016/j.proci.2020.06.110
- Emulation of condensed fuel flames with gaseous fuels supplied through a porous copper calorimeter — doi:10.1002/fam.2896
- Radiative Extinction of Laminar Diffusion Flame above the Flat Porous Burner in Microgravity: A Computational Study — doi:10.1134/s0010508220040036
- Transient ellipsoidal combustion model for a porous burner in microgravity — doi:10.1016/j.combustflame.2019.09.030
- Measuring heat flux to a porous burner in microgravity — doi:10.1016/j.proci.2018.05.006

<!-- AUTO:END -->

## Evaluación (manual — DE/PHY)

> Primera pasada DE-04 (2026-11-14) basada en el bloque automático y en las muestras L2. La clasificación
> Medida / Calculada / Log es **propuesta DE — pendiente de validación PHY (PHY-02)**.

### Evaluación breve (contexto)
ACME BRE (emulador de tasa de quemado): ET de 18 filas **por día de prueba**. El O₂ viene como lista en una celda ("21; 26.5; 40") y la presión no está identificada (lo dice la propia nota). Contexto de materiales. **Tier 3.**
