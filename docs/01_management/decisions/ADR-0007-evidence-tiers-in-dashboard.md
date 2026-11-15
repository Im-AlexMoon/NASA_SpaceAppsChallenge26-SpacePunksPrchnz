# ADR-0007 — Lecturas del modelo en el dashboard, con niveles de evidencia

- **Estado:** **Aceptado por el responsable del proyecto (2026-11-15)** como dirección de producto. Pendiente de incorporarse
  al [RAG_IMPLEMENTATION_PLAN.md](../../03_data_science/RAG_IMPLEMENTATION_PLAN.md) por el equipo que lo mantiene.
- **Tarea relacionada:** APP-01 / APP-05 · visión en [PRODUCT_VISION.md](../../05_dashboard/PRODUCT_VISION.md)
- **Modifica:** el punto "Predicciones: versión posterior; no habilitarlas en la primera entrega" de ADR-0004 y del plan RAG.
  No cambia la arquitectura, el hosting ni el alcance del RAG.
- **Nota de numeración:** ADR-0006 queda reservado para las decisiones PHY y la unidad de la tasa de quemado de FLEX.

## Contexto
El plan vigente inhabilita toda predicción en la primera versión para no publicar resultados sin aprobar. La precaución es
correcta, pero deja fuera lo que distingue al proyecto: la lectura por atmósfera con su nivel de evidencia y la ley física de
duración de la llama, que ya se transfiere entre campañas (RESEARCH_LOG R9). Sin eso, la aplicación queda como un catálogo con chat.

## Decisión
La primera versión **sí muestra lecturas del modelo**, bajo cuatro condiciones:

1. **Nivel de evidencia obligatorio** (A medido cerca, B interpolado, C sin evidencia). En nivel C no se muestra ningún número.
2. **Solo consultas parametrizadas y versionadas** servidas por el backend Python (atmósfera, combustible, fuente). El chat no
   calcula ni improvisa predicciones.
3. **Marca *Candidate*** en todo resultado sin firma PHY; un interruptor de publicación por bloque permite ocultarlo.
4. **Nunca gravedad parcial como dato:** se muestra microgravedad con la atmósfera del hábitat y se dice explícitamente.

## Alternativas consideradas
| Opción | Pros | Contras |
|---|---|---|
| Mantener las predicciones inhabilitadas (plan actual) | cero riesgo de publicar algo no revisado | la aplicación pierde su diferenciador; el Habitat Explorer queda solo con cobertura |
| Habilitar predicciones libres, también por chat | más llamativo | viola las reglas científicas; sin trazabilidad ni control de dominio |
| **Lecturas parametrizadas con niveles de evidencia y marca Candidate** | conserva el diferenciador y los controles | requiere un endpoint y componentes de evidencia; depende de la revisión PHY para quitar la marca |

## Consecuencias
- El backend necesita un endpoint de lectura por atmósfera con el modelo, el intervalo, el nivel de evidencia y las pruebas de respaldo.
- La UI necesita los componentes `evidence_level`, `candidate_badge` y la lista de pruebas cercanas.
- El RAG debe responder a preguntas predictivas remitiendo a esa lectura o explicando la brecha, nunca generando un número.
- Si PHY no firma a tiempo, la aplicación se publica con la marca *Candidate* o con el bloque oculto: ambas salidas son válidas.
- El equipo del plan RAG debe actualizar su sección 1 y la fila `/habitat` de la sección 13.
