# ADR-0004 — RAG bilingüe y dashboard Node.js con backend Python

- **Estado:** Aceptado para planificación por instrucción del responsable del proyecto; implementación pendiente.
- **Fecha:** 2026-11-15.
- **Decisor:** Responsable del proyecto, mediante decisiones explícitas en la conversación de planificación.
- **Tareas relacionadas:** RAG-01 a RAG-05 y APP-01 a APP-08.
- **Plan vigente:** [RAG_IMPLEMENTATION_PLAN.md](../../03_data_science/RAG_IMPLEMENTATION_PLAN.md).
- **Sustituye parcialmente:** [ADR-0001](ADR-0001-tech-stack.md), solo respecto a UI, despliegue, proveedor LLM y embeddings del nuevo RAG. Las decisiones de datos y calidad no afectadas siguen aplicando.

## Contexto

El diseño anterior proponía Streamlit, Anthropic y embeddings en inglés. El responsable confirmó consultas documentales y exactas sobre gold, español/inglés, embeddings locales multilingües, migración completa a Node.js y GoDaddy para la aplicación/dominio con hosting Python separado. Pidió mantener OpenAI y Gemini como opciones y posponer predicciones.

## Decisión

Seguir el plan enlazado: dashboard Next.js/TypeScript en `web/`, gateway Node.js y backend FastAPI/Python separado. Python conserva reglas científicas, unidades, auditoría y consultas DuckDB parametrizadas. Recuperación híbrida BM25/densa con embeddings compactos multilingües; candidato inicial `intfloat/multilingual-e5-small`, sujeto a evaluación y revisión fijada.

Implementar adaptadores delgados para OpenAI y Gemini, con selección explícita de un proveedor/modelo por despliegue y sin failover automático. La primera versión publica documentos y resúmenes exactos de datos; las predicciones y resultados científicos sin aprobación permanecen inhabilitados. Migrar todas las páginas no elimina esa restricción.

El plan nuevo prevalece sobre instrucciones incompatibles de `RAG_DESIGN.md`, `DASHBOARD_SPEC.md` y las partes sustituidas de ADR-0001. Los cambios posteriores de alcance/arquitectura deberán documentarse y actualizar el plan. Esta decisión no certifica funcionalidades implementadas ni aprueba gasto, publicación o resultados científicos.

## Alternativas consideradas

| Opción | Ventajas | Motivo para no adoptarla como objetivo actual |
|---|---|---|
| Mantener Streamlit como UI principal | Menos trabajo inicial | El responsable eligió migración completa a Node.js |
| Reescribir ciencia y datos en JavaScript | Un solo runtime web | Duplica reglas científicas y aumenta riesgo de divergencia |
| Elegir definitivamente OpenAI o Gemini ahora | Menos adaptadores | El responsable pidió mantener ambas opciones |
| Ejecutar todo dentro de hosting Node.js gestionado | Un despliegue | No se ha verificado soporte para Python y embeddings; se permite host separado |

## Consecuencias

- Dos runtimes, contratos OpenAPI/TypeScript y CI para Python y Node.js.
- Reutilización de medallion, DuckDB, conversiones y auditoría existentes.
- Artefactos RAG versionados, fuentes elegibles, herramientas permitidas y validación de citas/números.
- Streamlit se conserva durante la transición y se depreca tras aceptación del reemplazo.
- Host Python, modelo/proveedor activo, recursos y presupuesto siguen pendientes para despliegue.
- Configuración, dependencias y comandos actuales se actualizarán durante implementación; este ADR no los modifica.
- Revisión PHY y autorización de acciones externas siguen siendo requisitos independientes.
