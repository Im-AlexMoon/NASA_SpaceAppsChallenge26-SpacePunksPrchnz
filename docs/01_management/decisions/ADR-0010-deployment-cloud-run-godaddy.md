# ADR-0010 — Despliegue: backend Python en Cloud Run y web Next.js en GoDaddy

- **Estado:** **Aceptado (2026-11-15)**; **la parte web (GoDaddy) queda reemplazada por [ADR-0011](ADR-0011-web-on-vercel-static-content.md)**
  (Vercel). El backend en Cloud Run sigue vigente.
- **Tarea relacionada:** APP-08 · arquitectura en [ADR-0004](ADR-0004-rag-web-architecture.md) · infraestructura existente en
  [deploy/VIDEO_JOB.md](../../../deploy/VIDEO_JOB.md)
- **Nota de numeración:** ADR-0006 sigue reservado para las decisiones PHY y la unidad de la tasa de FLEX.

## Contexto
ADR-0004 separa la web (Next.js, GoDaddy) del backend Python (FastAPI: RAG, consultas parametrizadas, ranking y lecturas M-01 v2) y
permitía un host Python distinto. El backend necesita Python 3.12, Cantera, DuckDB, el snapshot de evidencia del RAG y, si se activa la
generación, los pesos del modelo de embeddings. Un hosting web compartido no ofrece eso. El proyecto `flamesafe-psi` de Google Cloud
ya existe (Cloud Run, Artifact Registry, Cloud Build, Cloud Storage, alerta de presupuesto de 2,000 MXN/mes).

## Decisión
| Capa | Dónde | Cómo |
|---|---|---|
| API Python | **Cloud Run** (`flamesafe-psi`, `us-west1`), servicio `flamesafe-api` | Imagen de `deploy/Dockerfile.api` construida en Cloud Build; 1 instancia máxima y 1 worker (ledger local, ADR-0004); `min-instances` 0 en pruebas, 1 durante la demo |
| Snapshot de evidencia y pesos | Bucket privado (p. ej. `gs://flamesafe-psi-evidence`) montado en solo lectura en `/evidence` (volumen de Cloud Storage de Cloud Run) | `rag/CURRENT` + bundle validado + `embedding-model/`; se actualiza subiendo un bundle nuevo y cambiando `CURRENT` (rollback igual) |
| Secretos | **Secret Manager** → variables de entorno del servicio | `FLAMESAFE_API_TOKEN`, claves de Gemini/OpenAI; nunca en la imagen ni en el repo |
| Web Next.js | **GoDaddy** (plan con Node.js ≥ 22), dominio propio | `npm ci && npm run build && npm start`; `FLAMESAFE_BACKEND_URL` = URL de Cloud Run; el token del backend vive solo en el servidor Node |
| Respaldo de la web | Cloud Run, servicio `flamesafe-web` + DNS en GoDaddy | Si el plan de GoDaddy no corre Node.js ≥ 22 o limita los tiempos de respuesta |

Controles mínimos antes de publicar: TLS (Cloud Run y GoDaddy), token de acceso al dashboard distinto del token del backend, generación
LLM **desactivada por defecto** (modo evidencia), límites de solicitudes de ADR-0004 y alerta de presupuesto activa.

## Alternativas consideradas
| Opción | Pros | Contras |
|---|---|---|
| Todo en GoDaddy | un proveedor | no corre Python con Cantera/DuckDB/embeddings de forma fiable |
| Todo en Cloud Run (web + API) | una consola, despliegue reproducible | el dominio y la marca ya están en GoDaddy; se conserva como respaldo |
| **API en Cloud Run + web en GoDaddy** | usa la infraestructura ya montada; la web queda donde está el dominio | dos plataformas; hay que verificar Node.js en el plan de GoDaddy |

## Consecuencias
- El ledger SQLite del RAG vive en el disco efímero de la instancia: con generación desactivada no importa; si se activa, los
  límites diarios se reinician con cada instancia nueva. Revisar antes de habilitar la generación pública (Cloud SQL o Firestore).
- Cantera entra al extra `api` (ya hecho) porque las lecturas calculan la termoquímica de cada atmósfera.
- El artefacto M-01 v2 va dentro del paquete (`src/flamesafe/models/artifacts/`), así que viaja con la imagen.
- Pendientes de verificación: runtime, puerto y timeout del plan de GoDaddy; latencia de arranque en frío de Cloud Run con el snapshot montado.
