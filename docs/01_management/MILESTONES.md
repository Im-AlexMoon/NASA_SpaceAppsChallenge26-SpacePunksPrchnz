# Milestones — checklist de avance

> Marca cada tarea como `- [x] ID … — HH:MM · iniciales`. Un gate solo se marca cuando **todos** sus criterios están ✔.
> IDs y detalle en [EXECUTIVE_PLAN.md](../00_executive/EXECUTIVE_PLAN.md).

## F0 · Setup y alineación (objetivo H+2)
- [x] Estructura del repositorio y plan ejecutivo
- [ ] PM-01 Personas asignadas a tracks (RACI)
- [ ] PM-02 Entorno funcionando en todas las máquinas + CI verde
- [ ] PM-03 ADR-0001 y ADR-0003 aceptados
- [ ] DS-01 RQ v0 acordadas
- [ ] PHY-01 Primer de física leído por todos (primer revisado y actualizado — 2026-11-15 · AM; lectura del equipo por confirmar)
- [ ] 🚦 **G0** cerrado

## F1 · Descubrimiento y triage (objetivo H+5)
- [x] DE-01 Endpoints PSI verificados y registrados — 2026-11-14 · `flamesafe verify-api` + DATA_SOURCES.md
- [x] DE-02 Catálogo de 24 investigaciones en bronze — 2026-11-14 · `flamesafe catalog` (snapshot + manifest sha256)
- [x] DE-03 Inventario aplanado (investigaciones, archivos, tablas experimentales, publicaciones) — 2026-11-14 · `flamesafe silver` → `silver/catalog/*.parquet`
- [x] DE-04 Perfiles de formato (Tier 1/2 completos, resto mínimo) — 2026-11-14 · `flamesafe profile` → 24 perfiles + 60 muestras L2
- [x] DE-05 Matriz de triage + manifest de descarga + ADR-0002 — 2026-11-14 · `flamesafe triage` (T1 6 · T2 8 · T3 10; manifest 147 archivos / 263 MB)
- [x] PHY-02 Mapeo pilar/entorno validado — 2026-11-15 · AM (etiquetas del triage usadas por el ranking)
- [ ] 🚦 **G1** cerrado — datasets MVP congelados

## F2 · Pipeline medallion (objetivo H+9/H+10)
- [x] DS-02 Contrato de variables por RQ (DS→DE) — 2026-11-14 · RESEARCH_QUESTIONS §variables + DATA_DICTIONARY § Gold
- [x] DE-06 Bronze: descargas con sha256 + sidecars + reporte — 2026-11-14 · `flamesafe bronze` 145/147 (2 × 404 documentados), 262 MB
- [x] DE-07 Silver: parsers por familia, flags de faltantes, unidades, procedencia — 2026-11-14 · 33 tablas silver, 0 errores
- [x] DE-08 Gold: tablas por RQ + DuckDB — 2026-11-14 · `flamesafe gold`: 5 tablas, 1 violación de invariante (CFI 1274A)
- [x] DE-09 Contratos pandera + tests con fixtures — 2026-11-14 · 37/37 contratos; fixtures `data/sample/gold_*.parquet`
- [x] DE-10 Data dictionary completo — 2026-11-14 · cobertura verificada por `flamesafe validate`
- [x] 🚦 **G2** cerrado — `make pipeline` reproducible — 2026-11-14 · gate de datos PASSED (contratos 37/37, reconciliación 34/34, tokens 19/19, diccionario 5/5; rebuild determinista)
- [ ] ⭐ Vertical slice end-to-end (H+10)
- [ ] 🧊 Scope freeze (H+12)

## F3 · EDA y estadística (objetivo H+14)
- [ ] DS-03 RQs finales priorizadas
- [x] DS-04 EDA por RQ (notebooks) — RQ1 completo (discovery, EDA RQ1, auditoría y segmentación del equipo); RQ2 pendiente
- [x] DS-05 Tests estadísticos con efecto + IC — 2026-11-15/16 · T1–T4, Cox agrupado, bootstrap por días
- [x] DS-06 Findings redactados (≥ 3) — 2026-11-15 · AM · F-01..F-05 + `findings/index.yaml`
- [x] PHY-03 Interpretación física de cada finding — 2026-11-15 · AM
- [x] DS-07 Ranking MCDA reproducible — 2026-11-15 · AM · `flamesafe rank`, API `/v1/ranking`
- [ ] 🚦 **G3** cerrado — falta DS-03 (ratificar RQs) y el EDA de RQ2 (gotas); hallazgos y ranking ✔

## F4 · Modelado (objetivo H+17)
- [x] DS-08 Targets + baselines — 2026-11-15 · ignición y duración con censura; baselines trivial y O₂ + presión
- [x] PHY-04 Validación física de features/monotonías — 2026-11-15 · AM · INTERPRETATION_FRAMEWORK §Aplicación + test de signos
- [x] DS-09 Features físicas — 2026-11-15/16 · Tad, Zst, ṁ, L (`physics/thermochem.py`, `spherical_flame.py`)
- [x] DS-10 Modelos entrenados — 2026-11-15 · AM · M-01 v2 (`flamesafe m1-train`)
- [x] DS-11 Validación agrupada + calibración — 2026-11-15 · AM · dejando fuera un día; calibración por terciles; transferencia entre campañas
- [x] DS-12 Incertidumbre + dominio de aplicabilidad — 2026-11-15 · AM · IC por bootstrap de días; niveles A/B/C
- [x] PHY-05 Bounding de gravedad parcial — 2026-11-15 · AM · PARTIAL_GRAVITY_BOUNDING.md
- [x] DS-13 Umbrales de riesgo para atmósferas de referencia — 2026-11-15 · AM · `/v1/readings/atmospheres`
- [x] 🚦 **G4** cerrado — model card(s) firmadas — 2026-11-15 · AM · M-01 v2 firmada por PHY

## F5 · RAG (objetivo H+16)
- [x] RAG-01 Corpus — 2026-11-15 · AM · 11 documentos revisados en `configs/rag_sources.yaml` (76 fragmentos)
- [ ] RAG-02 Índice híbrido — implementado por el equipo; snapshot léxico validado — 2026-11-15 · AM; el híbrido requiere los pesos E5 en el despliegue
- [x] RAG-03 Herramientas SQL sobre gold — 2026-11-15 · J0SETS (9 consultas parametrizadas)
- [x] RAG-04 Contrato de respuesta con citas — 2026-11-15 · J0SETS (ADR-0008, extractivo)
- [x] RAG-05 Evaluación (≥ 20 preguntas) — 2026-11-15 · J0SETS (60 preguntas de definiciones; falta evaluación en vivo)
- [ ] 🚦 **G5** cerrado

## F6 · Dashboard (objetivo H+20)
- [ ] APP-01 Wireframes aprobados
- [ ] APP-02 Vertical slice
- [ ] APP-03 Explorer + Compare
- [ ] APP-04 Insights
- [ ] APP-05 Habitat Risk Explorer
- [ ] APP-06 Ask the Data
- [ ] APP-07 Methods & Sources
- [ ] APP-08 Despliegue público
- [ ] 🚦 **G6** cerrado

## F7 · Física (continuo, objetivo H+20)
- [x] PHY-06 Revisión de literatura — 2026-11-15 · AM · 20 referencias verificadas contra PSI/NTRS
- [x] PHY-07 Atmósferas de hábitat con citas — 2026-11-15 · AM
- [x] PHY-08 Marco de interpretación — 2026-11-15 · AM
- [x] PHY-09 Recomendaciones accionables — 2026-11-15 · AM · REC-01..REC-07
- [x] 🚦 **G7** cerrado — 2026-11-15 · AM (firma PHY: Alexander Moon)

## F8 · Entrega (objetivo H+24)
- [ ] SUB-01 Code freeze + tag v1.0
- [ ] SUB-02 Video demo
- [ ] SUB-03 README final
- [ ] SUB-04 Página Space Apps enviada
- [ ] SUB-05 Checklist final
- [ ] 🚦 **G8** — ENVIADO 🚀
