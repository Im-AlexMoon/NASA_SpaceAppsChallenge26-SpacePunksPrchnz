# ADR-0001 — Stack tecnológico

- **Estado:** Propuesto originalmente; sustituido parcialmente desde el 2026-11-15 por [ADR-0004](ADR-0004-rag-web-architecture.md) respecto a UI, despliegue, proveedor LLM y embeddings del nuevo RAG.
- **Tarea relacionada:** PM-03

> Para trabajo nuevo de RAG/dashboard, seguir el [plan vigente](../../03_data_science/RAG_IMPLEMENTATION_PLAN.md). La tabla siguiente conserva el stack propuesto originalmente; no usar sus elecciones sustituidas como instrucciones actuales. Las decisiones no afectadas de datos/calidad siguen aplicando.

## Contexto
24 h, equipo mixto (datos, ciencia, física), datos tabulares pequeños (tablas experimentales PSI ≈ cientos de KB) más algunos
archivos medianos (telemetría). Necesitamos velocidad de desarrollo, reproducibilidad y un dashboard desplegable sin frontend dedicado.

## Decisión

| Capa | Elección | Por qué |
|---|---|---|
| Lenguaje | Python 3.11 | Un solo lenguaje para DE, DS, RAG y app |
| Datos | pandas + pyarrow (Parquet) + DuckDB | Parquet por capa; DuckDB para SQL rápido en gold y herramientas del RAG |
| Calidad | pandera | Contratos de esquema declarativos y testeables |
| Estadística | scipy + statsmodels | IC, tests, GLM/GAM con inferencia |
| ML | scikit-learn + LightGBM (restricciones monótonas) + MAPIE (conformal) + SHAP | Pocos datos → interpretabilidad + incertidumbre |
| LLM | Claude vía Anthropic API (`claude-sonnet-5-5` por defecto, configurable en `.env`) | Calidad de razonamiento y citas; modelo intercambiable |
| Retrieval | BM25 (`rank-bm25`) + embeddings locales (`bge-small`) + LanceDB | Gratis, local, híbrido robusto para terminología técnica (siglas: BASS, FLEX, XO2…) |
| Dashboard | Streamlit multipage + Plotly | Lo más rápido de construir y desplegar en 24 h |
| Despliegue | Streamlit Community Cloud (alternativa: Hugging Face Spaces) | Gratis, deploy desde GitHub |
| Calidad de código | ruff + pytest + GitHub Actions | Simple y estándar |

## Alternativas consideradas
| Opción | Pros | Contras |
|---|---|---|
| FastAPI + React | UI más pulida y flexible | Dos códigos base; demasiado para 24 h |
| Dash | Más control de layout | Más verboso que Streamlit |
| polars en lugar de pandas | Más rápido | Curva de aprendizaje; volumen no lo justifica |
| Vector DB gestionada | Escala | Innecesario para < 10k chunks; requiere cuentas |

## Consecuencias
Una sola base de código Python; la UI será funcional más que espectacular — compensar con buen diseño de información.
Si el tiempo sobra, se puede pulir con componentes custom de Streamlit.
