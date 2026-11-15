# ADR-0008 — Contrato extractivo para el piloto RAG

- **Estado:** Implementado como restricción conservadora del piloto; aceptación de
  producto y gates de publicación pendientes. No constituye aprobación PHY.
- **Fecha:** 2026-11-15.
- **Base de implementación:** `ba1e104`; arquitectura ADR-0004 y límite de modelos ADR-0007.

## Contexto

El plan exige validación de respaldo semántico y numérico. Comprobar que una cita existe
no basta para verificar una paráfrasis generada. No hay todavía corpus revisado de
findings ni una evaluación live con rúbrica humana que permita publicar interpretaciones.

## Decisión para esta entrega

Mantener Next.js/FastAPI, consultas parametrizadas, embeddings E5 locales y ambos proveedores.
Restringir las afirmaciones generadas a extractos literales citados. Renderizar números,
unidades y ámbitos desde `ToolResult`, sin reconstrucción del modelo. Las preguntas y
mensajes admiten EN/ES; las citas conservan su idioma. El modo evidencia permanece local.

Las agrupaciones de herramientas son fijas y los rangos numéricos libres requieren
aclaración. No se admite `group_by` arbitrario. Mantener publicación de modelos bloqueada
en `/habitat`: ADR-0007 sigue autorizando conceptualmente lecturas controladas, pero no
se fabrican tiers ni valores sin artefacto y validación. No aprobar automáticamente docs.

## Consecuencias y salida de esta restricción

Esta entrega permite explorar fuentes y resultados exactos, pero no equivale a completar
la evaluación científica ni a una traducción/síntesis generativa bilingüe validada.
El benchmark offline inicial de 60 preguntas es una base de definiciones, no una prueba
general de calidad. Ampliarlo con preguntas naturales, ambigüedad, denegación y filtros;
evaluar proveedores con presupuesto y revisión humana antes de permitir paráfrasis.
Registrar una decisión posterior al ampliar el contrato. No cerrar gates por estos tests.

Los límites operativos, comandos, retención de evidencia y pendientes están en
[RAG_RUNBOOK.md](../../03_data_science/RAG_RUNBOOK.md).
