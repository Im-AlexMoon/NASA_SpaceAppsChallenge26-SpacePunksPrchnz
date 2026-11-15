# Metodología de ranking de investigaciones (RQ5)

> Tarea DS-07 (con PHY-02) · **Implementado y revisado PHY (Alexander Moon), 2026-11-15.** El reto pide *rankear*: lo hacemos con
> un análisis multicriterio (MCDA) **transparente y ajustable** por el usuario, no con una caja negra. Código: `src/flamesafe/ranking/mcda.py`
> (tests en `tests/unit/test_ranking.py`); pesos: `configs/ranking.yaml`; resultados: [RANKING_RESULTS.md](RANKING_RESULTS.md);
> API: `GET /v1/ranking/profiles`, `POST /v1/ranking` (perfil o pesos propios).

## 1. Dimensiones

| Dimensión | Qué mide | Fuente del puntaje |
|---|---|---|
| **Relevancia por pilar** (prevención / detección / supresión) | qué tanto informa ese pilar | PHY (rúbrica) + extracción asistida por LLM verificada |
| **Relevancia por entorno** (nave, estación, base lunar, rover, Marte) | cercanía de condiciones (O₂, presión, flujo, materiales) | reglas sobre gold + PHY |
| **Calidad de evidencia** | tipo de dato (medido > calculado > log), tamaño muestral, acceso | triage R2–R5 |
| **Utilidad para modelado** | variables de condición + resultado medido | triage R4 |
| **Madurez científica** | publicaciones revisadas por pares | conteo de publicaciones con DOI |

## 2. Cálculo
`score(inv, perfil) = Σ_d w_d(perfil) · s_d(inv)`, con `s_d ∈ [0,1]`. Perfiles predefinidos de pesos:
*Ingeniero de hábitat lunar*, *Diseñador de supresión*, *Investigador de detección*, *Estudiante* (equilibrado).
El usuario puede mover los pesos en el dashboard y ver cómo cambia el orden (análisis de sensibilidad visible).

## 3. Extracción asistida por IA ("SI-powered")
El LLM propone, por investigación, etiquetas (pilar, entorno, combustible, variables, sensores) **con la cita del texto PSI**
que la soporta. Un humano (DS/PHY) acepta o corrige → se guarda en `configs/` como dato versionado. El dashboard indica qué
etiquetas fueron verificadas.

## 4. Validación
- Revisión de cordura por PHY del top-5 de cada perfil.
- Estabilidad: el top-5 no debe cambiar drásticamente con ±20% en un solo peso (si cambia, se reporta).

## 5. Implementación (2026-11-15)

Puntajes por dimensión, todos en [0, 1] y trazables a `configs/triage.yaml` y a la tabla gold `investigations`:

| Dimensión | Fórmula |
|---|---|
| Pilar (prevención / detección / supresión) | R1/3 × 1.0 si es el primer pilar listado en triage, × 0.7 si es secundario, 0 si no aplica |
| Entorno del perfil | 1 si la investigación lista ese entorno (× 0.6 si es de tierra), 0 si no |
| Calidad de evidencia | media(R2, R3, R5)/3 × factor de acceso (disponible 1.0; solo tabla experimental 0.85) |
| Utilidad para modelado | R4/3 |
| Madurez científica | ln(1 + publicaciones con DOI) / ln(1 + máximo) |

Perfiles: ingeniero de hábitat lunar, diseñador de supresión, investigador de detección, planificador de misión a Marte y estudiante.
La respuesta de la API incluye la contribución de cada dimensión al puntaje (para la gráfica de barras apiladas) y la sensibilidad.

**Validación (§4):** con ±20 % en un peso a la vez, el top-5 cambia como máximo en una investigación en todos los perfiles; el perfil de
detección no cambia nunca. Revisión de cordura del top-5 por PHY: lunar → Flame Design, FLEX, CFI-G, CFI, BASS-II (las cuatro con datos
gold más el estudio de sólidos con O₂ y flujo variados); supresión → FLEX, CFI, FLEX-2; detección → SAFFIRE-I, SAME-R, SAFFIRE-III, SAME,
SPICE. Coherente con lo que cada experimento midió.

**Pendiente (§3):** la extracción asistida por IA de etiquetas no se implementó; las etiquetas vienen del triage verificado por DE y PHY.

