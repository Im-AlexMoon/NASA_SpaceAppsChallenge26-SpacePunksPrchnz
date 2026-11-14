# ADR-0002 — Alcance de datos del MVP

- **Estado:** Propuesto — **se completa y acepta al cerrar G1** (tarea DE-05)
- **Tarea relacionada:** DE-05

## Contexto
PSI expone 24 investigaciones de combustión con ~13 TB registrados, dominados por video, imágenes y ZIP. Las tablas experimentales
curadas son pequeñas y estructuradas. El reto pide resumir, comparar, rankear y modelar.

## Hipótesis inicial (a verificar con la triage — no es una decisión todavía)

Basada en la revisión preliminar del repositorio de referencia (ver ADR-0003), a confirmar contra el API en vivo:

| Tier | Candidatas | Uso previsto |
|---|---|---|
| 1 — Primary | ACME Flame Design (PSI-10), ACME CFI-G (PSI-159), FLEX (PSI-69) | Estadística y modelos: O₂, presión, flujos, extinción, tasa de quemado, diluyentes |
| 2 — Supporting | BASS / BASS-II (PSI-26/25), SAFFIRE-III (PSI-100), SAME-R / SAME (PSI-101/102), SAFFIRE-II (PSI-99), CFI (PSI-39), SPICE (PSI-107) | Contexto material/flujo, telemetría de incendio a escala, detección de humo |
| 3 — Context | ACME BRE/CLD/E-FIELD/s-Flame, FLEX-2, SAFFIRE-I, SLICE, DAFT, investigaciones de tierra | Catálogo, ranking, RAG, brechas |

**Actualización DE-01 (2026-11-14):** los 3 XLSX de telemetría y sensores de SAFFIRE-I (PSI-98), que la referencia reportaba como
404, hoy devuelven HTTP 200. Evaluar SAFFIRE-I como fuente de telemetría en la triage.

**Actualización DE-04 (2026-11-14), tiers en borrador** ([investigations/README.md](../../02_data_engineering/investigations/README.md)):
- **Tier 1:** CFI-G (PSI-159), FLEX (PSI-69), **CFI (PSI-39, sube: tiene resultados procesados)** y ACME Flame Design (PSI-10; requiere unir con `EventData` para obtener el resultado de ignición).
- **Tier 2:** PSI-117 (de tierra, validación), BASS-II, BASS, SAFFIRE-I (sube: telemetría disponible), SAFFIRE-III, SAME-R, SAME, SPICE y SAFFIRE-II.
- **Tier 3:** el resto.

## Decisión
_Se completa en G1: lista final, archivos del manifest, bytes totales, justificación por la rúbrica de triage._

## Consecuencias
_Se completa en G1._
