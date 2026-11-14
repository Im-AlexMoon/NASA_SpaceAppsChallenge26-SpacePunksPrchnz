# Marco de interpretación física

> Tarea PHY-08. Checklist que PHY aplica a **cada** figura, finding y model card antes de que llegue al dashboard (PHY-03/04).

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
