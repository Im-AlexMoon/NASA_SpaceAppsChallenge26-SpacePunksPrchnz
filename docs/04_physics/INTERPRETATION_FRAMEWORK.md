# Marco de interpretación física

> Tarea PHY-08 · **Revisado PHY: Alexander Moon, 2026-11-15.** Checklist que PHY aplica a **cada** figura, finding y model card
> antes de que llegue al dashboard (PHY-03/04). §Aplicación registra cómo se aplicó al contenido publicado el 2026-11-15.

## Checklist (copiar en el PR o en el finding)

- [ ] **Variables:** ¿unidades correctas y explícitas? ¿Medida, calculada (Tad) o log de prueba?
- [ ] **Comparabilidad:** ¿las variables en un mismo eje son físicamente equivalentes? (ver matriz en DATA_DICTIONARY)
- [ ] **Régimen:** ¿µg, 1 g o tierra? ¿Se mezclan regímenes? ¿Está etiquetado?
- [ ] **Diseño experimental:** ¿qué se varió y qué se mantuvo fijo? ¿Hay confusión (p. ej. O₂ y presión variaron juntos)?
- [ ] **Mecanismo:** ¿qué proceso físico/químico explica la tendencia? (difusión, Da, pérdidas radiativas, dilución, química de baja T)
- [ ] **Signo y magnitud:** ¿la dirección del efecto es la esperada? Si sorprende, ¿hay explicación o es un artefacto?
- [ ] **Literatura:** ¿consistente con publicaciones del propio experimento (DOI)? Citar.
- [ ] **Rango de validez:** ¿en qué condiciones aplica? ¿Se está extrapolando a atmósferas de hábitat o a gravedad parcial?
- [ ] **Implicación de seguridad:** ¿qué significa para prevención / detección / supresión? ¿Con qué confianza?
- [ ] **Lenguaje:** ¿un estudiante de licenciatura lo entiende y a un investigador le parece preciso?

## Niveles de confianza (para findings y recomendaciones)

| Nivel | Criterio |
|---|---|
| **Alta** | Efecto estadísticamente robusto + mecanismo claro + consistente con literatura + dentro del rango de datos |
| **Media** | Dos de los tres primeros criterios, o efecto robusto con extrapolación moderada |
| **Baja** | Tendencia sugerente, n pequeño o extrapolación fuerte → se presenta como hipótesis / brecha |

## Aplicación (2026-11-15)

### Checklist aplicado a los hallazgos publicados
| Criterio | F-01 | F-02 | F-03 | F-04 | F-05 |
|---|---|---|---|---|---|
| Variables y unidades explícitas; Tad/Zst marcadas como calculadas | ✔ | ✔ | ✔ | ✔ | ✔ (radio en px; escala aproximada) |
| Comparabilidad (no se mezclan medidas con calculadas en un eje) | ✔ | ✔ | ✔ | ✔ | ✔ |
| Régimen etiquetado (µg) | ✔ | ✔ | ✔ | ✔ (sin gravedad parcial) | ✔ |
| Diseño: qué varió y confusores | ✔ grupos de O₂ | ✔ combustible ≈ campaña | ✔ 3 días | ✔ | ✔ retrospectivo |
| Mecanismo físico | extinción radiativa | extinción radiativa (4 signos) | inertes + presión | flotabilidad | debilitamiento/oscilación |
| Signo y magnitud esperados | ✔ | ✔ | ✔ | — | ✔ (hollín: negativo) |
| Literatura del registro PSI | L1, L2 | L2, L4, L7 | L17 | L13, L16 | L10 |
| Rango de validez declarado | ✔ | ✔ dominio M-01 | ✔ | ✔ | ✔ |
| Confianza | alta | media | media | alta | media |

### PHY-04 · Validación física de las variables y signos de M-01 v2
| Variable | Unidad | Sentido físico | Signo esperado sobre la duración | Signo estimado (IC 95 %) | Monotonía |
|---|---|---|---|---|---|
| 1000/Tad | 1000/K | temperatura adiabática del estequiométrico (calculada) | negativo: más caliente, dura más | −13.4 (−17.4 a −10.4) ✔ | verificada en test (`test_physical_signs_phy04`) |
| ln p | ln kPa | presión total | negativo: más hollín y radiación | −0.41 (−0.84 a −0.12) ✔ | verificada en test |
| ln ṁ | ln mg/s | caudal total del quemador | negativo: llama más grande, más radiación | −1.20 (−1.54 a −0.82) ✔ | verificada en test |
| ln L | — | posición de la llama respecto al quemador, L = −ln(1−Zst) | positivo: más cerca del quemador, pierde menos | +2.12 (+1.66 a +2.50) ✔ | — |
| Flame Design | 0/1 | campaña (etileno, otro montaje) | sin expectativa | +0.56 (+0.25 a +0.90) | término de ajuste; las lecturas usan CFI-G |

Las monotonías no se imponen en el ajuste: se estiman libremente y se comprueba que el signo coincide con la física; un test unitario
falla si una reestimación invierte un signo.

