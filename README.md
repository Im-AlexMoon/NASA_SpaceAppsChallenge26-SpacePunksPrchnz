# 🔥 FlameSafe — Flames in Free Fall

**NASA Space Apps Challenge 2026 · Team SpacePunks**

An SI-powered web dashboard that **summarizes, ranks and interprets** NASA's microgravity combustion investigations
(Physical Sciences Informatics, PSI) to deliver traceable fire-safety insights for crewed spacecraft, the lunar base,
pressurized rovers and Mars.

> **Status:** 🚧 in development. Plan: [docs/00_executive/EXECUTIVE_PLAN.md](docs/00_executive/EXECUTIVE_PLAN.md) ·
> Progress: [docs/01_management/PROGRESS.md](docs/01_management/PROGRESS.md)

## Run the public dashboard

The dashboard uses the versioned data in `web/src/content`. From a clone, use Node 22 or newer:

```powershell
npm --prefix web ci
npm --prefix web run dev
```

Open the address printed by Next.js. The public pages use the static snapshot. The optional chat uses a separate FastAPI service and a dashboard access token.

## What FlameSafe does

- Shows where the analyzed ISS combustion tests support an atmosphere comparison and where new measurements are needed.
- Reports observed outcomes and model estimates separately. M‑01 v2 describes the persistence of an already-lit laboratory gas flame in microgravity.
- Ranks the 24 investigations in the PSI snapshot using adjustable criteria.
- Serves exact queries and source excerpts through the optional chat.

NASA PSI data pass through Bronze, Silver and Gold. The Gold tables, curated findings and model feed the static Next.js site and the FastAPI evidence service. Streamlit is a historical prototype.

See [the release procedure](docs/06_submission/RELEASE_PROCEDURE.md) for reproduction, checks and rollback.

## Data & credits

Data: NASA Physical Sciences Informatics (PSI), cited by PSI accession and DOI. Raw NASA files are **not** redistributed here.
This project is not endorsed by NASA. Full references: [docs/REFERENCES.md](docs/REFERENCES.md).

## License

Code: MIT ([LICENSE](LICENSE)). NASA data remain subject to NASA's terms.
