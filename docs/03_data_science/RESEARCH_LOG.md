# Bitácora de investigación — exprimir la información disponible

> Objetivo (definido el 2026-11-15): generar conocimiento que aporte a NASA antes que entregables. Agotar la información que ya
> tenemos con modelos físicos y rigor estadístico, decir con claridad qué demuestran los datos y qué no, y proponer los
> experimentos que faltan. Cada iteración registra hipótesis, método, resultado (incluidos los negativos) y siguiente paso.
> Todo es **candidato** hasta la revisión PHY. PSI es microgravedad: nada aquí es evidencia de gravedad parcial.

## Corrección de base: qué son físicamente estos experimentos

CFI-G (PSI-159) y Flame Design (PSI-10) **no son llamas de chorro**: son **llamas de difusión esféricas** sobre un quemador
poroso esférico en microgravedad (texto de hipótesis de PSI: *"cool diffusion flames on spherical porous burners"*). La
literatura asociada en nuestra tabla `publications` describe el mecanismo que gobierna su duración:

- Extinción radiativa de llamas esféricas en microgravedad — doi:10.1016/j.combustflame.2007.08.009
- Temperatura crítica y flujo másico crítico para la extinción radiativa (etileno, 1 bar) — doi:10.1016/j.proci.2022.07.043
- Existencia de llamas esféricas estacionarias con pérdida radiativa — doi:10.1016/j.proci.2022.07.049
- Efecto de la presión en la cinética y extinción de llamas calientes, tibias y frías — doi:10.1016/j.proci.2024.105400
- Llamas de difusión frías esféricas con gas (CFI-G) — doi:10.1016/j.proci.2022.07.015

Lectura física (⚠️ a confirmar por PHY contra esos artículos): la llama crece con el tiempo; al crecer pierde más calor por
radiación, su temperatura baja y se extingue al llegar a una temperatura crítica. Una llama más grande o más fría de origen
vive menos. Esto reemplaza la descripción "llamas de chorro" usada hasta M1 v1.

## Inventario: información que tenemos y no estamos usando

| Fuente | Dónde está | Qué contiene | Estado |
|---|---|---|---|
| **Series temporales por prueba** (`*_data.csv`) | PSI; solo 2 muestras en bronze | ~125 Hz, ~80 s por prueba: 3–5 radiómetros, 3 PMT, termopar del quemador, presiones, caudales, corriente iónica. 339 archivos en PSI-159 (1.47 GB) y 317 en PSI-10 (1.25 GB) | **No ingerido** (excede `download_budget`: 500 MB / 150 archivos) |
| Comentarios por prueba (`*_Comments.txt`, `*_TP.txt`, "as run") | PSI, ~1 KB cada uno (~2,000 archivos, ~2 MB) | notas del operador y parámetros del punto de prueba | No ingerido |
| `comments` y `color` de CFI-G | silver | "hit burner T limit", "Flow timed out", "Irregular Oscillation", "5 transitions from hot to cool", color de la llama | En silver, **no llega a gold** |
| EventData | silver | potencia y tiempo del ignitor, `burn_fraction`, presión inicial/final, composición final del gas | Solo se usa `ignite` y las fechas |
| Duración de Flame Design | derivable de EventData / series | 327 pruebas de etileno sin `burn_time_s` ni modo de extinción en gold | No derivado |
| Reportes finales y SRD (PDF) | bronze | metodología, límites del hardware, definiciones | No leídos sistemáticamente |
| Tablas de otras investigaciones | silver (`et__*`) | BASS-II (129 pruebas de sólidos con O₂ inicial/final), BASS (122), SPICE (469, con encendido y apagado), Saffire-2 (15, con µg frente a 1 g), CFI gotas con radiometría | Fuera de gold |
| Gotas FLEX + CFI | gold | 501 pruebas, K, diámetro de extinción, diluyentes | Sin EDA ni modelo (RQ2) |

**Lo más valioso sin tocar son las series temporales.** En las dos muestras se ve directamente: el instante exacto de extinción
(la llama de 21256B1 se apaga a los ~13 s aunque el flujo sigue 30 s más), **oscilaciones de la radiación antes de extinguirse**
(posible señal precursora), la historia de calentamiento del quemador y, en Flame Design, si la llama llegó viva al corte.

## Iteración 1 (2026-11-15) — ¿una ecuación física predice la duración de la llama?

**Reproducible:** `python scripts/research/r01_physics_burn_time.py` · código en `src/flamesafe/models/aft.py` y
`src/flamesafe/physics/spherical_flame.py` (con tests).

**Hipótesis.** Si la extinción es radiativa, la duración debe depender de (1) la temperatura adiabática `Tad`, (2) la presión,
(3) el caudal másico total del quemador `ṁ` y (4) el término logarítmico `L` de la teoría de fracción de mezcla
(`L = −ln(1−Zst)` en llama normal, `−ln(Zst)` en inversa; el radio estacionario de la llama es ∝ `ṁ/L`).

**Método.** Regresión de tiempo de falla acelerado con censura por la derecha (corte de flujo), validación dejando fuera un día
completo, comparación por **log-verosimilitud fuera de muestra** (regla de puntuación propia, castiga la sobreconfianza) e
índice C; intervalos por bootstrap de días. Cohorte: la de M1 (132 llamas normales, 130 inversas).

### Resultados

**R1. La familia Weibull de M1 v1 es sobreconfiada.** En llamas normales su log-verosimilitud fuera de muestra (−1.55 por prueba)
es peor que la de un modelo con solo O₂ (−1.36), aunque ordena bien (C = 0.81). Con error log-logístico el mismo modelo pasa a
−1.34 y C = 0.83. En inversas el Weibull es peor que no usar covariables (−2.59 frente a −1.64). **M1 v2 debe usar log-logística
o lognormal.** El ranking de M1 v1 sigue siendo válido; sus probabilidades e intervalos, no.

**R2. Ecuación física candidata (llamas normales, log-logística):**

    ln t = 16.6 − 19.5·(1000/Tad) − 0.49·ln p − 0.57·ln ṁ + 1.30·ln L      (t en s, Tad en K, p en kPa, ṁ en mg/s)

| Término | Coeficiente | IC 95 % (bootstrap de días) | Lectura |
|---|---|---|---|
| 1000/Tad | −19.5 | −21.6 a −13.3 | llama más caliente de origen → vive más |
| ln p | −0.49 | −0.82 a −0.15 | más presión → vive menos (t ∝ p^−0.5) |
| ln ṁ | −0.57 | −1.52 a −0.10 | más caudal (llama más grande) → vive menos |
| ln L | +1.30 | +0.87 a +2.31 | llama más cerca del quemador → vive más |

- Cuatro grupos físicos y **sin saber qué combustible es**: AIC 271.6 frente a 278.4 del modelo empírico de M1 (6 pendientes).
  Fuera de muestra: −1.20 frente a −1.34 por prueba (diferencia +0.14, IC −0.09 a +0.41) y C = 0.82 frente a 0.83.
  **Lectura honesta: iguala al modelo empírico con menos parámetros; la mejora no es estadísticamente distinguible.**
- Añadir el combustible mejora algo más (−1.11; C = 0.86), tampoco de forma concluyente.
- Los signos son los que predice la extinción radiativa. ⚠️ Los exponentes deben contrastarse con la teoría y con los artículos citados.

**R3. La dependencia con Tad coincide entre geometrías.** Controlando el combustible, el coeficiente de 1000/Tad es −18.7
(IC −21.4 a −13.9) en llamas normales y −17.8 (IC −28.3 a −8.8) en inversas: dos conjuntos de pruebas de días y geometrías
distintas. El exponente de presión también (−0.41 y −0.52). Es una regularidad no trivial. ⚠️ Una "temperatura de activación
efectiva" de ~19,000 K equivale a ~155 kJ/mol; PHY debe decir si es comparable con la cinética global de hidrocarburos o si es
una coincidencia de la forma funcional (la forma ln(Tad − 1130) ajusta igual: AIC 270.3).

**R4 (negativo). La temperatura crítica de extinción no se puede identificar desde la tabla resumen.** El perfil de
verosimilitud sobre `Tc` en `ln(Tad − Tc)` es plano (cambia < 1 unidad entre 700 y 1,500 K). Para medirla hace falta la
historia temporal de la radiación: otra razón para ingerir las series.

**R5. La censura es informativa en parte.** Los comentarios de silver registran cortes por "burner temperature limit" además de
"flow timed out"; en inversas `color = limit` aparece en 29 pruebas. Una llama cortada por calentar demasiado el quemador **no**
es una censura aleatoria: son justamente las llamas más intensas. El modelo de duración debe separar corte por temporizador
(censura administrativa) de corte por límite térmico (riesgo competitivo).

**R6. "Autoextinguida" no siempre significa apagada.** Hay comentarios de transiciones de llama caliente a **llama fría**
("5 transitions from hot to cool"). Una llama fría es casi invisible y sigue consumiendo combustible. Solo 8 pruebas tienen
la bandera `cool_flame`. Para seguridad importa: una llama que "se apagó" puede seguir reaccionando y reencender.

### Qué demuestra y qué no esta iteración

- ✔ Demuestra: la duración de estas llamas sigue una ley con grupos físicos interpretables, con signos coherentes con extinción
  radiativa y estable entre geometrías. La forma Weibull era inadecuada.
- ✘ No demuestra: que la ecuación física sea mejor que la empírica (IC cruza cero); el valor de la temperatura crítica; nada sobre
  sólidos, gravedad parcial o incendios reales.

## Iteración 2 (2026-11-15) — qué añaden las series temporales por prueba

**Reproducible:** `flamesafe timeseries` (ADR-0005; 3,325 archivos, 2,716.5 MB, 0 diferencias de tamaño) → `flamesafe ts-features`
→ `python scripts/research/r02_timeseries_transfer.py`. Código en `src/flamesafe/pipeline/timeseries.py` (10 tests).
Tabla silver `acme__timeseries_features`: una fila por prueba (655; 634 de las 660 pruebas de gold tienen serie).

### R7. El detector sobre las series reproduce al investigador
- **CFI-G:** el modo de extinción coincide en el 99.6 % de 238 llamas sostenidas; la duración tiene Spearman 0.995 con la de la
  tabla, diferencia mediana 0.47 s, y el 94 % cae dentro de 2 s.
- **Flame Design:** coincide con el evento "Extinction detected" del script en el 97.5 % de 237 pruebas sin rampa.
- El brillo del ignitor se descuenta: 53 de 58 pruebas "no ignition" dan emisión solo transitoria.
- ⚠️ Dato sospechoso en la tabla: 21112A6 figura con 259 s de quemado, pero el flujo completo de esa prueba dura 157 s.

### R8. Flame Design gana duración y modo de extinción
244 llamas sostenidas sin rampa: 135 normales (54 autoextinguidas) y 109 inversas (31). Antes no tenían ni duración ni modo en gold.
Las 66 pruebas de **rampa de flujo** quedan aparte: son otro protocolo (se baja el caudal hasta extinguir) y miden otra cosa.

### R9. La ecuación física ajustada solo con CFI-G predice Flame Design sin reajuste (llamas normales)
Entrenamiento: 120 llamas de etano, propano y butano (CFI-G, 2021). Prueba: 135 llamas de **etileno** y propano de otra campaña
(Flame Design, 2019–2022). Ningún parámetro se reajusta.

| Métrica | Valor | IC 95 % (bootstrap de días en ambas campañas) |
|---|---|---|
| Índice C | 0.93 | 0.80 a 0.96 |
| Pendiente de calibración (1 = perfecta) | 1.16 | 0.72 a 1.48 |
| Ordenada | −0.03 | — |
| Log-verosimilitud por prueba frente a un modelo sin covariables ajustado en Flame Design | −0.62 frente a −1.03 | ganancia −0.41 a +0.68 |

- **Lectura:** el orden de las duraciones se transfiere muy bien a un combustible y una campaña que el modelo nunca vio, y la
  escala es correcta (pendiente compatible con 1, sin sesgo). La ganancia en verosimilitud no es concluyente (el IC cruza cero).
- El modelo empírico de M1 **ni siquiera se puede aplicar** a Flame Design: usa el combustible como categoría y el etileno no existe en CFI-G.
- Con la misma definición de duración en ambas campañas los coeficientes coinciden: 1000/Tad −13.5 (CFI-G) y −13.2 (Flame Design);
  ln ṁ −0.96 y −1.46; ln L +1.88 y +2.24. La presión no se puede comparar (Flame Design normal casi no la varía: 102–132 kPa).
- ⚠️ El coeficiente de Tad cambió de −19.5 (iteración 1, duración de la tabla) a −13.5 (duración de la serie, solo llamas sostenidas).
  El signo y el orden de magnitud son estables; el valor exacto depende de la cohorte y no debe interpretarse como cinética.

**Llamas inversas: la transferencia falla en escala.** Índice C 0.82 (0.60 a 0.95), pero pendiente 0.62 y predicciones ~2 veces
más cortas que lo observado; no supera al modelo sin covariables. La ecuación ordena bien pero no está calibrada entre campañas.

### R10. Por qué se cortó el flujo: temporizador o límite térmico
El temporizador corta el flujo ~23 s antes de `flowTimeoutSec` (confirmado con los comentarios "timed out").

| Campaña | Llama | Corte por temporizador | Corte antes del temporizador | Pico del quemador (mediana) |
|---|---|---:|---:|---|
| CFI-G | inversa | 42 | 13 | 537 K / **728 K** |
| CFI-G | normal | 8 | 22 | 701 K / **728 K** |
| Flame Design | inversa | 2 | 78 | sin dato en gold |
| Flame Design | normal | 8 | 74 | sin dato en gold |

- En CFI-G los cortes anticipados ocurren con el quemador en ~728 K en ambas geometrías (las autoextinguidas llegan a 400 K): es el
  **límite térmico del quemador**. En llamas normales, 22 de 30 cortes son por ese límite: **censura informativa confirmada**.
- En Flame Design casi ningún corte llega al temporizador y la causa no está identificada (⚠️ por verificar con los PDF de
  "test parameter notes" o el reporte final).

### R11. Las llamas que se apagan solas oscilan antes de apagarse
Proporción de llamas con oscilación ininterrumpida de la señal óptica durante los últimos 5 s o más:

| Campaña | Llama | Autoextinguidas | Cortadas por flujo |
|---|---|---|---|
| CFI-G | normal | 57 % (de 91) | 17 % (de 30) |
| CFI-G | inversa | 16 % (de 63) | 2 % (de 55) |
| Flame Design | normal | 38 % (de 50) | 6 % (de 82) |
| Flame Design | inversa | 90 % (de 29) | 6 % (de 80) |

- Entre las autoextinguidas que oscilan ≥ 2 s, la oscilación empieza **8.9 s antes** en mediana (cuartiles 3.8 y 20.3 s).
- Coherente con la literatura de extinción oscilatoria de llamas esféricas (doi:10.1016/s1540-7489(02)80008-6).
- ⚠️ Preliminar: el índice es RMS relativo > 5 % y puede inflarse cuando la señal cae rápido. Falta validarlo con un criterio
  espectral y revisar casos a mano. Si se confirma, es una **señal precursora** de extinción medible con un sensor óptico simple.

### Qué demuestra y qué no la iteración 2
- ✔ La ley física de duración es transferible entre combustibles y campañas en llamas normales (orden y escala).
- ✔ La censura por límite térmico existe y afecta sobre todo a las llamas normales de CFI-G.
- ✘ No demuestra: transferencia calibrada en inversas; la causa de los cortes en Flame Design; que la oscilación sirva como alarma
  (falta tasa de falsos positivos durante la vida de la llama, no solo al final).

## Iteración 3 (2026-11-15) — M1 v2, primera lectura para la base lunar y pruebas de rampa

**Reproducible:** `python scripts/research/r03_m1v2_lunar_ramps.py` (~4 min; requiere Cantera, extra `analysis`).
Código nuevo: `src/flamesafe/physics/thermochem.py` (3 tests).

### R12. Termoquímica propia validada: ya podemos situar cualquier atmósfera en los ejes físicos
`thermochem.zst` y `thermochem.tad_k` (equilibrio a presión y entalpía constantes) reproducen las columnas de los investigadores en
587 pruebas: Zst con diferencia máxima 0.008; Tad con diferencia mediana +3 K, el 90 % entre −41 y +50 K, correlación 0.998.
Son cantidades **calculadas**, igual que las publicadas.

### R13. M1 v2 (llamas normales, las dos campañas, ecuación física log-logística)
255 llamas sostenidas de 24 días (120 de CFI-G, 135 de Flame Design), con la misma definición de duración.

    ln t = 15.8 − 13.4·(1000/Tad) − 0.41·ln p − 1.20·ln ṁ + 2.12·ln L + 0.56·[Flame Design]

| Término | Coef. | IC 95 % (bootstrap de días) |
|---|---|---|
| 1000/Tad | −13.4 | −17.4 a −10.4 |
| ln p | −0.41 | −0.84 a −0.12 |
| ln ṁ | −1.20 | −1.54 a −0.82 |
| ln L | +2.12 | +1.66 a +2.50 |
| Flame Design (frente a CFI-G) | +0.56 | +0.25 a +0.90 |

- **Validación dejando fuera un día:** log-verosimilitud −0.72 por prueba e índice C 0.89, frente a −0.82 y 0.83 de O₂ + presión
  y −1.30 sin covariables.
- **Calibración fuera de muestra** de P(sigue ardiendo a 60 s) por terciles: predicho 0.03 / 0.38 / 0.84, observado 0.03 / 0.26 / 0.81.
  A 30 s: 0.27 / 0.90 / 0.99 frente a 0.20 / 0.91 / 1.00.
- **Sensibilidad a la censura por límite térmico** (21 cortes en CFI-G): los coeficientes cambian menos del 12 % entre
  (A) tratarlos como censura, (B) excluirlos y (C) suponer que habrían llegado al temporizador. La conclusión no depende de ese supuesto.
- ⚠️ Las llamas de Flame Design duran ~1.75 veces más que las de CFI-G a igualdad de grupos físicos (término +0.56). Puede ser el
  combustible (etileno, hollín) o el montaje; con un solo combustible por campaña no se pueden separar.
- En Flame Design 73 de 81 cortes ocurren antes del temporizador y su causa sigue sin identificar.

### R14. Primera lectura para la base lunar (30 % O₂, 70 kPa) — nivel B: interpolación del modelo
Fuente supuesta: corriente con 30 % de combustible en N₂ a 1 mg/s (el caso típico de CFI-G). Microgravedad.

| Atmósfera | Tad calculada | Duración mediana del modelo (IC 90 %) | P(sigue a 60 s) | Observado cerca |
|---|---|---|---|---|
| Cabina ISS (21 %, 101 kPa) | 2,125–2,196 K | 13 s (10–17) | 0.01 | 9 s (21 pruebas, todas autoextinguidas) |
| Exploración (34 %, 56.5 kPa) | 2,467–2,536 K | 91–97 s (73–125) | 0.77–0.80 | 63 s entre las autoextinguidas (15 pruebas, 3 siguieron hasta el corte) |
| **Base lunar (30 %, 70 kPa)** | 2,400–2,470 K | **58–61 s (47–75)** | **0.47–0.51 (0.32–0.66)** | **ninguna prueba** |

- En cada eje físico por separado la base lunar cae **dentro** de lo ensayado (temperatura en el percentil 64, caudal 31–49,
  posición de llama 37–58; la presión en el percentil 7, extremo bajo). Pero **no hay ninguna prueba cercana en la combinación**:
  la distancia a la quinta prueba más próxima es 2.1 veces la típica entre pruebas. Es interpolación del modelo, no medición.
- El resultado es estable entre los tres supuestos de censura (55–65 s).
- Lectura: en la base lunar una llama de este tipo duraría unas **4–5 veces más que en la ISS**, y algo menos que en la
  atmósfera de exploración. ⚠️ No incluye el efecto de la gravedad lunar (nivel C).
- El modelo sobreestima un poco donde hay datos (13 s frente a 9 s; ~95 s frente a 63 s entre autoextinguidas, que excluye las
  que seguían vivas). Debe mostrarse junto a lo observado.

### R15 (exploratorio). Pruebas de rampa: no aparece un único caudal crítico
34 pruebas de Flame Design con extinción registrada y caudales utilizables (calibración de los controladores con 90 pruebas
estacionarias: dispersión 0.1 % en combustible y 0.3 % en N₂).

- **19 con rampa de caudal** (se reduce hasta el 58 % en mediana): caudal total en la extinción 0.32–3.9 mg/s, mediana 0.91.
- **15 con rampa de composición:** Tad en la extinción entre 1,671 y 2,784 K.
- En ambos grupos, las llamas con mayor Tad se apagan con menor caudal (Spearman −0.54 y −0.66): coherente con un caudal crítico
  que baja al subir la temperatura, pero con 15–19 pruebas y condiciones mezcladas **no se puede ajustar una ley**. Sin intervalos.
- Cuatro pruebas se extinguen cerca de 1,700 K, pero no basta para fijar una temperatura crítica.

### Qué demuestra y qué no la iteración 3
- ✔ La ecuación física es estable frente al supuesto de censura y está razonablemente calibrada fuera de muestra.
- ✔ Hay una primera lectura cuantitativa para la base lunar con su nivel de evidencia.
- ✘ No demuestra: el efecto de la gravedad parcial, la validez para otros combustibles o sólidos, ni una ley de caudal crítico.
- **Experimento que más reduciría la incertidumbre:** llamas normales a 30 % O₂ y 70 kPa (hoy 0 pruebas) y, en general, O₂ entre 0.24 y 0.33.

## Iteración 4 (2026-11-15) — ¿el video de la ISS permite medir la llama? (ADR-0009, fase 1)

**Reproducible:** `flamesafe video-samples` (4 archivos, 494 MB, 0 diferencias de tamaño) →
`python scripts/research/r04_video_feasibility.py --burner-px 30`. Requiere `opencv-python-headless`.

### R16. Sí: la llama esférica es medible en el video de operaciones, y el video ve lo que los sensores no
Video: cámara analógica de operaciones grabada en tierra desde el enlace de bajada (CFI-G final report), 640×480 a 29.97 cps.
La cámara científica de alta definición (1024×1024, 30 cps) está en los `.zip`, mucho más pesados.

| Prueba | Llama | Duración: investigador / serie / **video** | Radio estable | Brillo amarillo a la mitad, antes del final |
|---|---|---|---|---|
| 21137A4 | normal, propano, 36 % O₂, 1 atm, autoextinguida | 35 / 35.8 / **36.0 s** | 79 px (~17 mm ⚠️) | 17 s antes |
| 21174F2 | normal, butano, 39 % O₂, 2 atm, cortada por flujo | 24 / 24.4 / **25.1 s** | 83 px (~18 mm ⚠️) | no ocurre (brillante hasta el corte) |
| 21228J1 | inversa, propano, 85 % O₂, 1.1 bar, autoextinguida | 18 / 17.9 / **17.8 s** | 36 px (~8 mm ⚠️) | 14 s antes |

- **La duración medida en el video coincide con las otras dos fuentes** con diferencias de 1 s o menos.
- **El radio se mide con claridad:** esfera casi redonda (redondez 0.85–0.87 en normales) sobre fondo negro. Escala: el
  quemador mide 6.35 mm (reporte final); ~30 px en un cuadro iluminado (⚠️ estimación visual, falta medirlo con precisión).
- **Lo que solo se ve en video:** la llama normal tiene un núcleo amarillo (hollín) dentro de una capa azul. En la llama que se
  autoextingue el amarillo se apaga **unos 17 s antes** de la extinción y al final solo queda la capa azul tenue; antes de
  apagarse el radio oscila y se encoge. En la llama cortada por flujo el núcleo sigue brillante hasta el corte.
  Es coherente con la extinción radiativa (el hollín radia calor y enfría la llama) y con la oscilación previa de R11.
- ⚠️ El brillo no se puede comparar entre pruebas: la ganancia de la cámara se ajustaba a veces para llamas tenues. Sí sirve dentro
  de una misma prueba (forma de la curva). Los puntos brillantes son píxeles calientes del sensor por radiación, no partículas.
- Limitaciones: tres pruebas; resolución modesta; destello del ignitor al inicio; errores de decodificación benignos del flujo `.ts`.

**Decisión:** la fase 1 es positiva. La fase 2 (336 videos de CFI-G en Google Cloud) queda justificada para medir radio y
desaparición del hollín en todas las pruebas y contrastar la ley `r ∝ ṁ/L` y el precursor óptico.

## Iteración 5 (2026-11-15) — el video de todas las pruebas de CFI-G, procesado en Google Cloud (ADR-0009, fase 2)

**Reproducible:** Cloud Run Job `flamesafe-video` (335 tareas, ~11 min; ver `deploy/VIDEO_JOB.md`) →
`flamesafe video-collect --source gs://flamesafe-psi-video/cfig-v2` → `python scripts/research/r05_video_all_cfig.py`.
Dos fallas encontradas y corregidas en la prueba de humo: OpenCV en Linux devolvía cuadros negros (se decodifica con
FFmpeg de `imageio-ffmpeg`) y el quemador incandescente tras la extinción se contaba como llama (regla de persistencia).

### R17. La duración medida en video concuerda con el investigador en 264 pruebas
334 videos procesados, llama vista en 331; 321 se unen a pruebas de gold. Contra la tabla del investigador: Spearman 0.97,
diferencia mediana 0.0 s, 70 % dentro de 2 s y 83 % dentro de 5 s. Contra el detector de las series: Spearman 0.975.
- Las discrepancias grandes son llamas **muy largas** (160–300 s) en las que el video pierde la llama antes: probablemente se
  vuelve demasiado tenue para la cámara (⚠️ posible llama tibia o fría; por verificar).
- **21112A6:** el video da 146 s, igual que las series (147 s); la tabla dice 259 s. Confirma el error sospechado en R7.

### R18. El radio de la llama no sigue la ley estacionaria, pero sí es independiente de la presión (llamas normales)
Teoría cuasi-estacionaria: radio ∝ ṁ/L (pendiente 1 en escala log). 83 llamas normales con radio de buena calidad, 11 días:
- **Pendiente 0.50** (IC 95 % 0.30–0.71), R² 0.42, Spearman 0.72. El radio crece con ṁ/L, pero como su raíz, no linealmente.
- Exponente de presión −0.04 (IC −0.25 a 0.17): **sin efecto de la presión**, como predice la teoría (ρD no depende de p).
- Lectura: estas llamas no alcanzan el estado estacionario durante la prueba (o el radio visible no es la hoja de llama).
  La ecuación de duración usa ṁ y L por separado, así que sigue siendo válida; lo que cae es la interpretación "radio estacionario".
- Llamas inversas: casi sin relación (pendiente 0.20, IC −0.13 a 0.52) y fuerte dependencia de la presión (−0.62). Son tenues:
  solo 55 con radio de buena calidad.

### R19 (negativo). El apagado del hollín NO anticipa la autoextinción
En las tres muestras de R16 el núcleo amarillo se apagaba antes de la extinción. Con todas las pruebas no se sostiene:
en llamas normales el brillo cae a la mitad ≥ 5 s antes del final en el 60 % de las autoextinguidas **y** en el 60 % de las
cortadas por flujo (AUC 0.45, IC 0.24–0.63). En inversas va al revés. El brillo decae con el tiempo en casi todas las llamas
(y la ganancia de la cámara variaba): no es un precursor. **La observación de R16 era un artefacto de muestra pequeña.**

### R20. El encogimiento de la llama sí anticipa la autoextinción (llamas normales)
Radio relativo a su mediana de media vida, en ventanas antes del final (67 llamas normales con radio de buena calidad):

| Ventana antes del final | Autoextinguidas (45) | Cortadas por flujo (22) | AUC "se va a apagar sola" (IC 95 %, bootstrap de días) |
|---|---|---|---|
| 15 a 10 s | 0.74 | 1.02 | 0.73 (0.62–0.84) |
| 10 a 5 s | 0.62 | 0.99 | 0.76 (0.67–0.86) |
| 5 a 0 s | 0.50 | 0.92 | — |

- El 71 % de las llamas que se autoextinguen ya mide menos del 80 % de su radio de media vida **5–10 s antes** de apagarse,
  frente al 32 % de las que siguen vivas hasta el corte. Coherente con la extinción radiativa y con la oscilación de R11.
- Es una señal medible con una cámara simple y sin calibración absoluta (radio relativo a sí mismo).
- ⚠️ Retrospectivo: aquí se conoce el final. Para una alarma en tiempo real hay que usar la caída respecto al máximo móvil y
  medir falsas alarmas durante toda la vida de la llama. En inversas no hay suficientes llamas con radio medible.

## Agenda (ordenada por información ganada por esfuerzo)

1. ✔ **Series temporales ingeridas** (ADR-0005) y reducidas a una fila por prueba. Pendiente dentro de este frente:
   **flujo en la extinción de las 66 pruebas de rampa** (mide directamente el caudal crítico), fracción radiativa con la
   historia de los radiómetros, validación espectral de la oscilación y calibración del termopar del quemador.
2. **Llevar `comments`, `color` y EventData a gold** (sin descargar nada): causa del corte, bandera de llama fría, energía del ignitor.
   Con la energía del ignitor se puede modelar la ignición como energía mínima, que es la variable física correcta.
3. **M1 v2**: log-logística, riesgos competitivos (autoextinción / límite térmico / temporizador), ecuación física como modelo
   principal, y **predicción para la base lunar** calculando `Tad` y `Zst` de esa atmósfera (requiere termoquímica: Cantera).
4. **Gotas (RQ2)**: ley d², diámetro de extinción y efecto de CO₂ y He como supresores; es física distinta y datos ya en gold.
5. **Sólidos**: BASS-II y Saffire-2 a gold; Saffire-2 trae µg frente a 1 g en el mismo material (único dato comparativo de gravedad).
6. **Diseño de experimentos**: con la incertidumbre de la ecuación, calcular qué condición nueva reduciría más el error
   (candidata evidente: llama normal a 30 % O₂ y 70 kPa, dentro del hueco 0.24–0.33 de O₂).
7. Solo después: procesamiento de imágenes (radio de llama desde video) para validar `r ∝ ṁ/L`.
