# Cómo contribuir (equipo SpacePunks)

1. **Toma una tarea** del [plan ejecutivo](docs/00_executive/EXECUTIVE_PLAN.md) por su ID (p. ej. `DE-07`) y márcala como en curso en
   [PROGRESS.md](docs/01_management/PROGRESS.md).
2. **Rama:** `<track>/<ID>-<slug>` → `de/DE-07-silver-parsers`, `ds/DS-10-m1-logistic`, `phy/PHY-07-atmospheres`.
3. **Commits:** `[ID] verbo en imperativo` → `[DE-07] add FLEX droplet parser`.
4. **Código reutilizable** en `src/flamesafe/`; los notebooks solo exploran ([notebooks/README.md](notebooks/README.md)).
5. **Antes del PR:** `ruff check src tests app` y `pytest -m "not integration"` en verde; documento correspondiente actualizado
   (data dictionary, finding, model card o ADR).
6. **PR** con la plantilla; 1 revisión de otro track. Findings y model cards requieren aprobación de PHY.
7. **Al hacer merge:** marca el checkbox en [MILESTONES.md](docs/01_management/MILESTONES.md) con hora e iniciales.

## Reglas de oro
- Nada sin procedencia (PSI-ID, archivo, sha256). Nada inventado. Lo desconocido se marca como desconocido.
- Nunca commitear `data/bronze|silver|gold`, `.env` ni archivos > 5 MB.
- Faltantes y tokens de error (`#DIV/0!`, `RAMP`, `n/a`…) → `NULL` + flag, **nunca 0**.
- Cambios de alcance o de stack → ADR en `docs/01_management/decisions/`.
