# Atmósferas de hábitat de referencia

> Tarea PHY-07. **Fuente única** de los valores usados en `src/flamesafe/physics/atmospheres.py`, en los modelos (DS-13) y en
> el Habitat Risk Explorer. Cada fila necesita una cita verificada antes de G7. pO₂ = XO₂ × P (1 psi = 6.894757 kPa).

| Entorno | P total (psi / kPa) | XO₂ | pO₂ (kPa) | Gravedad (g) | Fuente | Verificado |
|---|---|---|---|---|---|---|
| Tierra, nivel del mar | 14.7 / 101.3 | 0.209 | 21.2 | 1 | estándar | ✔ |
| Cabina ISS | 14.7 / 101.3 | ~0.21 | ~21.3 | ~0 (µg) | NASA ISS ECLSS | ☐ |
| Traje espacial (EMU) | 4.3 / 29.6 | 1.00 | 29.6 | 0 / 0.165 | enunciado del reto | ✔ (reto) |
| Preparación EVA del Shuttle (histórico) | 10.2 / 70.3 | ~0.265 | ~18.6 | ~0 | ⚠️ por verificar | ☐ |
| **Base lunar / rover (cota del reto)** | ≤ 10.2 / ≤ 70.3 | ≥ 0.30 | ~21.1 | 0.165 | enunciado del reto | ✔ (reto) |
| Atmósfera de exploración 8.2 psi / 34% | 8.2 / 56.5 | 0.34 | 19.2 | 0.165 (Luna) / 0.38 (Marte) | ⚠️ NASA Exploration Atmospheres Working Group, por verificar | ☐ |

## Lectura física (para la narrativa)
- La pO₂ de las atmósferas de exploración es **casi normóxica** (19–21 kPa): por eso son aceptables para la tripulación.
- Pero la fracción de **inertes** baja de ~79% a ~66–70%, así que hay menos N₂ para absorber calor. Eso aumenta la temperatura de llama
  y la inflamabilidad de los materiales (H1 se prueba con datos).
- Ninguna combinación de "Luna/Marte + atmósfera enriquecida" tiene datos de combustión medidos en PSI. Todo lo que el dashboard
  muestre ahí es **extrapolación o acotamiento** y debe decirlo.

## Gravedad parcial: política de acotamiento (PHY-05)
- Cota inferior de flotabilidad = datos µg (PSI). Cota superior = datos/ensayos en 1 g (literatura, NASA-STD-6001 ⚠️).
- No se interpola linealmente en g como si fuera dato. Se muestra la banda con la nota "comportamiento no monotónico posible
  (ver PHYSICS_PRIMER §7)".
