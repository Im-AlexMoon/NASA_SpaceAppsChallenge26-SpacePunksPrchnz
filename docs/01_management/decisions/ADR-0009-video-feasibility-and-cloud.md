# ADR-0009 — Video de llamas: muestra de factibilidad local y procesamiento en Google Cloud

- **Estado:** **Aceptado (2026-11-16)** por el responsable del proyecto para la **fase 1** (muestra local). La fase 2 (todos
  los videos en la nube) requiere confirmar el resultado de la fase 1 y una alerta de presupuesto activa.
- **Tarea relacionada:** investigación posterior a M1 ([RESEARCH_LOG.md](../../03_data_science/RESEARCH_LOG.md), agenda punto 7)
- **Fuentes de verdad:** [configs/video_samples.yaml](../../../configs/video_samples.yaml) ·
  [video_samples.csv](../../02_data_engineering/video_samples.csv)
- **Modifica:** `configs/sources.yaml::download_budget.deny_extensions` solo para los archivos exactos de la muestra (`.ts`, `.mp4`).

> **Resultado de la fase 1 (2026-11-16): positivo.** La llama es medible; duración del video a ≤ 1 s del investigador; radio estable ~17 mm en llama normal; el núcleo de hollín se apaga ~17 s antes de la autoextinción. Ver RESEARCH_LOG R16.

> **Fase 2 preparada (2026-11-16):** bucket `gs://flamesafe-psi-video`, imagen en Artifact Registry, cuenta de servicio con permisos solo sobre el bucket y Cloud Run Job `flamesafe-video` (335 tareas) **creado sin ejecutar**. Manifiesto [configs/video_manifest.yaml](../../../configs/video_manifest.yaml) (patrón solo para `.ts`/`.mp4` de PSI-159; los `.zip` siguen prohibidos). La ejecución espera la alerta de presupuesto. Procedimiento: [deploy/VIDEO_JOB.md](../../../deploy/VIDEO_JOB.md).

> **Fase 2 ejecutada (2026-11-16):** 335 de 335 videos procesados en ~11 min (`flamesafe-video-bfp5f`), resultados en `gs://flamesafe-psi-video/cfig-v2` y en silver `acme__video_features`. Hallazgos en RESEARCH_LOG R17–R20.

## Contexto
La ecuación de duración (RESEARCH_LOG R2, R9, R13) supone que el radio de la llama esférica escala con `ṁ/L`. Hoy ese radio
solo se infiere. PSI guarda video de cada prueba de CFI-G (336 grabaciones `.ts` del enlace de bajada, ~82 GB; mediana 233 MB)
y secuencias de imágenes científicas en `.zip` (~2 TB solo en CFI-G). Nadie del equipo ha abierto uno: no sabemos la
resolución, el encuadre ni si la llama es medible. Procesar todo sin comprobarlo sería gastar a ciegas.

## Decisión

**Fase 1 — factibilidad local (esta decisión).**
- Descargar **4 archivos exactos** (~520 MB): tres `.ts` representativos (llama normal autoextinguida, inversa autoextinguida,
  normal cortada por flujo) y el único `.mp4` del registro. Comando: `flamesafe video-samples`. Lista cerrada, sin patrones.
- Revisar formato, cuadros por segundo, encuadre y visibilidad de la llama; prototipar la medición del radio contra la línea de
  tiempo ya validada de las series (ADR-0005).

**Fase 2 — procesamiento en Google Cloud (solo si la fase 1 es positiva).**
- Proyecto `flamesafe-psi`, región `us-west1`. Servicios habilitados el 2026-11-16: Cloud Run, Artifact Registry, Cloud Build y
  Cloud Storage. Sin máquinas virtuales.
- Un **Cloud Run Job** con una tarea por prueba: descarga el video desde PSI, lo procesa y escribe una tabla pequeña por prueba en
  un bucket. El video no se conserva (regla de ciclo de vida). Cuenta de servicio con permisos solo sobre ese bucket.
- Los resultados entran al pipeline como tabla silver; la web y la API solo leen gold. Ninguna credencial en el repo ni en el frontend.

## Alternativas consideradas
| Opción | Pros | Contras |
|---|---|---|
| Procesar los 336 videos en la nube de entrada | más rápido si todo sale bien | costo y tiempo sin saber si el video sirve |
| Máquina virtual en Compute Engine | control total | cobra encendida; fácil olvidarla; no escala por prueba |
| Secuencias `.zip` de la cámara científica | mejor calidad | ~1.4 GB por prueba, ~2 TB en CFI-G; solo si el video no alcanza |
| **Muestra local de 4 archivos y luego Cloud Run Jobs** | decide con evidencia; paga solo el tiempo de cómputo | un paso más |

## Consecuencias
- Bronze local crece ~0.5 GB (no versionado). El manifiesto núcleo y la extensión de ADR-0005 no cambian.
- Si la fase 1 falla (llama no visible o sin escala), se documenta como resultado negativo y la fase 2 no se ejecuta.
- Antes de la fase 2: alerta de presupuesto en la consola, nuevo manifiesto con su presupuesto y actualización de este ADR.
