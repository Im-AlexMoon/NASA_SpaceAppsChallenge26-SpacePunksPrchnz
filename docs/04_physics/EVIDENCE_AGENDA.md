# Agenda reproducible de evidencia y uso

## Prevención y materiales

Usar la ficha de atmósfera para decidir qué comparación de laboratorio falta. Para calificación, registrar material, geometría, orientación, ventilación, O₂, presión y régimen de gravedad. Revisar aplicabilidad con el equipo de materiales del programa. Un resultado de gas es evidencia sobre las condiciones ensayadas.

Fuentes para mapear cobertura y confirmar el criterio aplicable: [NASA-STD-6001](https://standards.nasa.gov/standard/nasa/nasa-std-6001), [SoFIE](https://science.nasa.gov/biological-physical/investigations/sofie/), [resultados de LUCI](https://ntrs.nasa.gov/citations/20250010653) y [FM²](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/flammability-of-materials-on-the-moon-fm2/).

## Detección

Correr `scripts/research/r07_optical_replay.py <frames> <labels.csv>` con fotogramas por ensayo y una tabla adjudicada con `video_key`, `end_s` y `extinction_mode`. La duración y el tipo de término intervienen solo en la puntuación. Reservar días y hardware antes de ajustar parámetros. Reportar cobertura de video, antelación y alertas por hora observada en pruebas con corte. Evaluar señales multimodales y falsas alertas fuera de este archivo antes de hablar de un detector operativo.

## Supresión

Correr `scripts/research/r06_droplet_coverage.py` sobre Gold. Comparar diluyentes dentro de campaña y evaluar solapamiento de presión y diámetro inicial antes de combinar resultados. Distinguir extinción caliente, extinción fría y disrupción. Los puntos digitizados se contabilizan por rol; los ceros inferidos se separan. No usar la fila PSI-39 1274A para calcular umbrales a partir de diámetro hasta adjudicar la anomalía.

## Ficha de procedencia de un evento

Registrar accession PSI, campaña, identificador de ensayo, geometría, combustible, instrumento y calibración, columna y unidad, archivo y fila de origen, hash de entrada, tiempo en segundos sobre el reloj indicado, evento, razón del término y certeza. En CFI-G, mantener la etiqueta de tabla y EventData como dos observaciones cuando difieran. En Flame Design, marcar el origen de la etiqueta derivada y de la duración reconstruida. Aplicar los términos de cada fuente antes de redistribuir archivos o miniaturas.

## Evaluación de utilidad

Pedir a una persona por función que explique qué evidencia admite el preset lunar, encuentre en PSI una prueba comparable y exporte el fundamento de su próximo ensayo. Registrar tiempo hasta la fuente, acierto al distinguir medición y modelo, y claridad de la acción. Repetir tras resolver los fallos observados. Estado: protocolo pendiente de evaluación con usuarios.
