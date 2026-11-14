# Milestones — checklist de avance

> Marca cada tarea como `- [x] ID … — HH:MM · iniciales`. Un gate solo se marca cuando **todos** sus criterios están ✔.
> IDs y detalle en [EXECUTIVE_PLAN.md](../00_executive/EXECUTIVE_PLAN.md).

## F0 · Setup y alineación (objetivo H+2)
- [x] Estructura del repositorio y plan ejecutivo
- [ ] PM-01 Personas asignadas a tracks (RACI)
- [ ] PM-02 Entorno funcionando en todas las máquinas + CI verde
- [ ] PM-03 ADR-0001 y ADR-0003 aceptados
- [ ] DS-01 RQ v0 acordadas
- [ ] PHY-01 Primer de física leído por todos
- [ ] 🚦 **G0** cerrado

## F1 · Descubrimiento y triage (objetivo H+5)
- [x] DE-01 Endpoints PSI verificados y registrados — 2026-11-14 · `flamesafe verify-api` + DATA_SOURCES.md
- [x] DE-02 Catálogo de 24 investigaciones en bronze — 2026-11-14 · `flamesafe catalog` (snapshot + manifest sha256)
- [x] DE-03 Inventario aplanado (investigaciones, archivos, tablas experimentales, publicaciones) — 2026-11-14 · `flamesafe silver` → `silver/catalog/*.parquet`
- [x] DE-04 Perfiles de formato (Tier 1/2 completos, resto mínimo) — 2026-11-14 · `flamesafe profile` → 24 perfiles + 60 muestras L2
- [x] DE-05 Matriz de triage + manifest de descarga + ADR-0002 — 2026-11-14 · `flamesafe triage` (T1 6 · T2 8 · T3 10; manifest 147 archivos / 263 MB)
- [ ] PHY-02 Mapeo pilar/entorno validado
- [ ] 🚦 **G1** cerrado — datasets MVP congelados

## F2 · Pipeline medallion (objetivo H+9/H+10)
- [ ] DS-02 Contrato de variables por RQ (DS→DE)
- [x] DE-06 Bronze: descargas con sha256 + sidecars + reporte — 2026-11-14 · `flamesafe bronze` 145/147 (2 × 404 documentados), 262 MB
- [ ] DE-07 Silver: parsers por familia, flags de faltantes, unidades, procedencia
- [ ] DE-08 Gold: tablas por RQ + DuckDB
- [ ] DE-09 Contratos pandera + tests con fixtures
- [ ] DE-10 Data dictionary completo
- [ ] 🚦 **G2** cerrado — `make pipeline` reproducible
- [ ] ⭐ Vertical slice end-to-end (H+10)
- [ ] 🧊 Scope freeze (H+12)

## F3 · EDA y estadística (objetivo H+14)
- [ ] DS-03 RQs finales priorizadas
- [ ] DS-04 EDA por RQ (notebooks)
- [ ] DS-05 Tests estadísticos con efecto + IC
- [ ] DS-06 Findings redactados (≥ 3)
- [ ] PHY-03 Interpretación física de cada finding
- [ ] DS-07 Ranking MCDA reproducible
- [ ] 🚦 **G3** cerrado

## F4 · Modelado (objetivo H+17)
- [ ] DS-08 Targets + baselines
- [ ] PHY-04 Validación física de features/monotonías
- [ ] DS-09 Features físicas
- [ ] DS-10 Modelos entrenados
- [ ] DS-11 Validación agrupada + calibración
- [ ] DS-12 Incertidumbre + dominio de aplicabilidad
- [ ] PHY-05 Bounding de gravedad parcial
- [ ] DS-13 Umbrales de riesgo para atmósferas de referencia
- [ ] 🚦 **G4** cerrado — model card(s) firmadas

## F5 · RAG (objetivo H+16)
- [ ] RAG-01 Corpus
- [ ] RAG-02 Índice híbrido
- [ ] RAG-03 Herramientas SQL sobre gold
- [ ] RAG-04 Contrato de respuesta con citas
- [ ] RAG-05 Evaluación (≥ 20 preguntas)
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
- [ ] PHY-06 Revisión de literatura
- [ ] PHY-07 Atmósferas de hábitat con citas
- [ ] PHY-08 Marco de interpretación
- [ ] PHY-09 Recomendaciones accionables
- [ ] 🚦 **G7** cerrado

## F8 · Entrega (objetivo H+24)
- [ ] SUB-01 Code freeze + tag v1.0
- [ ] SUB-02 Video demo
- [ ] SUB-03 README final
- [ ] SUB-04 Página Space Apps enviada
- [ ] SUB-05 Checklist final
- [ ] 🚦 **G8** — ENVIADO 🚀
