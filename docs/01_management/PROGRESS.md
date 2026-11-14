# Progress — tablero de fases

> Se actualiza en cada sync (cada 4 h) y al cerrar un gate.
> Estado: ⬜ no iniciado · 🟦 en curso · 🟨 en riesgo · 🟥 bloqueado · ✅ cerrado

**H+0 (inicio):** `____-__-__ __:__` · **Deadline:** `____-__-__ __:__`

## Estado por fase

| Fase | Gate | Objetivo | Estado | % | Responsable | Nota |
|---|---|---|---|---|---|---|
| F0 Setup y alineación | G0 | H+2 | 🟦 | 20 | | Repo + plan listos |
| F1 Descubrimiento y triage | G1 | H+5 | 🟦 | 15 | DE | DE-01 ✔ (API verificado); siguiente DE-02 |
| F2 Pipeline medallion | G2 | H+9 | ⬜ | 0 | | |
| F3 EDA y estadística | G3 | H+14 | ⬜ | 0 | | |
| F4 Modelado | G4 | H+17 | ⬜ | 0 | | |
| F5 RAG | G5 | H+16 | ⬜ | 0 | | |
| F6 Dashboard | G6 | H+20 | ⬜ | 0 | | |
| F7 Física | G7 | H+20 | 🟦 | 5 | | Primer en borrador |
| F8 Entrega | G8 | H+24 | ⬜ | 0 | | |

## Bitácora de syncs

<!-- Copia este bloque por cada sync -->
### Sync H+0 — kick-off
- ✔ Hecho: estructura del repo, plan ejecutivo, plantillas.
- ▶ Siguiente: G0 (roles, entorno, RQ v0), arrancar DE-01/DE-02.
- ⛔ Bloqueos: —
- 🔀 Decisiones / recortes: —

### DE-01 cerrado — 2026-11-14
- ✔ Hecho: cliente PSI con reintentos (`psi_client.py`), comando `flamesafe verify-api`, reporte JSON de evidencia y 16 tests (2 en vivo).
- 📌 Hallazgos:
  - 133 investigaciones / 24 de combustión; todos los conteos de referencia coinciden.
  - **La telemetría de SAFFIRE-I ya descarga (HTTP 200).** La referencia la daba por 404.
  - Los datos PSI son **CC0 1.0** (23/24 registros).
  - Un id de investigación inexistente devuelve 403, no 404.
- ▶ Siguiente: DE-02 (catálogo de las 24 investigaciones a bronze) y DE-03 (aplanado del inventario).
