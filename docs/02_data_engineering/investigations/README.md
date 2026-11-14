# Perfiles de investigaciones (DE-04)

> Un archivo por registro PSI. Cada uno tiene un **bloque AUTO**, que se regenera con `flamesafe profile` a partir del catálogo
> silver y de las muestras L2 descargadas, y un **bloque manual** (evaluación DE/PHY) que se preserva al regenerar.
> Muestras L2: [configs/l2_samples.yaml](../../../configs/l2_samples.yaml) → 60 archivos, 50.3 MB (22 tablas experimentales
> + 38 archivos seleccionados), 60/60 HTTP 200, tamaños = listado.

## Resumen de la primera pasada (borrador para DE-05 — triage)

| PSI | Acrónimo | Mejor fuente tabular | Resultado medido disponible | Pilar | RQ | Tier (borrador) |
|---|---|---|---|---|---|---|
| [PSI-159](PSI-159.md) | ACME CFI-G | ET Normal (179) + Inverse (154) | ignición, tiempo de quemado, SE/FT, llama fría, T del quemador | Prevención | RQ1 · M1/M3 | **1** |
| [PSI-69](PSI-69.md) | FLEX | ET (274) | D de extinción, tasa de quemado, tiempo de quemado, `Test end` | Supresión | RQ2 · M2 | **1** |
| [PSI-39](PSI-39.md) | CFI | DataSummary `DATA` + `Master Sheet` (146 completas) | k caliente y frío, Dext caliente y frío, reigniciones | Prev./Sup. | RQ2 · M2 | **1** ⬆ |
| [PSI-10](PSI-10.md) | ACME Flame Design | ET (327) + Chamber Calculator `EventData` | ignición (solo vía `EventData`) | Prevención | RQ1 · M1 | **1** (condicional) |
| [PSI-117](PSI-117.md) | — (tierra) | CSVs de figuras + ReadMe | Dext y k (Expt vs Model) | Prev./Sup. | RQ2 (validación) | 2 |
| [PSI-25](PSI-25.md) | BASS-II | ET (129) + calibración de ventilador | O₂, CO₂ y CO finales (sin tasas de propagación) | Prevención | RQ3 | 2 |
| [PSI-26](PSI-26.md) | BASS | As-Run Matrix (130) | observaciones en texto libre | Prevención | RQ3 | 2 |
| [PSI-98](PSI-98.md) | SAFFIRE-I | Telemetría XLSX (antes 404) | radiómetros, detectores de humo, P y T | Detección | RQ4 | 2 ⬆ |
| [PSI-100](PSI-100.md) | SAFFIRE-III | Telemetría CSV/XLSX | radiómetros, detectores de humo, P y T | Detección | RQ4 | 2 |
| [PSI-101](PSI-101.md) | SAME-R | ET (109) + HKP + analizados | señales de detectores y aerosol | Detección | RQ4 | 2 |
| [PSI-102](PSI-102.md) | SAME | ET (8) + testlog/HKP | señales de detectores | Detección | RQ4 | 2 |
| [PSI-107](PSI-107.md) | SPICE | SmokePointReview (114) | longitud de punto de humo | Det./Prev. | RQ4 (contexto) | 2 |
| [PSI-99](PSI-99.md) | SAFFIRE-II | ET (9 muestras) | propagación **µg y 1 g** (texto) | Prevención | RQ3 | 2 (singular) |
| [PSI-23](PSI-23.md) | ACME s-Flame | ET por día + test log | — | — | — | 3 |
| [PSI-20](PSI-20.md) · [21](PSI-21.md) · [22](PSI-22.md) | ACME BRE · CLD · E-FIELD | ET por día de prueba | — | Contexto (E-FIELD: proxy de gravedad parcial) | — | 3 |
| [PSI-47](PSI-47.md) | DAFT | resumen XLS | conteos de polvo | Detección (polvo lunar) | — | 3 |
| [PSI-68](PSI-68.md) | FLEX-2 | ET de rangos (8) | — | Supresión | — | 3 |
| [PSI-106](PSI-106.md) | SLICE | ET (fecha, combustible) | — | — | — | 3 |
| [PSI-142](PSI-142.md) | — (índice) | índice de figuras CFE/HFE | puntos de figuras | — | — | 3 |
| [PSI-60](PSI-60.md) · [62](PSI-62.md) · [115](PSI-115.md) | — (tierra) | sin tablas muestreadas | — | — | — | 3 |

⬆ = sube respecto a la clasificación del repositorio de referencia.

## Hallazgos clave de DE-04
1. **CFI (PSI-39) tiene resultados procesados:** la hoja `CFI_DataSummary` trae k (mm²/s) y Dext de llama caliente y fría para
   146 pruebas, con O₂, N₂, He y presión en la `Master Sheet`. Junto con FLEX forma un dataset de supresión por dilución mucho
   más rico que lo esperado.
2. **PSI-10 no tiene resultado en su tabla experimental.** La ignición (Sí/No) está en el `EventData` del Chamber Calculator
   y se une por ID de prueba. Para M1, la fuente primaria es CFI-G (PSI-159), que trae ignición, extinción y llama fría en la tabla.
3. **Ninguna tabla trae tasas de propagación de llama en sólidos**, salvo SAFFIRE-II (9 muestras, en texto, µg y 1 g).
   BASS y BASS-II solo tienen las tasas en video.
4. **Calidad recurrente:** tokens dentro de columnas numéricas (`RAMP`, `#DIV/0!`, `–`, `OR`, `~6`), subíndices perdidos en
   encabezados (FLEX "O"/"CO", SAFFIRE-II "?-g"), categorías con mayúsculas inconsistentes, IDs con espacios, y exportes duplicados
   (SAFFIRE-III) que no deben concatenarse.
