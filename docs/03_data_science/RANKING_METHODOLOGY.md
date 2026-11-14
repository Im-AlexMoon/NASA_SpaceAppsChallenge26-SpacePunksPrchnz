# Metodología de ranking de investigaciones (RQ5)

> Tarea DS-07 (con PHY-02). El reto pide *rankear*: lo hacemos con un análisis multicriterio (MCDA) **transparente y ajustable**
> por el usuario, no con una caja negra.

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
