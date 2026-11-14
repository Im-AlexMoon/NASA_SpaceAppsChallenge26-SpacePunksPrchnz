# Protocolo de EDA y análisis estadístico reproducible

> Tareas DS-04 → DS-06. Cierra en **G3**.

## 1. Ciclo iterativo por RQ (timebox 60–90 min por iteración)

1. **Perfil** — conteos, faltantes por columna (y sus flags), rangos, unidades, duplicados, balance de clases.
2. **Univariado** — distribuciones; detectar valores físicamente imposibles → reportar a DE (no corregir en el notebook).
3. **Bivariado / condicional** — resultado vs. cada condición, estratificado por combustible / investigación / campaña.
4. **Confusores** — ¿la variable de interés está correlacionada con otra condición (p. ej. O₂ con presión por diseño experimental)?
   Mapear el *diseño experimental*: qué se varió y qué se mantuvo fijo.
5. **Prueba** — test pre-especificado (abajo) con tamaño de efecto e IC.
6. **Interpretación** — borrador del finding → revisión PHY.

## 2. Reglas estadísticas

- **Pre-registrar** en el notebook (celda markdown) la hipótesis y el test *antes* de correrlo.
- Reportar siempre: n, estadístico, **tamaño de efecto**, **IC 95%** (bootstrap si no hay forma cerrada), p-valor.
- Comparaciones múltiples: Holm-Bonferroni o Benjamini-Hochberg (declarar cuál).
- Datos agrupados (varias pruebas por día/campaña): usar modelos con efecto de grupo o bootstrap por grupos.
- n pequeño: preferir tests no paramétricos o exactos; decir explícitamente cuando la potencia es baja.
- Correlación ≠ causalidad, salvo que el diseño experimental controle la variable (decirlo).
- Nunca mezclar variables no comparables (ver matriz en DATA_DICTIONARY).

| Situación | Test sugerido | Tamaño de efecto |
|---|---|---|
| Resultado binario vs. condición continua | Regresión logística (GLM) | odds ratio por unidad física |
| Continuo vs. continuo | Regresión (OLS/robusta), Spearman | pendiente con IC, ρ |
| Dos grupos | Mann-Whitney / Welch t | Cliff's δ / Hedges g |
| > 2 grupos | Kruskal-Wallis + post-hoc Dunn | ε² |
| Relación física conocida (p. ej. ley d²) | Ajuste no lineal | parámetros con IC |

## 3. Reproducibilidad

- Notebooks leen de `data/silver` o `data/gold`; semillas fijas; funciones reutilizables en `src/flamesafe/analysis/`.
- Toda figura del dashboard se genera con una función (no a mano) y guarda su spec en `reports/figures/`.
- "Restart & Run All" debe pasar antes de abrir el PR.

## 4. Salida: findings
Cada hallazgo usable → `findings/F-XX-<slug>.md` con la [plantilla](findings/_TEMPLATE.md). Solo findings aprobados por PHY
llegan al dashboard.
