# PSI-21 — ACME CLD Flame · Advanced Combustion via Microgravity Experiments / Coflow Laminar Diffusion Flame

<!-- AUTO:BEGIN — generado por `flamesafe profile`; no editar a mano dentro de este bloque -->

| Campo | Valor (PSI) |
|---|---|
| DOI de datos | 10.60555/23e1-9950 |
| Tipo | Microgravity Investigation |
| Sub-área | Flames of gaseous fuel |
| Programa / plataforma | International Space Station (ISS) / International Space Station (ISS) |
| Hardware | Combustion Integrated Rack (CIR), ACME |
| Centro | Glenn Research Center (GRC) |
| Periodo | 2006-10-01 → 2022-05-31 |
| Licencia | Creative Commons Zero v1.0 Universal |
| Investigaciones relacionadas | — |
| Snapshot | snapshot_2026-11-14 |

### Inventario (L1)

| Archivos `added` | Tablas exp. (fuera de `added`) | `removed` | Publicaciones (con DOI) | GB expuestos | GB registrados | Acceso |
|---:|---:|---:|---:|---:|---:|---|
| 1 | 1 (0) | 0 | 18 (18) | 0.00 | 2,005.54 | `available` |

Categorías: Experimental table 1.0 (0.00 GB)
Extensiones: `.csv` 1

**Objetivo (texto PSI):**

> In order to provide the experimental data needed to allow rigorous testing of computational models at the extremes of the fuel dilution spectrum, we have the following objectives: A) Characterize the behavior of weak coflow diffusion flames of methane and ethylene, as a function of velocity and fuel dilution, through measurement of flame shape, lift-off heights, temperatures and extinction limits. B) Characterize the sooting tendencies of diffusion flames with long residence times, as a function of velocity and fuel dilution, through measurement of flame shape, gas temperatures in the soot-free portion of the flame, soot luminosity, soot temperatures, and soot volume fractions.

**Hipótesis (texto PSI):**

> This investigation was focused on gathering bench mark data to validate the hypothesis of computation models, the details of which are available within the following publications:      1)  Smooke, M.D., Hall, R.J., Colket, M.B., Fielding, J., Long, M.B., McEnally, C.S., and Pfefferle, L.D., Investigation of the transition from lightly sooting towards heavily sooting co-flow ethylene diffusion   flames. Combustion Theory and Modelling, 2004. 8(3): p. 593-606. https://doi.org/10.1088/1364-7830/8/3/009     2)  Luque, J., Jeffries, J.B., Smith, G.P., Crosley, D.R., Walsh, K.T., Long, M.B., and Smooke, M.D., CH(A-X) and OH(A-X) optical emission in an axisymmetric laminar diffusion flame. …

### Archivos perfilados (L2)

#### `PSI-21_Experimental table_CLD Flame.csv`

- Lista: `experimentalTable` · 2,454 bytes · sha256 `9fafbc5b3dddaf71…` · HTTP 200
- CSV · encoding `utf-8` · delimitador `,` · encabezado en fila 1 · filas no vacías **32** / físicas 32 · **8** columnas · bloques lado a lado: 1

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Test Type |  | text | 32 | 3 | Methane based test, Ethylene based test, Improved coflow tests |  |
| 2 | Test Day |  | numeric | 32 | 32 | 1.732e+04 … 2.106e+04 |  |
| 3 | Fuel MFC |  | numeric | 32 | 2 | 0.1 … 0.2 |  |
| 4 | N2 MFC |  | numeric | 32 | 4 | 0.02 … 0.2 |  |
| 5 | Fuel Bottle |  | text | 32 | 30 | 40% CH4, 40% CH5, 40% CH6 |  |
| 6 | Fuel conc. Range |  | text | 32 | 18 | 30%-40%, 40%, 25%-40% |  |
| 7 | Flames ignited |  | numeric | 32 | 15 | 2 … 18 |  |
| 8 | Notes |  | text | 1 | 1 | Test Day - includes the year as the fir… |  |

### Publicaciones con DOI (primeras 8)

- Analysis of CH* concentration and flame heat release rate in laminar coflow diffusion flames under microgravity and normal gravity — doi:10.1016/j.combustflame.2016.02.012
- Signal-to-noise ratio improvements in laser flow diagnostics using time-resolved image averaging and high dynamic range imaging — doi:10.1007/s00348-016-2218-5
- A computational and experimental study of coflow laminar methane/air diffusion flames: Effects of fuel dilution, inlet velocity, and gravity — doi:10.1016/j.proci.2014.05.138
- A Combined Experimental and Computational Study of Soot Formation in Normal and Microgravity Conditions — doi:10.1080/00102202.2022.2041621
- Constrained-temperature solutions of coflow laminar diffusion flames — doi:10.1016/j.proci.2020.06.034
- Effects of pressure and fuel dilution on coflow laminar methane–air diffusion flames: A computational and experimental study — doi:10.1080/13647830.2017.1403051
- Effect of soot self-absorption on color-ratio pyrometry in laminar coflow diffusion flames — doi:10.1364/ol.43.001103
- A computational and experimental study of coflow laminar methane/air diffusion flames: Effects of fuel dilution, inlet velocity, and gravity — doi:10.1016/j.proci.2014.05.138

<!-- AUTO:END -->

## Evaluación (manual — DE/PHY)

> Primera pasada DE-04 (2026-11-14) basada en el bloque automático y en las muestras L2. La clasificación
> Medida / Calculada / Log es **propuesta DE — pendiente de validación PHY (PHY-02)**.

### Evaluación breve (contexto)
ACME CLD Flame: ET de 32 filas por día de prueba, con rangos de concentración como texto. Sin resultados medidos. **Tier 3.**
