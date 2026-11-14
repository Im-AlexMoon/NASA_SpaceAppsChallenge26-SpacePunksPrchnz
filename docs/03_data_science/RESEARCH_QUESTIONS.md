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

| RQ | Variables de condición | Variables de resultado | Agrupación (para CV) | Tabla gold |
|---|---|---|---|---|
| RQ1 | _por llenar tras G1_ | | | `gas_flame_tests` |
| RQ2 | | | | `droplet_tests` |
| RQ5 | | | | `investigations` |

## Cómo se convierte una RQ en dashboard
RQ → finding(s) → figura con fuente → interpretación física → recomendación → página *Insights* / *Habitat Risk Explorer*.
