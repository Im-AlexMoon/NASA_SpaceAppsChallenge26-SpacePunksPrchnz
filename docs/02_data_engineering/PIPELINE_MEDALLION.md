# Pipeline medallion (bronze → silver → gold)

> Tareas DE-06 → DE-10. Cierra en **G2**. Comandos: `flamesafe catalog | bronze | silver | gold` (o `make pipeline`).

## 1. Contratos por capa

| | **Bronze** | **Silver** | **Gold** |
|---|---|---|---|
| Propósito | Copia fiel e inmutable de la fuente | Datos limpios y tipados, uno a uno con la fuente | Tablas analíticas armonizadas, una por necesidad (RQ/modelo/página) |
| Formato | Original + `*.meta.json` | Parquet | Parquet + `flamesafe.duckdb` |
| Granularidad | archivo | tabla fuente | entidad analítica (prueba, condición, investigación) |
| Transformaciones | ninguna | tipos, nombres snake_case, tokens faltantes → NULL + `__flag`, unidades explícitas, dedupe exacto | joins, unidades canónicas, variables derivadas físicas, filtros documentados |
| Procedencia | url, retrieved_at, http_status, bytes, sha256 | + `psi_id`, `source_file`, `source_sha256`, `source_row` | se conserva `psi_id` + `source_row` (o lista) |
| Validación | sha256 + tamaño esperado | esquema pandera por tabla | esquema pandera + reglas de negocio + reconciliación de conteos |
| Idempotencia | no re-descarga si sha256 coincide | determinista | determinista |

## 2. Estructura de carpetas

```text
data/
  bronze/
    catalog/LATEST                              # nombre del último snapshot completo
    catalog/snapshot_YYYY-MM-DD/                # 1 snapshot inmutable por día UTC; re-correr el mismo día reanuda
      search.json, PSI-XX.json                  # respuestas del API byte a byte (incluyen contactos de PIs → silver los elimina)
      manifest.json                             # url, retrieved_at_utc, http_status, bytes, sha256 por archivo + drift vs snapshot previo
    files/PSI-XX/<archivo original> + <archivo>.meta.json   # psi_id, list_source, source_url, retrieved_at_utc, http_status, bytes, sha256, size_matches
    _reports/acquisition_<selección>.json, l2_profiles.json
  silver/
    catalog/investigations.parquet, files.parquet, publications.parquet
    psi_xx__<tabla>.parquet
    _reports/parse_report.json                 # filas leídas/emitidas/descartadas + issues
  gold/
    <tabla_gold>.parquet
    flamesafe.duckdb
    _reports/quality_report.json
```

### Adquisición bronze (DE-06)

```bash
flamesafe bronze --dry-run       # resuelve el lock, valida presupuesto y drift vs catálogo; no descarga
flamesafe bronze                 # descarga docs/02_data_engineering/acquisition_manifest.csv → data/bronze/files/
flamesafe bronze --verify-only   # re-hashea todo contra sus sidecars (corrupción, huérfanos, .part)
```

- La entrada es **el lock** (`acquisition_manifest.csv`, generado por `flamesafe triage` y versionado), no el YAML. Así lo
  descargado es exactamente lo revisado en DE-05.
- Lo ya descargado con sha256 válido se reutiliza (p. ej. las muestras L2). Los 404 se registran en el sidecar y no se ocultan.
- Si un tamaño no coincide con el lock o falla la integridad, el comando sale con código 1. El drift (PSI cambió desde DE-05) se reporta.
- Reporte: `data/bronze/_reports/acquisition_l3_manifest.json` (por grupo, duplicados por sha256, integridad, drift).

## 3. Reglas de transformación (no negociables)

1. **Nunca** convertir faltantes, `#DIV/0!`, `#VALUE!`, `OR`, `RAMP`, etc. a 0. → `NULL` + columna `<col>__flag` con el token original.
2. Valores originales y unidades originales se conservan en silver; la conversión canónica (configs/pipeline.yaml::units)
   se hace en gold con funciones de `src/flamesafe/physics/units.py` (testeadas, reversibles).
3. Variables calculadas por la fuente (p. ej. Tad) se marcan `is_computed = true` en el data dictionary.
4. Exportes alternativos del mismo dato (p. ej. CSV vs XLSX de una misma telemetría) **no se concatenan**: se elige uno canónico (ADR).
5. Cada parser es una función registrada por familia de tabla con su test sobre un fixture en `data/sample/`.
6. Encoding: intentar utf-8, luego cp1252, registrando el fallback en el parse report.

## 4. Tablas gold previstas (se confirman en DS-02)

| Tabla gold | Fuente candidata | Uso |
|---|---|---|
| `investigations` | catálogo L0/L1 + triage + ranking | Explorer, Compare, ranking, RAG |
| `gas_flame_tests` | **CFI-G (PSI-159)** + Flame Design (PSI-10) unido a `EventData` | RQ1, M1/M3 |
| `droplet_tests` | **FLEX (PSI-69)** + **CFI DataSummary (PSI-39)**; PSI-117 como validación | RQ2, M2 |
| `solid_material_tests` | BASS / BASS-II / SAFFIRE-II | RQ3, contexto material/flujo |
| `smoke_detection` | SAME / SAME-R | RQ4, detección |
| `fire_telemetry` (stretch) | SAFFIRE-III | series de tiempo de incendio a escala |
| `reference_atmospheres` | `physics/atmospheres.py` | Habitat Risk Explorer |

## 5. Calidad de datos (DE-09)

- Esquemas pandera para cada tabla silver y gold (`src/flamesafe/quality/`).
- Reconciliación: `filas_bronze_validas == filas_silver == Σ filas_gold` (o diferencia explicada en el reporte).
- Rangos físicos plausibles (p. ej. 0 ≤ XO₂ ≤ 1; presión > 0) → violación = error, no se corrige en silencio.
- El `quality_report.json` alimenta la página *Methods & Sources*.
