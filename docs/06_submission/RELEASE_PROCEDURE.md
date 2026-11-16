# Procedimiento de release de FlameSafe

La versión pública combina Next.js con JSON estáticos y una API opcional de evidencia. ADR-0007 gobierna los niveles, ADR-0011 describe la web y ADR-0010 describe la API. El chat organiza pasajes verificables y preserva sus poblaciones de origen.

## Demostración

Ejecutar `npm --prefix web ci` y `npm --prefix web run dev`. Methods identifica el snapshot. Abrir ISS, exploración y la referencia lunar. Si se usa el chat, configurar los tokens y el backend según deploy/VERCEL.md.

## Reconstrucción

1. Instalar con `uv sync --locked --extra pipeline --extra analysis --extra api --extra dev`. Añadir el extra del proveedor si se usa generación.
2. Para reconstruir tablas, usar los locks documentados y los comandos `catalog`, `bronze`, `silver`, `gold` y `validate`. Consultar PIPELINE_MEDALLION. Las series de ACME se materializan con `timeseries` y `ts-features`.
3. Usar `m1-train` al revisar un artefacto nuevo. El resultado se guarda en artifacts/models y la versión publicada se protege de reemplazos accidentales. Registrar hash de entradas, población y resultados. Mantener el artefacto aprobado para la demo.
4. Ejecutar `uv run --no-sync flamesafe rag-index --source-mode full --retrieval-mode lexical`, `rag-validate` y `web-content`. Versionar juntos los JSON de la web y conservar el bundle anterior.
5. Verificar lint y tipos web, los tres presets y las pruebas Python de lecturas y chat. Si cambian los esquemas de API, regenerar OpenAPI y los tipos del frontend.

## Evidencia de aceptación

DE verifica el snapshot, las excepciones y los hashes. DS reproduce los recuentos y la censura contra el EDA RQ1 y la sección 3 del notebook M1. PHY revisa el texto y los límites. APP verifica la web y su versión. La persona responsable de la entrega registra el resultado antes de promover.

Para revertir, seleccionar el bundle anterior y la revisión de API que lo usa, junto a un build web con el mismo identificador. Verificar ambos estados antes de reactivar el chat.

Para reconciliar los valores de referencia, ejecutar `uv run --no-sync python scripts/research/reconcile_reference_readings.py`. Para el benchmark bilingüe, ejecutar `uv run --no-sync python scripts/research/evaluate_release_chat.py`. Las llamadas al proveedor requieren la opción explícita `--generate` y cuota configurada. Los análisis de gotas, el protocolo de video y la evaluación de utilidad se describen en [la agenda de evidencia](../04_physics/EVIDENCE_AGENDA.md).
