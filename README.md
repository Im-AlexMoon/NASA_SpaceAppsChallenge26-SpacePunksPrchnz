# 🔥 FlameSafe — Flames in Free Fall

**NASA Space Apps Challenge 2026 · Team SpacePunks**

An SI-powered web dashboard that **summarizes, ranks and interprets** NASA's microgravity combustion investigations
(Physical Sciences Informatics, PSI) to deliver traceable fire-safety insights for crewed spacecraft, the lunar base,
pressurized rovers and Mars.

> **Status:** 🚧 in development. Plan: [docs/00_executive/EXECUTIVE_PLAN.md](docs/00_executive/EXECUTIVE_PLAN.md) ·
> Progress: [docs/01_management/PROGRESS.md](docs/01_management/PROGRESS.md)

## What it does

| | Capability |
|---|---|
| 🔎 **Find** | Catalog of the 24 PSI combustion investigations, ranked by relevance to prevention / detection / suppression and to each crew environment, with adjustable weights |
| ⚖️ **Compare** | Side-by-side objectives, fuels, oxygen, pressure, flow, variables and sensors |
| 📊 **Understand** | Statistically supported findings, each with physical interpretation and a citation to the source file / DOI |
| 🎯 **Predict** | *Habitat Fire Risk Explorer*: set O₂, pressure, flow and gravity regime, get risk indicators with uncertainty and an explicit extrapolation warning |
| 💬 **Ask** | RAG assistant that answers only from cited evidence (documents + queries over curated data) |
| 🚀 **Act** | Actionable recommendations and the next experiments needed (e.g., partial-gravity data) |

## Architecture

```text
NASA PSI API → bronze (raw + sha256) → silver (typed, units, flags) → gold (analysis-ready, DuckDB)
                                                                     ├→ statistics & findings
                                                                     ├→ predictive models (+ uncertainty)
                                                                     ├→ relevance ranking (MCDA)
                                                                     └→ RAG index ──→ Streamlit dashboard
```

## Repository layout

```text
app/            Streamlit dashboard (multipage)
configs/        YAML configs: data sources, pipeline, models, RAG
data/           Medallion layers (bronze/silver/gold are generated, not committed; sample/ fixtures are)
docs/           Plans, methodology, scientific documentation, milestones, ADRs  →  docs/README.md
notebooks/      Exploration & EDA (reusable code goes to src/)
src/flamesafe/  Python package: ingestion, pipeline, quality, analysis, models, physics, ranking, rag
tests/          Unit and integration tests
reports/        Generated figures
artifacts/      Trained models and RAG indices (generated)
```

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[all]"
cp .env.example .env                                 # add ANTHROPIC_API_KEY for the assistant
pytest -m "not integration"
make pipeline        # or: flamesafe catalog && flamesafe bronze && flamesafe silver && flamesafe gold
make app             # streamlit run app/Home.py
```

## Data & credits

Data: NASA Physical Sciences Informatics (PSI), cited by PSI accession and DOI. Raw NASA files are **not** redistributed here.
This project is not endorsed by NASA. Full references: [docs/REFERENCES.md](docs/REFERENCES.md).

## License

Code: MIT ([LICENSE](LICENSE)). NASA data remain subject to NASA's terms.
