# Atmósferas de hábitat de referencia

> Tarea PHY-07 · **Revisado PHY: Alexander Moon, 2026-11-15.** Fuente única de los valores usados en
> `src/flamesafe/physics/atmospheres.py`, en las lecturas de M-01 v2 (`/v1/readings/atmospheres`) y en el *Atmosphere Explorer*.
> pO₂ = XO₂ · P (1 psi = 6.894757 kPa). Tad y Zst: calculadas con `physics/thermochem.py` (equilibrio químico, validado contra
> 587 pruebas de PSI) para una fuente de propano al 30 % en N₂. Son cantidades **calculadas**, no medidas.

| Entorno | P total (psi / kPa) | XO₂ | pO₂ (kPa) | Gravedad (g) | Tad calc. (K) | Evidencia M-01 v2 | Fuente | Verificado |
|---|---|---|---|---|---|---|---|---|
| Tierra, nivel del mar | 14.7 / 101.3 | 0.209 | 21.2 | 1 | ~2,170 | A en µg; efecto de la gravedad: C | estándar | ✔ |
| Cabina ISS | 14.7 / 101.3 | ~0.21 | ~21.3 | ~0 (µg) | 2,171 | **A** (35 pruebas, 6 días) | [S1] rango de presión; [S2] valor histórico de 14.7 psia | ✔ (valor nominal; ver nota) |
| Traje espacial (clase EMU) | 4.3 / 29.6 | 1.00 | 29.6 | 0 / 0.165 | — | **C** (fuera del rango ensayado) | enunciado del reto | ✔ (reto) |
| **Base lunar / rover (cota del reto)** | ≤ 10.2 / ≤ 70.3 | ≥ 0.30 | ~21.1 | 0.165 | 2,446 | **B** (0 pruebas cercanas; interpolación) | enunciado del reto | ✔ (reto) |
| Atmósfera de exploración 8.2 psi / 34 % | 8.2 / 56.5 | 0.34 | 19.2 | 0.165 (Luna) / 0.38 (Marte) | 2,512 | **A** en el borde (19 pruebas, 3 días) | [S3], [S4] | ✔ |
| Hábitat en Marte (supuesto = exploración) | 8.2 / 56.5 | 0.34 | 19.2 | 0.38 | 2,512 | A en µg; efecto de la gravedad: C | supuesto del proyecto | supuesto |

**Fuentes (verificadas el 2026-11-15 en NTRS y sitios de NASA):**
- **[S1]** NASA OCHMO, *Technical Brief: Environmental Control and Life Support Systems* (derivado de NASA-STD-3001): presión
  tolerable para exposición indefinida 26.2–103 kPa (3.8–14.9 psia), pO₂ normóxica inspirada objetivo 145–155 mmHg y al menos
  30 % de gas diluyente en cabina. https://www.nasa.gov/wp-content/uploads/2023/07/eclss-technical-brief-ochmo.pdf
- **[S2]** NASA, *Space Shuttle News Reference — Environmental Control and Life Support System*: cabina a 14.7 ± 0.2 psia con
  ~80 % N₂ / 20 % O₂ (referencia histórica del valor de 14.7 psia; la ISS opera a presión atmosférica nominal).
  https://webarchive.library.unt.edu/eot2008/20090119101725/http://science.ksc.nasa.gov/shuttle/technology/sts-newsref/sts_eclss.html
- **[S3]** Norcross, J. R. et al. (2015), *Evidence Report: Risk of Hypobaric Hypoxia from the Exploration Atmosphere*, NASA
  JSC-CN-34806, NTRS 20150021491: el Exploration Atmospheres Working Group (EAWG) recomendó 8.0 psia / 32 % O₂ y en 2012 se
  cambió a **8.2 psia / 34 % O₂** para reducir el estrés hipóxico. https://ntrs.nasa.gov/citations/20150021491
- **[S4]** NASA/TP-2010-216134, *Recommendations for Exploration Spacecraft Internal Atmospheres: The Final Report of the NASA
  Exploration Atmospheres Working Group* (listado como referencia en NTRS 20220005716). El documento primario no se consultó
  directamente. https://ntrs.nasa.gov/api/citations/20220005716/downloads/AsMA%202022%20-%20Garbino%20-%20Exploration%20Atmospheres%20v2.pdf

**Notas:**
- No se encontró un documento de la ISS con su punto de ajuste exacto de O₂. Se usa el nominal ~21 % a 101.3 kPa, dentro de [S1].
- ⚠️ Una búsqueda indica que un artículo de *Aerospace Medicine and Human Performance* (2018, vol. 89, p. 792) estima 31.4 % como el
  O₂ máximo a 8.2 psia que no aumentaría la velocidad de combustión, por debajo del 34 % adoptado. El servidor rechazó la descarga
  (403): **por verificar** antes de citarlo en el dashboard. Es coherente con F-03.
- La fila "Shuttle EVA prep 10.2 psi / ~26.5 %" de versiones anteriores se retiró por no tener fuente verificada.

## Lectura física (para la narrativa)
- La pO₂ de las atmósferas de exploración es **casi normóxica** (19–21 kPa): por eso son aceptables para la tripulación.
- Para la llama cuenta además la fracción de **inertes**: la razón N₂/O₂ cae de 3.8 (aire) a 1.9 (34 % O₂). La llama nace ~340 K más
  caliente (Tad calculada) y, en microgravedad, dura ~7–10 veces más que cerca de la cabina ISS (F-03). Bajar la presión no lo
  compensa: en los datos, menos presión también alarga la llama (F-01, F-02).
- Ninguna combinación de "Luna/Marte + atmósfera enriquecida" tiene datos de combustión medidos en PSI. Todo lo que el dashboard
  muestre ahí es interpolación en µg o acotamiento, y debe decirlo (F-04, PARTIAL_GRAVITY_BOUNDING.md).

## Gravedad parcial: política de acotamiento (PHY-05)
Ver [PARTIAL_GRAVITY_BOUNDING.md](PARTIAL_GRAVITY_BOUNDING.md). Resumen: el efecto de la gravedad es siempre nivel C; la duración
en µg es probablemente una **cota inferior** de la persistencia de la llama en la Luna o Marte, porque la flotabilidad debilita
la autoextinción radiativa. No se interpola linealmente en g.
