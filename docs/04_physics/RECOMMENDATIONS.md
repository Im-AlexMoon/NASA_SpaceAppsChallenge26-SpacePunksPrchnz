# Recomendaciones accionables y agenda de investigación

> Tarea PHY-09 · **Revisado PHY: Alexander Moon, 2026-11-15.** Convierte los hallazgos (F-01..F-05) y el modelo M-01 v2 en acciones
> para la seguridad contra incendios en la exploración tripulada. **Regla:** cada recomendación cita su evidencia y declara su
> confianza ([INTERPRETATION_FRAMEWORK.md](INTERPRETATION_FRAMEWORK.md)). Todo proviene de microgravedad salvo que se diga lo contrario.

### REC-01 — Tratar la atmósfera de exploración como un régimen de llamas más persistentes
- **Pilar:** prevención · **Entorno:** base lunar, rover presurizado, Marte · **Audiencia:** ingenieros de hábitat, agencias
- **Evidencia:** F-01, F-03, M-01 v2; [PSI-159], [PSI-10]; HABITAT_ATMOSPHERES [S3]
- **Confianza:** media
- **Acción propuesta:** al elegir 34 % O₂ / 56.5 kPa, asumir que una llama de gas encendida dura ~7–10 veces más que en una cabina
  tipo ISS (mediana observada 62.5 s frente a 9 s; modelo 95 s, IC 90 % 75–120). Calificar materiales y dimensionar la respuesta con
  la **fracción de O₂ del hábitat**, no con la del aire, y no tomar la pO₂ normóxica como indicador de riesgo de incendio.
- **Siguiente experimento:** materiales sólidos de cabina en la atmósfera de exploración con flujo controlado.

### REC-02 — Medir lo que falta: llamas a 30 % O₂ / 70 kPa y en todo el rango 24–33 % O₂
- **Pilar:** prevención · **Entorno:** base lunar · **Audiencia:** investigadores, planificadores de experimentos en la ISS
- **Evidencia:** F-04; lectura M-01 v2 de nivel B (60 s, IC 90 % 48–72, distancia a los datos 2.15 veces la típica)
- **Confianza:** alta (la brecha es un hecho de cobertura)
- **Acción propuesta:** programar una campaña de llamas esféricas normales en esas condiciones con el hardware ACME. Es la prueba que
  más reduciría la incertidumbre del modelo para la cota de base lunar del reto, y convertiría esa lectura de nivel B en nivel A.
- **Siguiente experimento:** el mismo conjunto en gravedad parcial (REC-05).

### REC-03 — No contar con la autoextinción al reducir la presión de cabina
- **Pilar:** prevención / supresión · **Entorno:** rover, base lunar, Marte · **Audiencia:** diseñadores de supresión
- **Evidencia:** F-01, F-02 (duplicar la presión multiplica por 2.2 el riesgo de autoextinción, IC 1.5–3.3; término ln p −0.41)
- **Confianza:** media
- **Acción propuesta:** a menor presión total las llamas de estos experimentos duran más. Los procedimientos de supresión para
  hábitats a baja presión deben suponer llamas más persistentes que a 1 atm, aunque la pO₂ sea la misma.
- **Siguiente experimento:** barrido de presión a fracción de O₂ fija en la región 50–75 kPa.

### REC-04 — Vigilar el tamaño relativo de la llama como alerta temprana, y no confiar en que deje de verse amarilla
- **Pilar:** detección · **Entorno:** todos · **Audiencia:** diseñadores de detectores
- **Evidencia:** F-05 (71 % de las llamas que se autoextinguen ya están por debajo del 80 % de su radio 5–10 s antes; AUC 0.76;
  el apagado del hollín no anticipa nada, AUC 0.45); R6 (transiciones a llama fría)
- **Confianza:** media
- **Acción propuesta:** en detección óptica, seguir el tamaño de la llama respecto a su propio máximo distingue una llama que muere de
  una que persiste. Una llama que pierde su brillo amarillo **no** debe considerarse apagada: puede seguir viva en azul o pasar a llama fría.
- **Siguiente experimento:** evaluar la alarma en tiempo real (falsas alarmas en toda la vida de la llama) sobre los videos de PSI-159
  y PSI-10, ya procesables con el Cloud Run Job del proyecto.

### REC-05 — No extrapolar a la Luna o Marte la autoextinción observada en microgravedad
- **Pilar:** prevención · **Entorno:** base lunar, Marte · **Audiencia:** agencias, ingenieros de hábitat
- **Evidencia:** F-04; PARTIAL_GRAVITY_BOUNDING.md (flotabilidad renueva el gas en ~0.1 s a 0.165 g frente a 5–300 s de vida en µg)
- **Confianza:** media-baja (argumento de escala, sin mediciones en gravedad parcial)
- **Acción propuesta:** tratar la duración en µg como **cota inferior** de la persistencia de una llama en gravedad parcial. Priorizar
  experimentos de combustión en gravedad lunar y marciana (vuelos parabólicos, centrífuga en la ISS).
- **Siguiente experimento:** llamas esféricas y sólidos en gravedad parcial con la atmósfera de exploración.

### REC-06 — Registrar la causa de cada corte de flujo y conservar el video en los experimentos de combustión
- **Pilar:** todos (calidad de la evidencia) · **Audiencia:** equipos de experimentos de NASA, curadores de PSI
- **Evidencia:** R5, R10 (22 de 30 cortes en llamas normales de CFI-G fueron por límite térmico del quemador, no por temporizador);
  R7, F-02 (21112A6 figura con 259 s en la tabla; series y video dan ~146 s); ADR-0005 y ADR-0009
- **Confianza:** alta
- **Acción propuesta:** publicar en la tabla experimental la causa del final de cada prueba (autoextinción, temporizador, límite térmico,
  decisión del operador). Sin ella, las llamas más intensas quedan como censuras "aleatorias" y sesgan cualquier modelo. Mantener los
  videos y las series por prueba: permitieron validar y corregir la tabla.
- **Siguiente experimento:** ninguno; es una mejora de protocolo y de curaduría.

### REC-07 — Usar la ley de duración M-01 v2 solo dentro de su dominio y con su nivel de evidencia
- **Pilar:** prevención · **Audiencia:** usuarios del dashboard, analistas
- **Evidencia:** F-02; ADR-0007; model card M-01
- **Confianza:** alta (es una regla de uso)
- **Acción propuesta:** la lectura del modelo solo es válida para llamas esféricas de gas (etano, propano, butano) en microgravedad,
  dentro del rango de Tad, presión, caudal y L ensayado. Fuera de ese dominio el dashboard no muestra número (nivel C).

## Aplicaciones en Tierra (add-on)
- La relación entre fracción de inertes y persistencia de la llama (F-01, F-03) es la misma que gobierna los riesgos en ambientes
  enriquecidos en O₂ en Tierra (hospitales, cámaras hiperbáricas, soldadura). ⚠️ Extrapolación cualitativa; no evaluada con datos.
