# Especificación del dashboard

> **Visión vigente del producto:** [PRODUCT_VISION.md](PRODUCT_VISION.md) (qué nos distingue, niveles de evidencia y recorrido principal) y [ADR-0007](../01_management/decisions/ADR-0007-evidence-tiers-in-dashboard.md).

> **Especificación histórica.** La web vigente usa Next.js en Vercel y un backend FastAPI en Cloud Run. Consultar [RELEASE_PROCEDURE.md](../06_submission/RELEASE_PROCEDURE.md) para configuración, ciencia publicada y verificación.

> Tareas APP-01 → APP-08. Cierra en **G6**. Código: `app/` (Streamlit multipage). Idioma de la UI: **inglés** (jurado internacional).

## 1. Audiencias y su pregunta principal

| Audiencia | Pregunta | Página de entrada |
|---|---|---|
| Ingeniero aeroespacial | "¿Es segura esta atmósfera / este flujo para mi hábitat?" | Habitat Risk Explorer |
| Investigador | "¿Qué datos existen sobre X y cómo se comparan?" | Investigation Explorer / Compare |
| Profesor / estudiante | "¿Por qué el fuego es distinto en el espacio y qué aprendimos?" | Mission Brief / Insights |

## 2. Páginas

| # | Página | Contenido | Depende de | Tarea |
|---|---|---|---|---|
| 0 | **Home** | Propuesta de valor, 3–4 KPIs (24 investigaciones, n pruebas analizadas, findings, modelos), navegación por audiencia | G2 | APP-02 |
| 1 | **Mission Brief** | Por qué importa (Apollo 1, Mir, Artemis II), física en 60 s (vela 1 g vs µg), atmósferas de hábitat | PHY-01/07 | APP-03 |
| 2 | **Investigation Explorer** | Catálogo filtrable (pilar, entorno, combustible, hardware, estado de acceso) + **ranking MCDA con pesos ajustables** + ficha por investigación | DE-03, DS-07 | APP-03 |
| 3 | **Compare** | 2–4 investigaciones lado a lado: objetivos, combustibles, condiciones (O₂, P, flujo), variables, sensores; matriz de similitudes/diferencias | DATA_DICTIONARY | APP-03 |
| 4 | **Insights** | Findings como tarjetas: afirmación → figura interactiva → evidencia (n, efecto, IC) → física → confianza → fuente | G3 | APP-04 |
| 5 | **Habitat Risk Explorer** ⭐ | Sliders: XO₂, P total, flujo, régimen de gravedad (µg / Luna / Marte / 1 g). Presets de atmósferas. Salida: P(llama sostenida) ± IC, posición sobre la frontera O₂–P, **badge de extrapolación**, findings y recomendaciones relacionadas | G4 | APP-05 |
| 6 | **Ask the Data** | Chat RAG; citas clicables que abren la investigación o el finding; preguntas sugeridas | G5 | APP-06 |
| 7 | **Methods & Sources** | Pipeline, procedencia, reporte de calidad, limitaciones, model cards, créditos NASA/PSI, uso de IA, licencias | G2 | APP-07 |

## 3. Componentes reutilizables (`app/components/`)
- `source_chip(psi_id, file, doi)` — chip de fuente en toda figura.
- `evidence_badge(level)` — Medido / Calculado / Log · Confianza alta/media/baja.
- `extrapolation_banner(in_domain: bool, reason)`.
- `finding_card(finding_id)`.
- Paleta y tipografía consistentes; modo claro/oscuro.

## 4. Requisitos no funcionales
- Carga de página < 5 s (datos gold precargados con `st.cache_data`).
- Ninguna figura sin unidades ni fuente.
- Funciona sin API key (el chat muestra aviso y respuestas en caché para las preguntas sugeridas).
- Despliegue: Streamlit Community Cloud desde `main` (alternativa: HF Spaces).

## 5. Wireframes
_(APP-01: pegar aquí bocetos o capturas aprobadas en el sync de H+8)_
