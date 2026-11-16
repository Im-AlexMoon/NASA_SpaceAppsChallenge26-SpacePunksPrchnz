# Entrega al frontend — luz verde (2026-11-15)

> Consultar el [procedimiento de release](../06_submission/RELEASE_PROCEDURE.md) para reconstruir el bundle y verificar los cambios de ciencia.

> **Actualización 2026-11-15 (ADR-0011):** el frontend ya está construido en `web/` y se aloja en Vercel. Las páginas leen el
> contenido de `web/src/content/*.json` (generado con `flamesafe web-content`) en lugar de llamar a la API; solo *Ask the data*
> usa el gateway `/api/backend/*`. Las reglas de presentación de abajo siguen vigentes y la UI las cumple.

> Qué contenido ya existe, de dónde sale y cómo se consume. Visión y reglas de producto: [PRODUCT_VISION.md](PRODUCT_VISION.md) ·
> lecturas del modelo: [ADR-0007](../01_management/decisions/ADR-0007-evidence-tiers-in-dashboard.md) · despliegue:
> [ADR-0010](../01_management/decisions/ADR-0010-deployment-cloud-run-godaddy.md). UI en inglés. Todo el contenido científico está
> **revisado PHY (Alexander Moon)**; el campo `status` de cada respuesta lo dice y la UI debe mostrarlo.

## Endpoints nuevos (backend Python, detrás del gateway Next.js `/api/backend/...`)

Contrato completo en `contracts/openapi.json`; tipos generados en `web/src/generated/api.d.ts` (`npm run generate`).

| Endpoint | Para qué página | Qué devuelve (campos clave) |
|---|---|---|
| `GET /v1/status` | todas | `publication.{ranking,findings,model_readings}.{enabled,status}`, `model_readings_enabled`, `build_id` |
| `GET /v1/ranking/profiles` | Investigations | `profiles.{key}.{label,environment,weights}`, `dimensions.{key}` (descripción de cada dimensión) |
| `POST /v1/ranking` `{profile}` o `{weights, environment}` | Investigations | `rows[]`: `rank, psi_id, acronym, title, score`, las 7 dimensiones y `contrib_*` (barras apiladas); `sensitivity` (solo con perfil) |
| `GET /v1/readings/atmospheres` | Atmosphere Explorer (presets) | `readings[]`: `key, label, gravity_g, tier, tier_label, prediction, nearby, physics, support, caveats, gravity_effect?` |
| `POST /v1/readings/atmosphere` `{xo2, p_kpa, fuel?, x_fuel?, m_fuel_mg_s?, gravity?}` | Atmosphere Explorer (sliders) | igual que un elemento de `readings[]` |
| `GET /v1/findings` | Insights, Knowledge Gaps | `findings[]`: `id, title, claim, pillar, confidence, status, key_numbers[], evidence, physics, limits, page, next_experiment?` |

Los endpoints existentes del RAG (`/v1/chat`, `/v1/data/query`, `/v1/investigations`, `/v1/sources`, `/v1/evidence`) no cambian.

## Reglas de presentación que la UI debe respetar

1. **Nivel de evidencia siempre visible** en cada lectura: `A · Measured nearby`, `B · Model interpolation`, `C · No evidence`.
2. **Nivel A:** mostrar primero `nearby` (n, días, tasa de ignición observada, mediana observada) y el modelo como comparación.
3. **Nivel B:** valor con su IC 90 % (`median_burn_s_90ci`) y el primer `caveat` ("No real test near this atmosphere...").
4. **Nivel C:** `prediction` es `null` → no inventar ni interpolar en el cliente; mostrar `reason` y el experimento que falta (F-04).
5. **Gravedad:** si existe `gravity_effect`, banner fijo con su `note` (nivel C). Nunca dibujar curvas entre µg y 1 g.
6. Todo número lleva unidad y procedencia (PSI-ID, artefacto o documento). Tad/Zst se etiquetan como "calculated".
7. Si `publication.<bloque>.enabled` es `false`, ocultar el bloque; si `status` es `candidate`, mostrar la insignia *Candidate*.

## Contenido listo por página

| Página (PRODUCT_VISION §4) | Contenido | Fuente |
|---|---|---|
| **Atmosphere Explorer** | 6 atmósferas de referencia + atmósfera libre; ISS A (13 s; observado 9 s), exploración A (95 s; observado 62.5 s), base lunar B (60 s, 48–72), traje C | `/v1/readings/*`, model card M-01 |
| **The Burn-Time Law** | la ecuación, sus 4 términos con IC y su prueba de transferencia (C 0.93) | F-02, `/v1/findings` |
| **Knowledge Gaps** | hueco de O₂ 24–33 %, 0 pruebas cerca de la base lunar, sin gravedad parcial; experimento recomendado | F-04, REC-02, REC-05 |
| **Insights** | F-01..F-05 (incluye el resultado negativo del hollín) | `/v1/findings` |
| **Investigations** | ranking MCDA con 5 perfiles y pesos ajustables, sensibilidad | `/v1/ranking*`, RANKING_RESULTS.md |
| **Methods & Sources** | pipeline, ADR-0005/0009 (series y video), literatura verificada, atmósferas con citas | docs/04_physics, RESEARCH_LOG |
| **Ask the Data** | RAG con 11 documentos revisados en el corpus | `/v1/chat` |

## Visuales sugeridos (datos ya disponibles)
- Curva duración–O₂ con banda IC 90 % y puntos observados: iterar `POST /v1/readings/atmosphere` sobre `xo2` (y dos presiones).
- Mapa O₂–presión de cobertura con las atmósferas de referencia superpuestas: `GET /v1/data/query` (`list_gas_tests`) + presets.
- Barras apiladas del ranking con `contrib_*`.
- Secuencias reales de llamas de la ISS: miniaturas en `gs://flamesafe-psi-video/cfig-v2/thumbs/` (PSI-159, licencia CC0; crédito NASA).
