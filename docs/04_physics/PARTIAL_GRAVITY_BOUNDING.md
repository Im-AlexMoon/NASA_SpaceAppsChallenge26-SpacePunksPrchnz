# Acotamiento de gravedad parcial (PHY-05)

> **Revisado PHY: Alexander Moon, 2026-11-15.** Regla del proyecto: PSI no tiene datos de combustión en gravedad parcial; todo
> resultado lunar o marciano es acotamiento o extrapolación y debe decirlo. Este documento fija *cómo* se acota y qué se muestra.
> Las estimaciones de orden de magnitud de §2 son cálculos de escala propios, no mediciones.

## 1. Qué tenemos y qué no
- **Tenemos:** llamas esféricas de gas en **microgravedad** (ISS: CFI-G, Flame Design), con ignición, duración, modo de extinción,
  radio en video y series ópticas por prueba; y la ley de duración M-01 v2 (F-02).
- **No tenemos:** ninguna prueba a 0.165 g (Luna) ni a 0.38 g (Marte). E-FIELD Flames (PSI-22) imitó un efecto tipo flotabilidad con
  campos eléctricos, pero sin resultado tabulado (tier 3).

## 2. Por qué la microgravedad no es un caso "seguro" para la Luna o Marte
El mecanismo que apaga nuestras llamas es la **extinción radiativa**: sin flotabilidad, la llama crece rodeada de sus propios
productos, acumula hollín y gases calientes que radian, y se enfría hasta un umbral crítico (F-01, F-02, F-05). Ese mecanismo
necesita tiempos de residencia largos.

Escala de velocidades y tiempos (llama de radio r ≈ 17 mm medido en video; gas caliente a ~2,000 K, Δρ/ρ ≈ 0.85):

| Entorno | g (m/s²) | Velocidad de flotabilidad u ≈ √(g·r·Δρ/ρ) | Tiempo de residencia r/u |
|---|---|---|---|
| Tierra | 9.81 | ~0.37 m/s | ~0.05 s |
| Marte | 3.73 | ~0.23 m/s | ~0.07 s |
| Luna | 1.62 | ~0.15 m/s | ~0.11 s |
| ISS (µg) | ~0 | solo difusión y ventilación | segundos a decenas de segundos (r²/D) |

Incluso a 0.165 g la flotabilidad renueva el gas alrededor de la llama en ~0.1 s, órdenes de magnitud más rápido que el tiempo
en que una llama esférica en µg se apaga por radiación (5–300 s en los datos). Consecuencias:

1. **Hipótesis:** la flotabilidad podría cambiar la autoextinción radiativa. La dirección y magnitud dependen de geometría, ventilación y mecanismos de pérdida. El argumento de escala no establece una cota para la persistencia.
2. **La velocidad inducida en gravedad parcial (~0.15–0.23 m/s) cae en el rango de las velocidades de ventilación de cabina**
   (⚠️ valores típicos de ventilación por verificar en NASA-STD-3001). Las investigaciones de sólidos (BASS, BASS-II; ver *Microgravity
   flammability boundary for PMMA rods in axial stagnation flow*, doi:10.1016/j.combustflame.2017.03.001) muestran que la
   inflamabilidad depende del flujo, con una frontera en O₂–velocidad. Hipótesis H4: la gravedad parcial podría caer cerca del
   flujo de máxima inflamabilidad, no en una zona intermedia segura.
3. **La ignición podría ser más fácil o más difícil**, según el modo: un estudio numérico 3D de ignición de un sólido por una
   fuente radiante localizada (Liao & T'ien, *A numerical simulation of transient ignition and ignition limit of a composite solid by
   a localised radiant source*, *Combustion Theory and Modelling*, 2013, doi:10.1080/13647830.2013.831486; artículo aportado por el
   equipo y leído completo) encuentra que en gravedad lunar (0.16 g) la energía mínima de ignición en fase gas es menor que en
   1 g a tasas de calentamiento altas y mayor a tasas bajas (las curvas se cruzan cerca de 3.4 W), y que la tasa crítica de
   calentamiento baja ligeramente (0.742 W frente a 0.814 W). No hay base para interpolar linealmente en g.

## 3. Cómo se muestra en el dashboard
- La lectura para la Luna o Marte se calcula con la atmósfera del hábitat **en microgravedad** y se etiqueta así.
- El **efecto de la gravedad** se indica como no estimable con los datos analizados. El texto identifica el régimen de microgravedad de la estimación.
- Nunca se muestra una curva que interpole entre µg y 1 g.

## 4. Experimentos que cerrarían la brecha
1. Llamas esféricas normales a 30 % O₂ / 70 kPa y en 24–33 % O₂ en la ISS (cierra la brecha de atmósfera, F-04).
2. El mismo conjunto en gravedad parcial: vuelos parabólicos con perfil lunar/marciano o una centrífuga a bordo de la ISS.
3. Materiales sólidos de cabina en la atmósfera de exploración con flujo controlado en el rango 0.05–0.25 m/s.

## 5. Confianza
La estimación de escala formula una hipótesis. La auditoría de F-04 verifica la cobertura de la instantánea y no establece el efecto en gravedad parcial.
