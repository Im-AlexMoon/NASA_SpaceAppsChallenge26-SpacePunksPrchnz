# Preguntas de investigación

> **Estado:** v0 (borrador para G0) → v1 ratificada en DS-03 tras la triage (G1).
> Las RQ definen la narrativa del dashboard, las tablas gold y los modelos. Cada RQ se mapea a los tres objetivos del reto:
> **O1** identificar investigaciones relevantes para entornos tripulados · **O2** extraer datos para modelado predictivo de
> inflamabilidad · **O3** informar controles y equipos de seguridad contra incendio de próxima generación.

## Pregunta rectora

**¿Qué nos dicen décadas de experimentos de combustión en microgravedad sobre el riesgo de incendio en las atmósferas
enriquecidas en O₂ y de baja presión previstas para la base lunar, los rovers presurizados y Marte — y dónde están las brechas?**

## RQs

| ID | Pregunta | Pilar | Objetivo reto | Datos candidatos | Prioridad |
|---|---|---|---|---|---|
| **RQ1** | ¿Cómo gobiernan la fracción molar de O₂, la presión total (y la presión parcial de O₂) la ignición, sostenimiento y modo de extinción de llamas en microgravedad? ¿Qué implica para atmósferas de ≥ 30% O₂ y ≤ 10.2 psi? | Prevención | O2, O1 | ACME Flame Design, CFI-G | **MVP** |
| **RQ2** | ¿Cómo cambian los diluyentes inertes (CO₂, He, N₂) y la presión la tasa de quemado y el diámetro de extinción de gotas, y qué concentraciones extinguen la llama? | Supresión | O3, O2 | FLEX, FLEX-2, CFI | **MVP** |
| **RQ5** | ¿Cuáles de las 24 investigaciones son más relevantes para cada pilar y cada entorno tripulado? | Todos | O1 | Catálogo completo | **MVP** |
| **RQ3** | ¿Qué evidencia hay sobre el efecto del flujo de aire y del material en la inflamabilidad de sólidos (límites de inflamabilidad) en microgravedad? | Prevención | O2, O3 | BASS, BASS-II, SAFFIRE | Stretch |
| **RQ4** | ¿Cómo responden distintos detectores de humo a distintos materiales en microgravedad y qué implica para el diseño de detección? | Detección | O3 | SAME, SAME-R, SAFFIRE-III | Stretch |
| **RQ6** | ¿Qué hallazgos tienen aplicación directa a seguridad contra incendios en Tierra? | Todos | add-on | Todas + publicaciones | Stretch |

## Hipótesis de trabajo (a confirmar o refutar con datos — nunca se presentan como resultado)

- **H1 (RQ1):** a mayor XO₂ se amplía el rango de condiciones con llama sostenida; la presión parcial de O₂ explica la
  inflamabilidad mejor que la fracción molar sola *o* viceversa — determinar cuál con los datos.
- **H2 (RQ2):** el helio y el CO₂ difieren en eficacia de supresión por diferencias en capacidad calorífica y difusividad.
- **H3 (RQ3):** en microgravedad existe un flujo de aire de baja velocidad en el que la inflamabilidad es máxima, y los límites
  pueden ser menos conservadores que las pruebas normalizadas en 1 g.
- **H4 (RQ1/RQ3):** los resultados en µg y 1 g acotan el comportamiento en gravedad parcial (Luna 0.165 g, Marte 0.38 g).

## Variables necesarias por RQ (contrato DS→DE, tarea DS-02)

> **DS-02 (2026-11-14), contrato v1.** Basado en las fuentes congeladas en ADR-0002 y en los perfiles DE-04. Las especificaciones
> columna a columna están en [DATA_DICTIONARY.md § Gold](../02_data_engineering/DATA_DICTIONARY.md#gold).

| RQ | Variables de condición | Variables de resultado | Agrupación (para CV) | Tabla gold |
|---|---|---|---|---|
| RQ1 | `flame_type` (normal/inversa), `fuel`, `xo2` del lado oxidante, `x_fuel`, `p_kpa`, `po2_kpa` (derivada), caudales (`m_fuel_mg_s`, `m_o2_mg_s`, `m_n2_mg_s`), `zst` y `tad_k` (**calculadas**: etiquetarlas así) | `ignited` (bool) + `ignition_outcome` (yes/no/flash), `extinction_mode` (self_extinguished / flow_terminated), `burn_time_s`, `cool_flame`, `peak_burner_t_k` | `test_day` (día de operación) dentro de `campaign` | `gas_flame_tests` |
| RQ2 | `fuel`, `p_kpa`, `x_o2`, `x_n2`, `x_co2`, `x_he`, `d0_mm`, `fiber` (CFI) | `test_end` (extinction / disruption / completion, solo FLEX), `d_ext_hot_mm`, `d_ext_cool_mm`, `k_hot_mm2_s`, `k_cool_mm2_s`, `burn_time_s`, `reignitions` | `test_date` dentro de `campaign` | `droplet_tests` (+ `droplet_reference_points` de PSI-117 para validar) |
| RQ5 | pilar, entorno, hardware (normalizado), plataforma, tipo (vuelo/tierra), estado de acceso | puntajes R1–R6, tier, n de pruebas y variables disponibles | — | `investigations` |

**Decisiones del contrato:**
- `ignited` de Flame Design normal (PSI-10) viene del `EventData` del Chamber Calculator (columna `Ignite`, decisión operativa).
  En CFI-G viene de `Hot ignition` en la tabla experimental. Se guarda `outcome_source` para no confundirlos.
  **Actualización DE-07:** las inversas de PSI-10 aparecen en `EventData` como `INV_TP`. La unión cubre 207/207 normales y 118/120
  inversas, así que solo 2 pruebas quedan sin resultado. En CFI-G, `EventData` permite verificar `Hot ignition` en 331 pruebas.
- `flash` (CFI-G inversas, 8 casos) **no** se mapea a sí/no sin decisión de PHY: queda en `ignition_outcome` y `ignited = NULL`.
- La "tasa de quemado" de FLEX entra como `k_hot_mm2_s` solo cuando PHY confirme la unidad (R-DE-05b). Hasta entonces silver la guarda
  como `burning_rate_k` con la unidad del encabezado ("mm").
- En llamas inversas el O₂ sale del quemador: `xo2` = fracción del lado oxidante. `po2_kpa` = `xo2` × `p_kpa` es una variable derivada
  cuya interpretación requiere revisión PHY (PHY-04).

## Cómo se convierte una RQ en dashboard
RQ → finding(s) → figura con fuente → interpretación física → recomendación → página *Insights* / *Habitat Risk Explorer*.
