# Primer de física — combustión en microgravedad para seguridad contra incendios

> Tarea PHY-01 · **Revisado PHY: Alexander Moon, 2026-11-15.** Lectura de 30 min para todo el equipo. Lo marcado ✔ quedó
> confirmado con datos del proyecto o con publicaciones del registro PSI ([LITERATURE_REVIEW.md](LITERATURE_REVIEW.md)); lo que
> sigue con ⚠️ no se ha verificado y no debe usarse en el dashboard sin fuente. La §9 resume lo que aprendimos de los datos.

## 1. Por qué una llama es distinta en microgravedad

En la Tierra, el gas caliente de la llama es menos denso y **sube** (flotabilidad): eso arrastra aire fresco hacia la base de la
llama, se lleva los productos y da la forma de lágrima. En microgravedad la flotabilidad casi desaparece:

- El transporte de O₂ hacia la llama y de productos hacia afuera ocurre solo por **difusión** y por **flujo forzado**
  (ventiladores, ventilación de cabina).
- La llama de una vela se vuelve **esférica**, más tenue y azulada; la combustión es más lenta.
- Los productos de combustión se acumulan alrededor de la llama → puede "ahogarse" sola si no hay flujo.
- Las **pérdidas por radiación** pesan mucho más, porque los tiempos de residencia son largos.
- Matiz: en llamas de chorro de gas, los tiempos de residencia largos pueden *aumentar* el hollín (tema de SPICE). ⚠️
- ✔ Las llamas de CFI-G y Flame Design **no** son de chorro: son llamas de difusión esféricas sobre un quemador poroso. En el
  video de la ISS se ven como una esfera con núcleo amarillo (hollín) y capa azul (R16, R17).

**Número adimensional clave:** el número de Grashof (flotabilidad / viscosidad) ∝ g → 0 en microgravedad.

## 2. Ignición, sostenimiento y extinción

- **Número de Damköhler** Da = tiempo de flujo / tiempo químico. Da bajo → la química no alcanza → extinción.
- Dos límites de extinción: (1) por **estiramiento/soplado** (flujo demasiado rápido, Da bajo) y (2) **radiativo** (llama grande y
  lenta que pierde más calor por radiación del que genera). El límite radiativo es casi exclusivo de microgravedad, y ACME
  Flame Design lo estudió en llamas esféricas. ✔ (publicaciones del registro PSI-10, p. ej. doi:10.1016/j.proci.2022.07.043;
  y nuestros datos: la duración sigue los signos de la extinción radiativa, F-02)
- **Llamas frías (cool flames):** combustión a baja temperatura (~500–800 K) por química de baja temperatura. Durante FLEX se
  observaron gotas de heptano que siguieron "quemando" tras apagarse la llama visible. ✔ (registro PSI-68/69: *Isolated n-heptane droplet combustion in microgravity: "Cool Flames" – Two-stage combustion*,
  doi:10.1016/j.combustflame.2013.09.011). ✔ En CFI-G los comentarios del operador registran transiciones de llama caliente a llama fría ("5 transitions
  from hot to cool", R6), y el registro PSI-159 incluye *Spherical gas-fueled cool diffusion flames* (doi:10.1016/j.proci.2022.07.015). **Por qué importa:** una llama casi
  invisible y difícil de detectar puede persistir y reencender la combustión. CFI y CFI-G las estudian.

## 3. Oxígeno: fracción molar vs. presión parcial

- **Fracción molar** XO₂ (o % en volumen): proporción de moléculas de O₂ en la mezcla.
- **Presión parcial** pO₂ = XO₂ · P_total: lo que "ve" la química y la fisiología.
- Ejemplo: 34% O₂ a 8.2 psi da pO₂ ≈ 19.2 kPa, similar al nivel del mar (≈ 21.2 kPa). Para los pulmones es casi lo mismo. Para
  el fuego no lo es: hay **mucho menos N₂ inerte** que absorba calor, así que la llama queda más caliente y los materiales son
  más inflamables en algunos ensayos. Para la fuente de referencia, el modelo calcula una temperatura adiabática mayor. En F-03 se comparan cohortes con distintas mezclas de combustible. La transferencia a materiales sólidos requiere ensayos representativos.
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
- Estrategia del proyecto: mostrar la estimación de microgravedad y el efecto de gravedad como no estimable con la instantánea. El argumento de escala se documenta en [PARTIAL_GRAVITY_BOUNDING.md](PARTIAL_GRAVITY_BOUNDING.md).

## 8. Glosario rápido

| Término | Significado |
|---|---|
| XO₂ | fracción molar de oxígeno (0–1) |
| pO₂ | presión parcial de oxígeno |
| Tad | temperatura adiabática de llama (**calculada**, no medida) |
| Zst | fracción de mezcla estequiométrica (estructura de llamas de difusión) |
| Llama normal | el combustible sale del quemador esférico hacia la atmósfera de la cámara; es la geometría que se proyecta a un hábitat |
| Llama inversa | el oxidante sale del quemador hacia un ambiente con combustible (CFI-G, Flame Design) |
| L | término logarítmico de la fracción de mezcla, L = −ln(1 − Zst) en llama normal; ubica la llama respecto al quemador |
| Censura | la prueba terminó antes que la llama (corte de flujo): sabemos que duró *al menos* ese tiempo |
| LOC / MOC | concentración límite / mínima de oxígeno para sostener la combustión |
| CIR / MDCA / MSG | hardware de la ISS: Combustion Integrated Rack / Multi-user Droplet Combustion Apparatus / Microgravity Science Glovebox |

## 9. Lo que aprendimos de los datos (2026-11-15)

Resumen físico de las cinco iteraciones de investigación ([RESEARCH_LOG.md](../03_data_science/RESEARCH_LOG.md)) y de los hallazgos
F-01..F-05 ([findings](../03_data_science/findings/)):

1. **Extinción radiativa.** Una llama esférica en µg crece, acumula hollín y gases calientes, radia y se apaga al enfriarse. Su
   duración sigue `ln t = 15.8 − 13.4·(1000/Tad) − 0.41·ln p − 1.20·ln ṁ + 2.12·ln L`: más caliente dura más; más presión y más
   caudal, menos; más cerca del quemador, más (F-02). La ley se transfiere de CFI-G a Flame Design sin reajuste.
2. **El oxígeno manda.** +0.05 de O₂ ≈ ×2.3 de duración (F-01).
3. **La presión parcial no basta.** A pO₂ casi igual, la atmósfera de exploración da llamas mucho más persistentes que la cabina
   ISS, porque hay la mitad de inertes por molécula de O₂ (F-03).
4. **No son llamas estacionarias.** El radio medido en video crece como (ṁ/L)^0.5 y no depende de la presión; la teoría
   estacionaria predice ṁ/L (R18).
5. **Señales antes de la extinción.** La llama se encoge y oscila antes de apagarse sola (F-05). El hollín se apaga con el tiempo en
   casi todas las llamas y no anticipa nada (R19).
6. **"Apagada" no siempre es apagada.** Hay transiciones a llama fría (R6), casi invisible: relevante para detección.
7. **El final de una prueba no siempre es físico.** Muchos cortes de flujo ocurren por el límite térmico del quemador (~728 K), no
   por temporizador: es censura informativa que hay que modelar aparte (R10).
8. **Lo que no sabemos.** No hay pruebas de CFI-G entre 24 % y 33 % de O₂ en llama normal (Flame Design: 6 de etileno a 1 atm, sin duración), ni cerca de la base lunar, ni en gravedad parcial (F-04).

