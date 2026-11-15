# Visión del producto — qué nos distingue

> **Documento vigente de visión (2026-11-15).** Define *qué* debe comunicar la aplicación y *por qué*. No cambia la arquitectura:
> el *cómo* (Next.js/Node.js, backend Python, RAG, hosting) sigue en [RAG_IMPLEMENTATION_PLAN.md](../03_data_science/RAG_IMPLEMENTATION_PLAN.md)
> y [ADR-0004](../01_management/decisions/ADR-0004-rag-web-architecture.md). La decisión de alcance que introduce esta visión está en
> [ADR-0007](../01_management/decisions/ADR-0007-evidence-tiers-in-dashboard.md). Idioma de la UI: inglés.

## 1. La idea en una frase

**No decimos "qué tan peligroso es el fuego en el espacio"; decimos cuánto sabe NASA realmente, con qué nivel de evidencia, y
dónde no sabe nada.**

NASA va a usar atmósferas más ricas en oxígeno y de menor presión en la Luna y Marte. Tiene 24 investigaciones de combustión en
microgravedad. La aplicación responde tres preguntas, en este orden:

1. **¿Qué dicen los datos sobre esta atmósfera?** — con el nivel de evidencia a la vista.
2. **¿Qué ley física explica lo observado?** — una ecuación que se puede leer, no una caja negra.
3. **¿Qué experimento falta?** — la brecha concreta y la prueba que la cerraría.

## 2. Los cuatro diferenciadores

| # | Diferenciador | Qué ve el usuario | Evidencia que ya tenemos |
|---|---|---|---|
| 1 | **Niveles de evidencia, siempre visibles** | Cada número lleva una etiqueta: *Medido cerca*, *Interpolado por el modelo* o *Sin evidencia* | Regla de dominio de M1; la base lunar no tiene ninguna prueba cercana |
| 2 | **Una ley física transferible** | La ecuación de duración de la llama, con sus cuatro términos explicados y su prueba en otra campaña | Ajustada solo con CFI-G predice Flame Design sin reajuste: índice C 0.93 (IC 0.80–0.96) |
| 3 | **Mapa de brechas y siguiente experimento** | Dónde hay pruebas y dónde no en el espacio O₂–presión, sobre las atmósferas de exploración; la prueba recomendada | Hueco de O₂ 0.24–0.33 en llamas normales; 0 pruebas cerca de 30 % O₂ y 70 kPa |
| 4 | **Del dato crudo al hallazgo, trazable** | De cada cifra se llega a las pruebas, al archivo de NASA y al código que la calculó | Procedencia por fila, 655 series temporales reducidas con un detector validado al 99.6 % |

Lo que **no** nos distingue y por eso no encabeza la aplicación: un chat que resume artículos, un catálogo de investigaciones o un
modelo que extrapola a la Luna sin advertencias. Los dos primeros existen como apoyo; el tercero no debe existir.

## 3. Los tres niveles de evidencia

| Nivel | Etiqueta en la UI | Cuándo aplica | Qué se muestra |
|---|---|---|---|
| A | **Measured nearby** | ≥ 5 pruebas reales de ≥ 2 días a ±0.05 de O₂ y ±25 % de presión | Primero el dato observado (tasa, mediana, n, días); el modelo va al lado como comparación |
| B | **Model interpolation** | Sin pruebas cercanas, pero dentro del rango probado de cada variable física | El valor del modelo con su intervalo, la advertencia "no hay pruebas cercanas" y las pruebas más próximas |
| C | **No evidence** | Fuera del rango probado, otra geometría o combustible, o gravedad parcial | Ningún número. Se explica qué falta y qué experimento lo daría |

Reglas fijas: la gravedad parcial (Luna, Marte) es siempre nivel C para el efecto de la gravedad; lo que se muestra es
microgravedad con la atmósfera de ese hábitat, y se dice así. Un resultado sin revisión de física lleva la marca **Candidate**.

## 4. Recorrido principal

La página de entrada no es un catálogo: es la pregunta del ingeniero.

1. **Atmosphere Explorer** (antes Habitat Risk Explorer) — *la página protagonista*. El usuario elige un hábitat o mueve O₂ y
   presión. Ve el nivel de evidencia, lo observado, la lectura del modelo si procede y las pruebas reales que la respaldan.
2. **The Burn-Time Law** — la ecuación de duración término por término (temperatura de llama, presión, caudal, posición de la
   llama), con la gráfica de transferencia entre campañas y lo que la ley *no* cubre.
3. **Knowledge Gaps** — mapa de cobertura con las atmósferas de exploración superpuestas y la tarjeta "experimento siguiente".
4. **Findings** — tarjetas con afirmación, evidencia (n, efecto, intervalo), física y estado de revisión, incluidos los negativos.
5. **Investigations & Compare**, **Ask the Data** (RAG) y **Methods & Sources** — apoyo, navegación y trazabilidad.

## 5. Contenido listo para la primera versión (todo marcado *Candidate* hasta PHY)

| Bloque | Contenido | Fuente |
|---|---|---|
| Atmosphere Explorer | Cabina ISS: nivel A, duración observada 9 s (modelo 13 s). Exploración 34 % / 56.5 kPa: nivel A en el borde, observada 63 s (modelo ~95 s). **Base lunar 30 % / 70 kPa: nivel B, ~60 s (IC 90 % 47–75), sin pruebas cercanas** | RESEARCH_LOG R12–R14 |
| The Burn-Time Law | ln t = 15.8 − 13.4·(1000/Tad) − 0.41·ln p − 1.20·ln ṁ + 2.12·ln L, con IC y prueba de transferencia | RESEARCH_LOG R9, R12 |
| Knowledge Gaps | Hueco de O₂ 0.24–0.33; 0 pruebas junto a la base lunar; sin datos de gravedad parcial; sólidos fuera de gold | M-01, RESEARCH_LOG |
| Findings | Censura por límite térmico, oscilación previa a la extinción (preliminar), llamas frías tras la "autoextinción" | RESEARCH_LOG R5, R6, R10, R11 |

## 6. Lo que la aplicación nunca hace
- Presentar una frecuencia experimental como riesgo de misión.
- Mostrar un número para gravedad parcial, sólidos o combustibles no ensayados.
- Dar una predicción sin su nivel de evidencia, su intervalo y sus pruebas de respaldo.
- Llamar "tiempo disponible" a la duración de una llama de laboratorio.
- Ocultar un resultado negativo.

## 7. Dependencias con el plan técnico
- El RAG responde con los mismos niveles: si la pregunta cae en nivel C, explica la brecha en lugar de improvisar.
- El backend expone la lectura por atmósfera como consulta parametrizada y versionada (no como chat libre).
- La publicación de cada bloque depende del estado de revisión PHY, igual que los findings.
