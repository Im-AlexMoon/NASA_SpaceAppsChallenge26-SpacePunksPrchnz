# ADR-0012 — Respuestas sintetizadas con Gemini, ancladas a citas y cifras verificadas

- **Estado:** **Aceptado (2026-11-15)** por el responsable del proyecto (Alexander Moon), que pidió que el chat "responda como un agente"
  preguntas como "¿cuáles son los 3 descubrimientos más relevantes del estudio?". `findings/STUDY_SUMMARY.md` revisado y aprobado por él el mismo día.
- **Modifica:** el contrato extractivo de [ADR-0008](ADR-0008-rag-extractive-baseline.md) (solo citas literales). ADR-0004 (arquitectura RAG) sigue vigente.

## Contexto
Con el contrato de ADR-0008 el chat solo podía devolver fragmentos copiados; no podía comparar, ordenar ni resumir. Tres obstáculos más:
1. El adaptador de Gemini enviaba `response_schema` con los contratos estrictos (`additionalProperties: false`) y la API los rechazaba
   (400 INVALID_ARGUMENT): la generación nunca había funcionado.
2. Cualquier número en la pregunta activaba "confirma unidades y filtros": "los 3 descubrimientos" se bloqueaba.
3. Si el planificador inventaba una consulta estructurada sin filas, la respuesta terminaba en "no hay registros".

## Decisión
| Regla | Implementación |
|---|---|
| Afirmaciones `interpretation`/`limitation` pueden sintetizar, ordenar o traducir | `ANSWER` en `rag/service.py` |
| Cada afirmación cita fragmentos existentes del corpus | `validate_claims`: cita desconocida → rechazo |
| **Toda cifra de una afirmación sintetizada debe aparecer literalmente en los fragmentos que cita** | `validate_claims`: `_numbers(texto) ⊆ _numbers(citados)` |
| Las afirmaciones `data` siguen siendo citas literales exactas | sin cambio |
| Un conteo pequeño ("3 main findings") no es un filtro numérico | `COUNT_WORDS` |
| Consultas del planificador sin filas se descartan y se responde con documentos | `ask()` (las consultas explícitas del usuario conservan el comportamiento anterior) |
| Gemini con esquema JSON completo | `providers.py`: `response_json_schema=schema.model_json_schema()` |
| Preguntas generales sobre el estudio tienen una fuente directa y bilingüe | `findings/STUDY_SUMMARY.md` (revisado por PHY) |
| Producción: generación encendida, modo `free`, cuotas diarias y mensuales | variables de Cloud Run; clave en Secret Manager (`gemini-api-key`) |

Se mantienen: guardia de predicciones (el chat no predice), máximo tres llamadas por pregunta, presupuesto atómico, ninguna cifra
calculada por el modelo, datos tabulares solo desde herramientas tipadas.

## Consecuencias
- El chat puede responder preguntas de síntesis con trazabilidad; si los fragmentos no lo sostienen, no responde.
- Una paráfrasis puede matizar mal un fragmento sin cambiar cifras: por eso la UI muestra cada cita y su fuente, y el resumen del
  estudio debe estar revisado por PHY.
- La búsqueda sigue siendo léxica: el corpus necesita textos en el idioma de las preguntas (por eso el resumen es bilingüe).
