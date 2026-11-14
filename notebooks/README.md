# notebooks/

Exploración y EDA. **Regla:** los notebooks exploran; el código reutilizable se mueve a `src/flamesafe/`.

- Nombre: `NN_<track>_<tema>_<iniciales>.ipynb` — p.ej. `02_eda_rq1_oxygen_extinction_am.ipynb`
- `01_discovery/` exploración de formatos PSI (F1) · `02_eda/` EDA por pregunta (F3) · `03_modeling/` (F4) · `04_rag/` (F5)
- Leer **solo** de `data/silver` o `data/gold`, nunca de bronze directamente (salvo `01_discovery`).
- Antes de commitear: "Restart & Run All" debe funcionar; limpiar outputs pesados.
- Todo hallazgo que vaya al dashboard se registra como finding en `docs/03_data_science/findings/`.
