# Diseño del asistente RAG ("Ask the Data")

> **ANTECEDENTE — NO ES EL PLAN VIGENTE.** Desde el 2026-11-15, seguir [RAG_IMPLEMENTATION_PLAN.md](RAG_IMPLEMENTATION_PLAN.md) y [ADR-0004](../01_management/decisions/ADR-0004-rag-web-architecture.md). Este diseño se conserva como contexto; sus propuestas incompatibles (Anthropic como elección fija, embeddings en inglés y predicciones en la primera versión) quedan sustituidas. Los cambios posteriores deben actualizar el plan vigente y documentar la decisión correspondiente.

> Tareas RAG-01 → RAG-05. Cierra en **G5**. Config: `configs/rag.yaml`. Código: `src/flamesafe/rag/`.

## 1. Objetivo
Permitir navegar el dashboard y la evidencia en lenguaje natural ("¿Qué experimentos estudiaron supresión con helio?",
"¿Qué tan inflamable sería una atmósfera de 34% O₂ a 8.2 psi según los datos?") con respuestas **citadas** y **sin números inventados**.

## 2. Arquitectura

```text
pregunta ──► router ──┬─► retrieval documental (BM25 + embeddings, RRF) ──► chunks con PSI-ID/DOI/finding-id
                      ├─► herramientas estructuradas (SQL parametrizado sobre gold/DuckDB, predicción de modelos)
                      └─► navegación (deep-link a página/filtro del dashboard)
                                  │
                         LLM (Claude) con contrato de respuesta ──► validador de citas ──► respuesta + fuentes clicables
```

## 3. Corpus (RAG-01)

| Fuente | Unidad de chunk | Metadatos obligatorios |
|---|---|---|
| Metadatos PSI (objetivo, enfoque, hipótesis, hardware, impactos) | sección por investigación | `psi_id`, `acronym`, `section`, `doi` |
| Abstracts de publicaciones listadas en PSI | abstract | `psi_id`, `doi`, `year`, `authors` |
| Findings aprobados | finding | `finding_id`, `rq`, `psi_ids` |
| Model cards | sección | `model_id` |
| Docs de física (primer, atmósferas, recomendaciones) | sección | `doc`, `section` |

Chunks de ~300–500 tokens con solapamiento pequeño; nunca partir tablas.

## 4. Contrato de respuesta (RAG-04)
1. Cada afirmación factual lleva cita `[PSI-XX]`, `[doi:…]` o `[F-XX]`.
2. Todo número proviene de un chunk citado o de una herramienta SQL/modelo — nunca del conocimiento previo del LLM.
3. Separar **dato** ("los datos muestran…") de **interpretación** ("esto sugiere…").
4. Si no hay evidencia suficiente: decirlo y sugerir dónde buscar (página / investigación).
5. Preguntas de gravedad parcial → recordar que no hay datos medidos en PSI.
6. Temperatura 0; modelo configurable por `FLAMESAFE_LLM_MODEL`.

## 5. Evaluación (RAG-05)
Set ≥ 20 preguntas en `docs/03_data_science/rag_eval.md` (y `.jsonl`), cubriendo: búsqueda de investigaciones, comparación,
números de tablas gold, física, preguntas sin respuesta (deben rechazarse), preguntas trampa (gravedad parcial, cohetes).

| Métrica | Meta |
|---|---|
| Respuesta correcta | ≥ 85% |
| Citas válidas (existen y soportan la afirmación) | ≥ 95% |
| Números inventados | 0 |
| Rechazo correcto fuera de evidencia | 100% |

## 6. Riesgos
Alucinación de citas → validador que verifica que cada cita exista en los chunks recuperados. Costo/latencia → caché de
respuestas para las preguntas de la demo.
