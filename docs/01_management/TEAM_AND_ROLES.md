# Equipo, roles y forma de trabajo

## Asignación (completar en PM-01)

| Persona | Track principal | Track secundario | Contacto |
|---|---|---|---|
| | DE — Data Engineering | | |
| | DS — Data Science | RAG | |
| | PHY — Physics | SUB | |
| | APP — Dashboard | DE | |

## RACI por gate (R = ejecuta · A = aprueba · C = consultado · I = informado)

| Gate | DE | DS | RAG | PHY | APP |
|---|---|---|---|---|---|
| G0 Setup + RQ | C | R/A | I | C | I |
| G1 Triage | R/A | C | I | C | I |
| G2 Gold | R/A | C | I | I | I |
| G3 Findings | C | R | I | A | I |
| G4 Modelos | C | R | I | A | I |
| G5 RAG | C | C | R/A | C | I |
| G6 Dashboard | C | C | C | C | R/A |
| G7 Recomendaciones | I | C | I | R/A | I |
| G8 Entrega | C | C | C | C | R/A |

## Reglas de colaboración

- **Ramas:** `main` protegida; ramas `<track>/<id>-<slug>` (p. ej. `de/DE-07-silver-parsers`). PR pequeño > PR grande.
- **Commits:** `[ID] verbo en imperativo` — p. ej. `[DE-07] add FLEX droplet parser`.
- **Reviews:** 1 aprobación de otro track para tocar `src/`; PHY aprueba findings y model cards.
- **Sync:** cada 4 h, 10 min, de pie. Actualizar [PROGRESS.md](PROGRESS.md) al terminar.
- **Bloqueo > 30 min** → se avisa en el canal del equipo, no se espera al sync.
- **Datos:** nunca commitear `data/bronze|silver|gold`, secretos ni archivos > 5 MB.
- **Descanso:** turnos de sueño escalonados de 2–3 h a partir de H+14 para que siempre haya alguien en la ruta crítica.
