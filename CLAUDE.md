# CLAUDE.md — guía para asistentes de IA en este repo

Proyecto: NASA Space Apps 2026 "Flames in Free Fall" — dashboard que resume, rankea e interpreta las investigaciones de
combustión de NASA PSI para seguridad contra incendios en exploración espacial.

## Antes de trabajar
- Plan y tareas con ID: `docs/00_executive/EXECUTIVE_PLAN.md`. Avance: `docs/01_management/PROGRESS.md` y `MILESTONES.md`.
- Índice de docs: `docs/README.md`. Decisiones: `docs/01_management/decisions/`.
- **RAG y dashboard: seguir el plan vigente `docs/03_data_science/RAG_IMPLEMENTATION_PLAN.md` y ADR-0004 (2026-11-15).** Prevalecen sobre instrucciones incompatibles del diseño RAG anterior, la especificación Streamlit y ADR-0001. No volver a la arquitectura anterior sin documentar y actualizar la decisión. El objetivo es Node.js/Next.js con backend Python; implementación pendiente, predicciones diferidas.

## Convenciones
- Paquete Python en `src/flamesafe/`; CLI `flamesafe <verify-api|catalog|bronze|silver|gold|train|rag-index>`; configs en `configs/*.yaml`.
- Docs internos en español; README raíz, UI del dashboard, código e identificadores en inglés.
- Medallion: bronze inmutable con sidecar sha256 · silver tipado con `__flag` para tokens faltantes · gold armonizado por RQ.
- Unidades canónicas y conversiones solo vía `src/flamesafe/physics/units.py`; atmósferas de referencia en `physics/atmospheres.py`.
- Tests: `pytest -m "not integration"`; lint: `ruff check src tests app`.

## Reglas científicas (estrictas)
- No inventar conteos, valores, citas ni DOIs. Lo no verificado se marca ⚠️ / "por verificar".
- Faltantes/errores de hoja de cálculo → NULL + flag, nunca 0. No concatenar exportes alternativos del mismo dato.
- No mezclar variables no comparables (Tad calculada vs. temperatura medida; caudal másico vs. velocidad).
- PSI no tiene datos de gravedad parcial: todo resultado lunar/marciano es acotamiento o extrapolación y debe decirlo.
- El repo `YoussefHegazy74/flame-in-freefall` es solo referencia (ADR-0003): no copiar su código ni su texto.
- Nunca descargar el archivo PSI completo; respetar `configs/sources.yaml::download_budget`.
