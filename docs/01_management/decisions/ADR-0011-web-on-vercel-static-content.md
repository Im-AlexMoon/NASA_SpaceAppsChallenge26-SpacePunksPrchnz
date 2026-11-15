# ADR-0011 — Web en Vercel con contenido científico estático; backend solo para el RAG

- **Estado:** **Aceptado (2026-11-15)** por el responsable del proyecto (Alexander Moon): "No tenemos GoDaddy, usa Vercel para hostear la app".
- **Reemplaza:** la fila "Web Next.js → GoDaddy" (y su respaldo) de [ADR-0010](ADR-0010-deployment-cloud-run-godaddy.md). El backend en
  Cloud Run, el bucket de evidencia y Secret Manager de ADR-0010 siguen vigentes.
- **Tareas:** APP-08 (despliegue), APP-02…APP-07 (páginas)

## Contexto
El equipo no tiene GoDaddy. Vercel aloja Next.js 16 de forma nativa (rutas estáticas en CDN y funciones Node para `/api/backend/*`).
El contenido que da valor al dashboard (ranking MCDA, hallazgos F-01..F-05, lecturas M-01 v2) es determinista y está revisado por PHY:
no cambia entre solicitudes. Hacerlo depender de un backend con arranque en frío arriesga la demo sin ganar nada.

## Decisión
| Capa | Dónde | Cómo |
|---|---|---|
| Web (todas las páginas) | **Vercel**, proyecto con *Root Directory* `web/` | `next build` estándar; dominio `*.vercel.app` (o propio) |
| Contenido científico | **JSON estático dentro del build** (`web/src/content/*.json`) | `flamesafe web-content` lo genera con las mismas funciones de la API (`ContentService`, `readings.read`, `mcda.dimension_scores`). La malla del explorador cubre 37 × 16 puntos (O₂ 0.14–0.50 cada 0.01; 16 presiones de 30 a 101.3 kPa) en microgravedad con el quemador CFI-G típico |
| Ranking con pesos propios | Navegador | misma fórmula publicada `score = Σ w_d·s_d / Σ w_d` sobre los puntajes por dimensión exportados |
| Ask the data (RAG) | Función de Vercel `/api/backend/*` → API en **Cloud Run** (ADR-0010) | variables `FLAMESAFE_BACKEND_URL`, `FLAMESAFE_API_TOKEN`, `FLAMESAFE_WEB_ACCESS_TOKEN` en Vercel (solo servidor) |

Regla: cualquier cambio de un hallazgo, del artefacto M-01, de `configs/ranking.yaml` o de `configs/publication.yaml` exige volver a correr
`flamesafe web-content` y desplegar. El build no inventa ni interpola: el cliente solo elige puntos de la malla ya calculada.

## Alternativas
| Opción | Pros | Contras |
|---|---|---|
| Web en Vercel llamando a la API para todo | una sola fuente en vivo | arranque en frío y costo de Cloud Run en cada visita; la demo depende del backend |
| Web en Cloud Run | una consola | más configuración; sin CDN de Vercel |
| **Vercel + contenido estático + API solo para el RAG** | demo robusta, rápida, gratuita en el plan Hobby | hay que regenerar el JSON al cambiar contenido (documentado) |

## Consecuencias
- Las páginas públicas no requieren token. *Ask the data* sigue protegido por el token del dashboard (ADR-0004).
- Los endpoints de contenido de la API (`/v1/ranking*`, `/v1/readings/*`, `/v1/findings`) siguen existiendo para terceros y pruebas.
- Despliegue: `deploy/VERCEL.md`. El primer despliegue lo hace el responsable con su cuenta de Vercel.
