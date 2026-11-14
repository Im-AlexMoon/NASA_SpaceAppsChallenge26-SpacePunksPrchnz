# Data dictionary (gold)

> Tarea DE-10. **Se escribe antes de construir la tabla** (contrato DS→DE, tarea DS-02) y se actualiza con cada cambio.

## Convenciones
- Nombres `snake_case`, sufijo de unidad: `_kpa`, `_k`, `_cm_s`, `_mg_s`, `_mm`, `_s`; fracción molar `_xo2` (0–1).
- `__flag`: token original cuando el valor es NULL o no numérico.
- `is_computed`: la fuente lo calculó (no es medición directa).
- Procedencia mínima en toda tabla: `psi_id`, `source_file`, `source_row`.

## Matriz de comparabilidad (llenar en F1/F2 con PHY)

| Concepto | Investigación A (col, unidad, medido/calc.) | Investigación B | ¿Comparable? | Regla |
|---|---|---|---|---|
| Oxígeno | | | | XO₂ ↔ %vol convertible explícitamente |
| Presión | | | | todo a kPa |
| Temperatura | | | | medida ≠ calculada: nunca mismo eje sin etiqueta |
| Flujo | | | | caudal másico ≠ velocidad sin geometría |

## Tablas

### `<tabla_gold>`
- **Granularidad:** una fila = …
- **Fuente(s):** PSI-XX `<archivo>`
- **Filtros aplicados:**

| Columna | Tipo | Unidad | Origen (col. fuente) | Transformación | Medida/Calc./Log | Nulos permitidos | Notas |
|---|---|---|---|---|---|---|---|
