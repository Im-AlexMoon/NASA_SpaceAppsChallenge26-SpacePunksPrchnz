# PSI-68 — FLEX-2 · Flame Extinguishment Experiment - 2

<!-- AUTO:BEGIN — generado por `flamesafe profile`; no editar a mano dentro de este bloque -->

| Campo | Valor (PSI) |
|---|---|
| DOI de datos | 10.60555/byp8-h018 |
| Tipo | Microgravity Investigation |
| Sub-área | Spacecraft Fire Safety |
| Programa / plataforma | International Space Station (ISS) / International Space Station (ISS) |
| Hardware | Combustion Integrated Rack (CIR), Multi-user Droplet Combustion Appartatus (MDCA) |
| Centro | Glenn Research Center (GRC) |
| Periodo | 2016-08-12 → 2019-09-30 |
| Licencia | Creative Commons Zero v1.0 Universal |
| Investigaciones relacionadas | — |
| Snapshot | snapshot_2026-11-14 |

### Inventario (L1)

| Archivos `added` | Tablas exp. (fuera de `added`) | `removed` | Publicaciones (con DOI) | GB expuestos | GB registrados | Acceso |
|---:|---:|---:|---:|---:|---:|---|
| 0 | 1 (1) | 0 | 48 (36) | 0.00 | 1,224.75 | `experimental_table_only` |

**Objetivo (texto PSI):**

> The primary goal of the FLEX-2 flight experiments is to extend the results of FLEX-1 to fuels and environmental conditions that mimic real combustor conditions, as well as, provide benchmark experimental data on bi-component droplet combustion over a wide range of initial conditions in order to validate numerical simulations and to develop new theoretical models.  Detailed experimental objectives can be further itemized as:   1. Investigate the role of liquid-phase mixing on the burning characteristics of bi-component fuel droplets.   2. Examine the steady and unsteady liquid and gas-phase phenomena in pure fuel combustion.   3. Study flame extinction mechanisms and their boundaries.   4. …

**Hipótesis (texto PSI):**

> Fairly sophisticated numerical simulations of convective droplet combustion have been developed in the last decade where the key contribution is the inclusion of full Navier-Stokes equations for the gas-phase flow field. However, due to the inherent complexity of the problem, varying degrees of approximations have been made in treating the chemistry, radiation, and the coupling between the gas and liquid phases. The validity of the assumptions or the hypothesis used in these simulation have not been confirmed by using benchmark data. By conducting these experiments in a microgravity environment, the effects of buoyancy are minimized, and the droplet can be characterized only as a function …

### Archivos perfilados (L2)

#### `PSI-68_Experimental table_Flex2.csv`

- Lista: `experimentalTable` · 1,029 bytes · sha256 `cc57ad1bd9977aa1…` · HTTP 200
- CSV · encoding `utf-8` · delimitador `,` · encabezado en fila 1 · filas no vacías **8** / físicas 8 · **7** columnas · bloques lado a lado: 1

| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |
|---|---|---|---|---:|---:|---|---|
| 1 | Sample (Fuel Type) | Fuel Type | text | 8 | 8 | IsoOctane (pure), n-Octane (pure), Heptane (pure) |  |
| 2 | Initial Droplet Diameter (mm) | mm | text | 8 | 1 | 1.5 - 5 |  |
| 3 | Ambient Gas Mixture |  | text | 8 | 1 | O2/N2 or O2/He |  |
| 4 | Oxygen Mole Fraction |  | text | 8 | 1 | 0.17; 0.21;0.25; 0.3 |  |
| 5 | Ambient Pressure (atm) | atm | text | 8 | 1 | 0.5; 1.0; 1.5; 2.0; or 3.0 |  |
| 6 | Ambient Temperature (C) | C | numeric | 8 | 1 | 25 … 25 |  |
| 7 | Flow Velocity (cm/s) | cm/s | text | 8 | 1 | 0.1 - 5 |  |

### Publicaciones con DOI (primeras 8)

- Experimental Study of Initial Diameter Effects on Convection-free Droplet Combustion in the Standard Atmosphere for n-Heptane, n-Octane, and n-Decane: International Space Station and Ground-based Experiments — doi:10.2514/6.2014-1019
- Droplet Combustion Experiments Aboard the International Space Station — doi:10.1007/s12217-014-9372-2
- Oxygen Lewis Number Effects on Reduced Gravity Combustion of Methanol and Heptane Droplets — doi:10.1080/00102202.2015.1072176
- ISS Droplet Combustion Experiments - Uncertainties in Droplet Sizes and Burning Rates — doi:10.1007/s12217-014-9377-x
- Combustion of Butanol, Gasoline, and Butanol/Gasoline Mixture Droplets — doi:10.1021/acs.energyfuels.5b00158
- Computational Modeling of Unsupported and Fiber-Supported n-Heptane Droplet Combustion in Reduced Gravity: A Study of Fiber Effects — doi:10.1080/00102202.2014.971950
- The role of cool-flame chemistry in quasi-steady combustion and extinction of n-heptane droplets — doi:10.1080/13647830.2014.934296
- Combustion of Submillimeter Heptane/Methanol and Heptane/Ethanol Droplets in Reduced Gravity — doi:10.1155/2013/154202

<!-- AUTO:END -->

## Evaluación (manual — DE/PHY)

> Primera pasada DE-04 (2026-11-14) basada en el bloque automático y en las muestras L2. La clasificación
> Medida / Calculada / Log es **propuesta DE — pendiente de validación PHY (PHY-02)**.

### Evaluación breve (contexto)
FLEX-2: ET de 8 filas con **rangos** de condiciones por combustible (O₂ 0.17–0.30, P 0.5–3 atm, flujo 0.1–5 cm/s), no pruebas individuales; `experimental_table_only`. Contexto del espacio de diseño de FLEX. **Tier 3.**
