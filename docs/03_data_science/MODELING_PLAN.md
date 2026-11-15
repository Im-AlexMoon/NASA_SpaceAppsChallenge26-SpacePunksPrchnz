# Plan de modelado predictivo

> Tareas DS-08 → DS-13, PHY-04/05. Cierra en **G4** · **G4 cerrado el 2026-11-15:** M-01 v2 (duración con niveles de evidencia),
> model card [M-01](model_cards/M-01.md) firmada por PHY. M2 (gotas) y M4 quedan como extensiones. Esta es la "parte dorada": modelos que un ingeniero de misión pueda usar
> para fijar **umbrales de peligrosidad** dadas las condiciones de un hábitat o vehículo — con su incertidumbre y sus límites.

## 1. Realidad de los datos (y cómo la respetamos)

Los datasets tabulares de PSI tienen **decenas a cientos de filas**. Eso define la estrategia:

- Modelos **interpretables primero** (GLM logístico, GAM, ajustes físicos) → boosting solo si mejora en CV y con
  **restricciones monótonas** acordadas con PHY (p. ej. más O₂ no puede reducir la probabilidad de llama sostenida).
- **Features físicas** antes que features "ciegas": presión parcial de O₂, fracción molar, mezcla estequiométrica (Zst),
  temperatura adiabática (Tad, marcada como calculada), caudal/velocidad, tipo y fracción de diluyente.
- **Validación agrupada** (GroupKFold por campaña / día de prueba / combustible) para evitar fuga entre pruebas casi idénticas.
- **Incertidumbre obligatoria**: intervalos conformales (MAPIE) o bootstrap; probabilidades calibradas.
- **Dominio de aplicabilidad**: cada predicción reporta si las condiciones están dentro del casco de datos de entrenamiento
  (distancia de Mahalanobis / kNN). Fuera → advertencia de **extrapolación** visible en el dashboard.

## 2. Modelos candidatos (se confirman tras G1/G3)

| ID | Pregunta operativa | Target | Datos | Tipo | Prioridad |
|---|---|---|---|---|---|
| **M1** | ¿Con qué probabilidad se sostiene / se extingue una llama dadas O₂, presión y flujo? | binario o multiclase (modo de extinción, ignición, llama fría) | `gas_flame_tests` | clasificación calibrada | **MVP** |
| **M2** | ¿Cuánto diluyente (CO₂/He) y a qué presión se extingue una llama de gota? ¿Cómo cambia la tasa de quemado? | diámetro de extinción, tasa de quemado K | `droplet_tests` | regresión + ajuste físico (ley d²) | Stretch 1 |
| **M3** | Frontera de inflamabilidad O₂–presión con banda de incertidumbre | P(llama sostenida) = 0.5 / 0.05 | M1 (+ datos sólidos si alcanza) | derivado de M1 | **MVP** (salida de M1) |
| **M4** | Alerta temprana de detección de humo | respuesta del detector vs. tiempo/material | `smoke_detection`, `fire_telemetry` | series de tiempo | Stretch 2 |

### Datos disponibles tras DE-08 (2026-11-14)
- **M1:** `gas_flame_tests`. **CFI-G** tiene 333 pruebas; 263 sí / 62 no en `ignited`, 8 `flash` y XO₂ de 0.12 a 0.85.
  Es la base del clasificador. **Flame Design** tiene 325 pruebas con `ignited` casi constante (323 sí / 2 no) y procedente de una
  decisión operativa (R-DE-08a). Sirve para describir el espacio de condiciones y como validación débil, **no** para entrenar sin cuidado.
- **M2:** `droplet_tests`. CFI tiene `k_hot_mm2_s` en 148 pruebas (con He y 0.5–5 atm). FLEX y CFI tienen `d_ext_hot_mm` en 341.
  FLEX tiene `test_end` en 274 (186 extinciones; CO₂ en 123 pruebas y He en 50). PSI-117 aporta 69 puntos experimentales y 4,237 de modelo.

## 3. Protocolo (por modelo)

1. **Target y unidad de análisis** definidos con PHY; documentar clases y desbalance.
2. **Baselines:** (a) trivial (clase mayoritaria / media), (b) físico (regla o correlación de literatura).
3. **Modelo interpretable** → **modelo flexible** (si aplica). Hiperparámetros con CV anidada pequeña.
4. **Métricas:** clasificación → ROC-AUC, PR-AUC, Brier score, curva de calibración; regresión → MAE, RMSE, R², cobertura del intervalo.
5. **Explicabilidad:** coeficientes / curvas parciales / SHAP; PHY verifica que los signos tengan sentido físico.
6. **Incertidumbre + dominio de aplicabilidad.**
7. **Umbrales de riesgo (DS-13):** para cada atmósfera de referencia (`physics/atmospheres.py`) reportar probabilidad e IC,
   y la condición límite (p. ej. XO₂ máxima a presión dada para P(llama) < 5%). Si la atmósfera cae fuera del dominio → "sin evidencia".
8. **Model card** en `model_cards/M-XX.md` ([plantilla](model_cards/_TEMPLATE.md)).

## 4. Gravedad parcial (PHY-05)

PSI no contiene datos en gravedad parcial. **Política:** los modelos se entrenan con datos de µg; los resultados en 1 g de
literatura o de pruebas normalizadas sirven como segunda cota. El dashboard muestra la Luna/Marte como una **banda acotada**
entre ambos regímenes con texto explícito "acotamiento, no medición", y propone los experimentos que cerrarían la brecha (LUCI, FM2).

## 5. Criterios de aceptación (G4)
- Supera ambos baselines en CV agrupada con IC que no se traslapan con el baseline trivial.
- Calibración aceptable (Brier y curva). Cobertura empírica del intervalo ≈ nominal.
- Signos/monotonías físicamente coherentes (firma PHY).
- Model card completa, incluyendo **usos no previstos** (p. ej. "no es un estándar de certificación de materiales").
