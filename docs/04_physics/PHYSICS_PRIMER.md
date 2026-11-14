# Primer de física — combustión en microgravedad para seguridad contra incendios

> Tarea PHY-01. Lectura de 30 min para **todo** el equipo antes de G0. Cada afirmación marcada ⚠️ debe confirmarse con una
> fuente en [LITERATURE_REVIEW.md](LITERATURE_REVIEW.md) antes de usarse en el dashboard.

## 1. Por qué una llama es distinta en microgravedad

En la Tierra, el gas caliente de la llama es menos denso y **sube** (flotabilidad): eso arrastra aire fresco hacia la base de la
llama, se lleva los productos y da la forma de lágrima. En microgravedad la flotabilidad casi desaparece:

- El transporte de O₂ hacia la llama y de productos hacia afuera ocurre solo por **difusión** y por **flujo forzado**
  (ventiladores, ventilación de cabina).
- La llama de una vela se vuelve **esférica**, más tenue y azulada; la combustión es más lenta.
- Los productos de combustión se acumulan alrededor de la llama → puede "ahogarse" sola si no hay flujo.
- Las **pérdidas por radiación** pesan mucho más, porque los tiempos de residencia son largos.
- Matiz: en llamas de chorro de gas, los tiempos de residencia largos pueden *aumentar* el hollín (tema de SPICE). ⚠️

**Número adimensional clave:** el número de Grashof (flotabilidad / viscosidad) ∝ g → 0 en microgravedad.

## 2. Ignición, sostenimiento y extinción

- **Número de Damköhler** Da = tiempo de flujo / tiempo químico. Da bajo → la química no alcanza → extinción.
- Dos límites de extinción: (1) por **estiramiento/soplado** (flujo demasiado rápido, Da bajo) y (2) **radiativo** (llama grande y
  lenta que pierde más calor por radiación del que genera). El límite radiativo es casi exclusivo de microgravedad, y ACME
  Flame Design lo estudió en llamas esféricas. ⚠️
- **Llamas frías (cool flames):** combustión a baja temperatura (~500–800 K) por química de baja temperatura. Durante FLEX se
  observaron gotas de heptano que siguieron "quemando" tras apagarse la llama visible. ⚠️ **Por qué importa:** una llama casi
  invisible y difícil de detectar puede persistir y reencender la combustión. CFI y CFI-G las estudian.

## 3. Oxígeno: fracción molar vs. presión parcial

- **Fracción molar** XO₂ (o % en volumen): proporción de moléculas de O₂ en la mezcla.
- **Presión parcial** pO₂ = XO₂ · P_total: lo que "ve" la química y la fisiología.
- Ejemplo: 34% O₂ a 8.2 psi da pO₂ ≈ 19.2 kPa, similar al nivel del mar (≈ 21.2 kPa). Para los pulmones es casi lo mismo. Para
  el fuego no lo es: hay **mucho menos N₂ inerte** que absorba calor, así que la llama queda más caliente y los materiales son
  más inflamables. ⚠️ Por eso el reto subraya que ≥ 30% O₂ hace a los materiales "mucho más inflamables".
- Consecuencia para el análisis: **siempre** modelar con ambas variables y dejar que los datos digan cuál explica mejor (H1).

## 4. Flujo de aire: el factor que la Tierra esconde

- En 1 g siempre hay un flujo inducido por flotabilidad (~decenas de cm/s). En µg el flujo lo pone la ventilación (~cm/s).
- **Propagación de llama en flujo opuesto** (la llama avanza contra el flujo) es el modo típico en naves.
- Con flujo muy bajo la llama se ahoga (falta O₂); con flujo intermedio se ve la **máxima inflamabilidad**; con flujo alto, soplado.
- Implicación ⚠️: en µg, a flujos bajos de ventilación, algunos materiales pueden arder con **menos O₂** que el límite medido en
  las pruebas normalizadas en 1 g. Los ensayos en Tierra pueden no ser conservadores. Temas de BASS, BASS-II y SAFFIRE.

## 5. Supresión

- **Dilución** de la atmósfera con inertes (CO₂, He, N₂): bajar XO₂ y añadir capacidad calorífica. FLEX probó CO₂ y He.
- CO₂ tiene alta capacidad calorífica molar y participa en la radiación; el He tiene alta difusividad térmica. Su eficacia
  relativa depende del régimen. ⚠️
- En µg los agentes no se dispersan "hacia arriba"; importa cómo se distribuye el agente. La **niebla fina de agua** desarrollada
  para la ISS tiene aplicaciones en Tierra (tema del add-on).

## 6. Detección

- Sin flotabilidad, el humo no sube hacia el techo: los detectores deben ubicarse según el flujo de ventilación.
- SAME y SAME-R midieron humo de materiales típicos de naves. Reportaron diferencias de tamaño de partícula frente a 1 g que
  afectan la sensibilidad de los detectores. ⚠️
- DAFT usó uno de los mismos instrumentos para polvo, que es relevante para el polvo lunar.

## 7. Gravedad parcial (Luna 0.165 g, Marte 0.38 g)

- La flotabilidad escala con g. Un flujo inducido de pocos cm/s puede caer justo en el rango de **máxima inflamabilidad**. ⚠️
  La hipótesis es que la gravedad parcial podría ser el peor caso, no un punto intermedio "seguro".
- PSI **no** tiene datos de gravedad parcial. E-FIELD Flames imitó un efecto tipo flotabilidad con campos eléctricos.
- Estrategia del proyecto: tratar µg y 1 g como **cotas**, mostrarlo explícitamente y proponer LUCI y FM2 como siguientes pasos.

## 8. Glosario rápido

| Término | Significado |
|---|---|
| XO₂ | fracción molar de oxígeno (0–1) |
| pO₂ | presión parcial de oxígeno |
| Tad | temperatura adiabática de llama (**calculada**, no medida) |
| Zst | fracción de mezcla estequiométrica (estructura de llamas de difusión) |
| Llama inversa | el oxidante sale del quemador hacia un ambiente con combustible (CFI-G, Flame Design) |
| LOC / MOC | concentración límite / mínima de oxígeno para sostener la combustión |
| CIR / MDCA / MSG | hardware de la ISS: Combustion Integrated Rack / Multi-user Droplet Combustion Apparatus / Microgravity Science Glovebox |
