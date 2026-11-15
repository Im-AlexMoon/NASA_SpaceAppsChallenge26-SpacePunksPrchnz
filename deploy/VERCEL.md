# Despliegue de la web en Vercel (ADR-0011)

## Una vez
1. En vercel.com → *Add New… → Project* → importar `Im-AlexMoon/NASA_SpaceAppsChallenge26-SpacePunksPrchnz`.
2. **Root Directory:** `web` · Framework: Next.js (autodetectado) · Node.js 22.x o superior.
3. Variables de entorno (Production), solo si se publica *Ask the data*:
   - `FLAMESAFE_BACKEND_URL` = URL del servicio `flamesafe-api` en Cloud Run (ADR-0010)
   - `FLAMESAFE_API_TOKEN` = token del backend (Secret Manager)
   - `FLAMESAFE_WEB_ACCESS_TOKEN` = token que se reparte a quien use el chat
   - `NEXT_PUBLIC_SITE_URL` = URL pública (para metadatos y tarjetas de redes)
4. *Deploy*. Cada push a `main` vuelve a desplegar; cada PR recibe una URL de vista previa.

Desde la terminal (alternativa): `npm i -g vercel`, `cd web`, `vercel link`, `vercel --prod`.

## Al cambiar contenido científico
```bash
uv run flamesafe web-content      # reescribe web/src/content/*.json
cd web && npm run build           # verifica
```
Hacer commit de los JSON y push: Vercel publica el contenido nuevo.

## Sin backend
Todas las páginas salvo *Ask the data* funcionan sin variables de entorno. El chat muestra "Request unavailable (503)" hasta que la
API esté desplegada.

## Backend para *Ask the data* (desplegado el 2026-11-15)
- Servicio Cloud Run `flamesafe-api` (`us-west1`, proyecto `flamesafe-psi`), imagen `deploy/Dockerfile.api` (modo léxico, solo el
  extra `api`), construida con `gcloud builds submit --config deploy/cloudbuild.api.yaml .`
- Evidencia: `gs://flamesafe-psi-evidence/rag/` (privado, montado en `/evidence` en solo lectura); actualizar = subir un bundle nuevo
  y cambiar `rag/CURRENT`.
- Token del backend: secreto `flamesafe-api-token` en Secret Manager; cuenta de servicio `flamesafe-api` (lector del secreto y del bucket).
- Valores para Vercel:
  ```powershell
  gcloud run services describe flamesafe-api --region=us-west1 --project=flamesafe-psi --format="value(status.url)"
  gcloud secrets versions access latest --secret=flamesafe-api-token --project=flamesafe-psi
  ```
