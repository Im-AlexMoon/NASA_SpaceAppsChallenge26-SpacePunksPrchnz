# ADR-0005 — Extensión de adquisición: series temporales por prueba de ACME (CFI-G y Flame Design)

- **Estado:** **Aceptado (2026-11-15)** — aprobado por Alexander Moon (DS / líder). Pendiente de visto bueno informativo de DE.
- **Tarea relacionada:** investigación posterior a M1 ([RESEARCH_LOG.md](../../03_data_science/RESEARCH_LOG.md), agenda punto 1)
- **Fuentes de verdad:** [configs/timeseries_manifest.yaml](../../../configs/timeseries_manifest.yaml) (selección y presupuesto) ·
  [timeseries_manifest.csv](../../02_data_engineering/timeseries_manifest.csv) (lista resuelta, byte a byte)
- **Modifica:** ADR-0002 §3 (que excluía los flujos crudos `*_data.csv` de ACME). No lo reemplaza.

## Contexto
El equipo priorizó generar conocimiento con modelos físicos antes que entregables. La iteración 1 de investigación mostró que la
tabla resumen (una fila por prueba) ya no alcanza:

- La temperatura crítica de extinción radiativa **no se puede identificar** desde el resumen.
- Flame Design (327 pruebas de etileno) no tiene duración ni modo de extinción en gold.
- Parte de los cortes de flujo son por límite térmico del quemador y no por temporizador (censura informativa), y el resumen no los distingue.

PSI guarda para cada prueba una serie temporal de ~125 Hz con radiómetros, fotomultiplicadores, termopares, presiones y caudales,
más comentarios del operador y parámetros del punto de prueba. ADR-0002 las dejó fuera porque el MVP no las necesitaba y superan
el presupuesto de descarga (`configs/sources.yaml::download_budget`: 150 archivos, 500 MB).

## Decisión
Crear una **extensión de adquisición opcional y separada** del manifiesto núcleo:

| Grupo | Archivos | Tamaño | Contenido |
|---|---:|---:|---|
| `ts_acme_data` | 1,310 | 2,714.2 MB | `*_data.csv` y `*_mfcSetpoints.csv` de PSI-159 y PSI-10 |
| `ts_acme_test_notes` | 2,015 | 2.3 MB | `*.txt` de Raw Data: comentarios, TP y scripts "as run" |
| **Total** | **3,325** | **2,716.5 MB** | |

- Presupuesto propio de la extensión: **3,000 MB, 3,400 archivos, 50 MB por archivo**.
- Se descarga con `flamesafe timeseries` (6 descargas en paralelo como máximo) a `data/bronze/files/<PSI-ID>/`, con el mismo sidecar sha256.
- **El manifiesto núcleo no cambia** (147 archivos, 263 MB; `max_files` 150 y `max_total_mb` 500 siguen vigentes y con test).
  Quien solo quiera reconstruir gold no necesita la extensión.
- **Sigue prohibido** descargar video (`.ts`, `.mp4`), archivos de imágenes (`.zip`) y `.mdipsug`. El archivo completo de PSI
  (13.5 TB) nunca se descarga; esta extensión es el 0.02 %.

## Alternativas consideradas
| Opción | Pros | Contras |
|---|---|---|
| Subir el presupuesto del manifiesto núcleo a 3 GB | un solo manifiesto | todo el equipo tendría que bajar 2.7 GB para reconstruir gold; debilita el guardarraíl |
| Descargar una muestra (p. ej. 60 pruebas) | más ligero | la validación deja fuera días completos: se necesitan todas las pruebas de cada día; la censura y las réplicas exigen el conjunto completo |
| Solo los `.txt` (comentarios y TP) | 2 MB | no da el instante de extinción ni la radiación; no resuelve ninguno de los tres problemas del contexto |
| Ir directo a imágenes o video | radio de llama medido | terabytes; la serie temporal responde antes las mismas preguntas |

## Consecuencias
- Se pueden derivar por prueba: instante real de extinción, modo de extinción de Flame Design, historia de radiación (fracción
  radiativa), oscilaciones previas a la extinción, calentamiento del quemador y causa del corte de flujo.
- Bronze local crece de 0.3 GB a ~3 GB. No se versiona (`data/` está en `.gitignore`).
- Las tablas derivadas (una fila por prueba) deben ser **pequeñas y compartibles** para que el equipo no dependa de la descarga:
  silver de características + muestra en `data/sample/` si entran a gold.
- Riesgo de deriva: PSI puede cambiar archivos; el lock registra los bytes esperados y la descarga reporta diferencias de tamaño.
- Revisar después: si alguna característica derivada entra a gold, documentarla en DATA_DICTIONARY y añadir su contrato.
