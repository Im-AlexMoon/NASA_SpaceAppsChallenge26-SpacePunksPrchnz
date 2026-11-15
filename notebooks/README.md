# notebooks/

Exploración y EDA. **Regla:** los notebooks exploran; el código reutilizable se mueve a `src/flamesafe/`.

- Nombre: `NN_<track>_<tema>_<iniciales>.ipynb` — p.ej. `02_eda_rq1_oxygen_extinction_am.ipynb`
- `01_discovery/` exploración de formatos PSI (F1) · `02_eda/` EDA por pregunta (F3) · `03_modeling/` (F4) · `04_rag/` (F5)
- Leer **solo** de `data/silver` o `data/gold`, nunca de bronze directamente (salvo `01_discovery`).
- Antes de commitear: "Restart & Run All" debe funcionar; limpiar outputs pesados.
- Todo hallazgo que vaya al dashboard se registra como finding en `docs/03_data_science/findings/`.

## Índice

| Notebook | Qué responde | Estado |
|---|---|---|
| `01_discovery/01_discovery_gold_coverage_am.ipynb` | Inventario de gold, diseño experimental, confusores, faltantes, cobertura cerca de los hábitats y evidencia para R-DE-05b | ✔ 2026-11-14 |
| `01_discovery/01_eda_nochateado.ipynb` | Exploración inicial de `burn_time_s` y `extinction_mode` en gas | 🟦 prototipo 2026-11-15 |
| `02_eda/02_eda_rq1_ignition_boundary_am.ipynb` | RQ1: ignición y extinción de llamas de gas (CFI-G) frente a O₂, presión y combustible; pruebas pre-registradas T1–T4 | ✔ v1 2026-11-14 (pendiente PHY-03) |
| `02_eda/02_eda_legit.ipynb` | Auditoría de identidad y cronología, familias y réplicas, faltantes, PCA por familia y asociaciones categórica × numérica (descriptivo) | ✔ 2026-11-15 (sin salidas versionadas) |

Orden recomendado: `01_discovery` → `02_eda` → `03_modeling`. `04_rag` es independiente y puede avanzar en paralelo.
Para ejecutar: `uv sync --extra pipeline --extra analysis --extra dev` y tener gold construido (`uv run flamesafe gold`).
