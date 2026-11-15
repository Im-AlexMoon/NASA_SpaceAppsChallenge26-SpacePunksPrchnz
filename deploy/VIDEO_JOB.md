# Cloud Run Job de video (ADR-0009, fase 2)

Mide cada video de operaciones de CFI-G (335 archivos, ~81.6 GB en PSI) sin descargarlo a ninguna laptop. Cada tarea baja
**un** video a su disco temporal, lo mide (`flamesafe video-task`), escribe resultados pequeños en el bucket y borra el video.

## Recursos creados (2026-11-15, proyecto `flamesafe-psi`, región `us-west1`)

| Recurso | Nombre | Notas |
|---|---|---|
| Bucket | `gs://flamesafe-psi-video` | acceso uniforme, acceso público bloqueado; solo resultados (parquet, json, jpg) |
| Artifact Registry | `us-west1-docker.pkg.dev/flamesafe-psi/flamesafe` | imagen `video-job:latest` |
| Cuenta de servicio | `flamesafe-video-job@flamesafe-psi.iam.gserviceaccount.com` | `roles/storage.objectAdmin` **solo sobre el bucket** |
| Cloud Run Job | `flamesafe-video` | 335 tareas, 20 en paralelo, 2 vCPU, 4 GiB, 30 min por tarea, 2 reintentos |

Configuración en [configs/video_manifest.yaml](../configs/video_manifest.yaml); lista de archivos (índice de tarea = fila) en
[video_manifest.csv](../docs/02_data_engineering/video_manifest.csv). Sin credenciales en el repo ni en la imagen.

## Reconstruir y actualizar

```powershell
uv run flamesafe video-manifest                       # regenera el lock si PSI cambió
gcloud builds submit . --config=deploy/cloudbuild.video.yaml --project=flamesafe-psi --region=us-west1
gcloud run jobs update flamesafe-video --region=us-west1 --image=us-west1-docker.pkg.dev/flamesafe-psi/flamesafe/video-job:latest --tasks=<filas del lock>
```

`.gcloudignore` evita subir `data/`, notebooks y la web al contexto de Cloud Build.

## Ejecutar (solo con alerta de presupuesto activa)

```powershell
# prueba de humo: solo las 3 primeras filas del lock
gcloud run jobs execute flamesafe-video --region=us-west1 --tasks=3 --wait
# todas las pruebas (las tareas ya procesadas se saltan: el resultado es idempotente)
gcloud run jobs execute flamesafe-video --region=us-west1
# seguimiento
gcloud run jobs executions list --job=flamesafe-video --region=us-west1
```

## Traer los resultados al pipeline

```powershell
uv run flamesafe video-collect --source gs://flamesafe-psi-video/cfig-v2   # -> silver acme__video_features
```

`gcloud auth application-default login` debe estar hecho en la máquina que corre `video-collect`.

## Probar localmente sin nube

```powershell
uv sync --extra video
uv run flamesafe video-task --index 119 --output ./artifacts/video --local-file "<ruta a un .ts en bronze>"
```

## Costo y limpieza
- Se paga el cómputo de Cloud Run mientras corren las tareas y el almacenamiento de resultados (megabytes). Revisar el costo
  estimado en la calculadora de Google Cloud antes de la ejecución completa; no se registra aquí una cifra sin verificar.
- El job, el bucket y el registro no cuestan nada relevante en reposo. Para borrar todo:
  `gcloud run jobs delete flamesafe-video --region=us-west1`, `gcloud storage rm -r gs://flamesafe-psi-video`,
  `gcloud artifacts repositories delete flamesafe --location=us-west1`.
