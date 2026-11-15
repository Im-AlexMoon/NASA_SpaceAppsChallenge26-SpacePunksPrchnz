# Study summary — Resumen del estudio FlameSafe

> Documento bilingüe para el corpus del chat (ADR-0012): responde preguntas generales sobre el estudio ("¿cuáles son los hallazgos
> más relevantes?"). Solo repite números de los hallazgos firmados F-01..F-05 (findings/index.yaml). El orden de relevancia es una
> decisión editorial del equipo. **Revisado y aprobado por PHY: Alexander Moon, 2026-11-15** (contenido y orden de relevancia).

## Key findings of the study, ranked by relevance
The three most relevant findings (main discoveries, key results) of the FlameSafe study of NASA PSI combustion data, ranked by
their impact on fire safety for crewed exploration habitats. All come from flames tested in microgravity on the ISS.

1. **Exploration air keeps a flame alive much longer (F-03).** Near the exploration atmosphere (34 % O2, 56.5 kPa) real spherical
   gas flames burned a median 62.5 s before self-extinguishing, versus 9 s near the ISS cabin (21 % O2, 101 kPa): about 7-10 times
   longer. It matters because habitats planned for the Moon and Mars use this kind of oxygen-enriched, low-pressure air, and
   lowering the pressure does not compensate raising the oxygen.
2. **NASA has no flame data where a lunar base would operate (F-04).** There are zero normal-flame tests within ±0.05 O2 and ±25 %
   pressure of the lunar-base atmosphere (30 % O2, 70 kPa), no CFI-G normal-flame tests between 24 % and 33 % O2, and no combustion
   data at lunar or Martian gravity. The model reading there (59.6 s, 90 % interval 48.2-72.3 s) is an interpolation, not a
   measurement. It matters because it names the experiment that is missing.
3. **A four-term physical law predicts how long a flame lasts (F-02).** ln t = 15.8 - 13.4 (1000/Tad) - 0.41 ln p - 1.20 ln m +
   2.12 ln L. It ranks burn times out of sample with a C-index of 0.89 (255 flames, 24 days) and transfers to Flame Design ethylene
   flames it never saw with a C-index of 0.93. It matters because it turns the data into readings for any atmosphere inside the
   tested range.

The other two findings: oxygen is the dominant control of burn duration, each +0.05 of oxygen mole fraction multiplies the typical
burn duration by about 2.3 (F-01); and flames shrink before they go out on their own, an optical early warning with AUC 0.76,
while the fading of the yellow soot glow is not a warning (AUC 0.45, a negative result) (F-05).

## Hallazgos clave del estudio, ordenados por relevancia
Los tres hallazgos más relevantes (descubrimientos principales, resultados clave) del estudio FlameSafe sobre los datos de
combustión de NASA PSI, ordenados por su impacto en la seguridad contra incendios de hábitats de exploración tripulada. Todos
provienen de llamas probadas en microgravedad en la ISS.

1. **El aire de exploración mantiene viva una llama mucho más tiempo (F-03).** Cerca de la atmósfera de exploración (34 % O2,
   56.5 kPa) las llamas esféricas de gas reales ardieron una mediana de 62.5 s antes de autoextinguirse, frente a 9 s cerca de la
   cabina de la ISS (21 % O2, 101 kPa): unas 7-10 veces más. Importa porque los hábitats planeados para la Luna y Marte usan este
   tipo de aire enriquecido en oxígeno y a baja presión, y bajar la presión no compensa subir el oxígeno.
2. **NASA no tiene datos de llamas donde operaría una base lunar (F-04).** No hay ninguna prueba de llama normal a ±0.05 de O2 y
   ±25 % de presión de la atmósfera de base lunar (30 % O2, 70 kPa), ninguna de CFI-G entre 24 % y 33 % de O2, y ningún dato de
   combustión en gravedad lunar o marciana. La lectura del modelo ahí (59.6 s, intervalo de 90 % 48.2-72.3 s) es una
   interpolación, no una medición. Importa porque señala el experimento que falta.
3. **Una ley física de cuatro términos predice cuánto dura una llama (F-02).** ln t = 15.8 - 13.4 (1000/Tad) - 0.41 ln p - 1.20 ln m
   + 2.12 ln L. Ordena las duraciones fuera de muestra con un índice C de 0.89 (255 llamas, 24 días) y se transfiere a llamas de
   etileno de Flame Design que nunca vio con un índice C de 0.93. Importa porque convierte los datos en lecturas para cualquier
   atmósfera dentro del rango probado.

Los otros dos hallazgos: el oxígeno es el control dominante de la duración, cada +0.05 de fracción molar de oxígeno multiplica la
duración típica por cerca de 2.3 (F-01); y las llamas se encogen antes de apagarse solas, una alerta óptica temprana con AUC 0.76,
mientras que el apagado del brillo amarillo del hollín no es una alerta (AUC 0.45, un resultado negativo) (F-05).

## What the study did — Qué hizo el estudio
FlameSafe ranked the 24 NASA PSI combustion investigations for five user profiles, harmonized 660 gas flame tests from ACME CFI-G
(PSI-159) and ACME Flame Design (PSI-10), re-derived each flame's end from 3,325 sensor time-series files and from all 335 CFI-G ISS
videos, fitted the burn-time model M-01 v2, and graded every reading with an evidence level: A measured nearby, B model
interpolation, C no evidence. FlameSafe clasificó las 24 investigaciones de combustión de NASA PSI, armonizó 660 pruebas de llamas
de gas, validó el final de cada llama con series de tiempo y videos de la ISS, ajustó el modelo M-01 v2 y calificó cada lectura con
un nivel de evidencia. Limits: microgravity only, laboratory gas flames; no partial-gravity data exist.
