# Evaluación RAG del piloto

`rag_eval.jsonl` contiene 60 preguntas, organizadas en 30 pares español/inglés.
Es una **base de definiciones** con identificadores de variables explícitos, no un
benchmark general de preguntas científicas. Las consultas esperadas son fijas y no
evalúan selección de herramientas por un proveedor.

Ejecutar `uv run --no-sync flamesafe rag-eval --offline`. El informe reproducible
se escribe en `artifacts/rag_eval/report.json`, con build, modo, resultados por caso
y latencia. `definition_success` comprueba que la herramienta encuentra la definición;
`hit_at_8` comprueba que al menos una fuente de esa definición aparece entre los ocho
fragmentos recuperados. Esto no es recall de todas las fuentes relevantes ni entailment.

En la ejecución local de esta entrega, modo **full/hybrid**, ambas métricas fueron
60/60. No hubo llamadas Gemini/OpenAI. No extrapolar estos resultados a consultas sin
identificador, documentos todavía no curados ni razonamiento científico.

`tests/test_rag.py` comprueba por separado consultas parametrizadas, filtros no aplicables,
faltantes, flash, integridad, citas inventadas, cuotas concurrentes, autenticación y límite
de llamadas. Las pruebas de navegador usan respuestas controladas y no gastan API.

Gates pendientes: corpus documental aprobado; preguntas naturales independientes que
cubran campañas, unidades ambiguas, cohortes, filtros, denegación e inyección; comparación
live de los proveedores con presupuesto explícito; revisión humana de respaldo semántico;
latencia y coste en el host de destino. No marcar esos gates como aprobados por el 60/60.
