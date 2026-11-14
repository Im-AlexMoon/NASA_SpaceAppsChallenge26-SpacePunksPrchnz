# Registro de riesgos

| # | Riesgo | Prob. | Impacto | Mitigación | Dueño | Estado |
|---|---|---|---|---|---|---|
| R1 | Pocas filas por dataset (decenas–cientos) → modelos sobreajustados | Alta | Alto | Modelos interpretables primero, CV agrupada, intervalos conformales, features físicas, reportar incertidumbre | DS | Abierto |
| R2 | Formatos/unidades heterogéneos (XO₂ vs %vol, atm vs bar vs psi, tokens `#DIV/0!`, `RAMP`) | Alta | Medio | Parsers por familia, tokens → NULL + flag, `physics/units.py` testeado | DE | Abierto |
| R3 | API PSI lenta, 404 o archivos listados que no existen | Media | Alto | Reintentos + caché en bronze; 404 registrado; empezar descargas temprano | DE | Abierto |
| R4 | El tamaño del archivo (~13 TB) tienta a descargar de más | Media | Alto | Presupuesto en `configs/sources.yaml` (≤ 500 MB, sin video/zip salvo ADR) | DE | Abierto |
| R5 | El RAG alucina números o citas | Media | Alto | Números solo vía herramientas SQL; citas obligatorias; set de evaluación | RAG | Abierto |
| R6 | Sin datos de gravedad parcial en PSI | Cierta | Medio | Bounding µg/1g explícito; etiquetar como extrapolación; proponer LUCI/FM2 | PHY | Abierto |
| R7 | Comparar variables no equivalentes (Tad calculada vs T medida) | Media | Alto | Matriz de comparabilidad en DATA_DICTIONARY; revisión PHY | DE/PHY | Abierto |
| R8 | Integración tardía del dashboard | Media | Alto | Vertical slice a H+10; scope freeze H+12 | APP | Abierto |
| R9 | Clave de API / costos del LLM | Baja | Medio | Modelo configurable por `.env`; caché de respuestas para la demo | RAG | Abierto |
| R10 | Uso indebido de código de terceros (repo de referencia sin licencia) | Baja | Alto | ADR-0003: solo como referencia, citar, re-verificar | Todos | Abierto |
| R11 | Fatiga del equipo | Alta | Medio | Turnos de sueño, scope freeze, recortes predefinidos | PM | Abierto |
