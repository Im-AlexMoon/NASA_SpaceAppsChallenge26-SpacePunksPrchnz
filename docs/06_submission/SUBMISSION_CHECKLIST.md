# Checklist de entrega final (F8 · G8)

> La implementación se registra en [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md). Para comprobar el release vigente, seguir [RELEASE_PROCEDURE.md](RELEASE_PROCEDURE.md).

> Actualizado el 2026-11-15 tras completar los puntos 1, 3 y 4 de la propuesta de valor. ✔ hecho y verificado · ◐ parcial ·
> ☐ pendiente · ⚠️ bloqueante. "Luz verde para el frontend" = todo lo de §A está ✔.

## ⚠️ Requisitos oficiales (verificar HOY en spaceappschallenge.org)
Una búsqueda del 2026-11-15 indica que el envío de proyectos 2026 abrió el 14 de noviembre a las 9:00 hora local y que el hackathon
cierra el **15 de noviembre de 2026**; no se encontró la hora exacta de cierre. La guía oficial exige un *Project Demo* y que los videos
tengan subtítulos en inglés. No hay ediciones después del cierre.
- [ ] ⚠️ Hora exacta de cierre (local y UTC) según la *2026 Project Submission Guide*
- [ ] ⚠️ Formato y duración máxima del demo (video o presentación)
- [ ] Campos obligatorios de la página del proyecto
- [ ] Declaración de uso de IA (el proyecto usó IA para análisis, código y redacción; la firma PHY es humana)

## A. Luz verde para el frontend (contenido y API)
- [x] **Punto 1 · Encontrar:** ranking MCDA de las 24 investigaciones, 5 perfiles, pesos ajustables, sensibilidad estable — `/v1/ranking*`
- [x] **Punto 3 · Entender:** 5 hallazgos con interpretación física firmada (F-01..F-05) — `/v1/findings`
- [x] **Punto 4 · Predecir:** lecturas por atmósfera con niveles A/B/C, IC 90 %, pruebas cercanas y aviso de gravedad — `/v1/readings/*`
- [x] Model card M-01 v2 firmada; artefacto versionado dentro del paquete
- [x] Física completa (F7/G7): primer, literatura verificada (20 refs), atmósferas con citas, PHY-04, PHY-05, REC-01..REC-07
- [x] Interruptor de publicación por bloque (`configs/publication.yaml`, ADR-0007)
- [x] Contrato OpenAPI y tipos TypeScript regenerados; 186 pruebas Python, ruff; web lint, tipos, pruebas y build
- [x] Guía para el equipo web: [FRONTEND_HANDOFF.md](../05_dashboard/FRONTEND_HANDOFF.md)
- [x] Corpus del RAG con 11 documentos revisados (76 fragmentos)

## B. Producto (pendiente tras el frontend)
- [x] Páginas: inicio con llama en microgravedad (WebGL), Atmosphere Explorer, Findings (F-01..F-05, ley de duración en F-02), Gaps,
  Investigations (ranking con pesos y reordenamiento animado), Ask the data, Methods — `web/` (2026-11-15); e2e 5/5
- [ ] Dashboard desplegado: web en **Vercel** (ADR-0011, `deploy/VERCEL.md`; requiere la cuenta del responsable) y API en Cloud Run solo para el chat (ADR-0010)
- [ ] Probado en navegador limpio (incógnito) y en móvil; sin errores en consola
- [x] Cada figura con unidades y leyenda; niveles de evidencia y banner de gravedad visibles (e2e los verifica)
- [ ] Índice del RAG **híbrido** en el despliegue (pesos E5 en el bucket de evidencia); hoy validado en modo léxico
- [ ] Chat: preguntas de la demo con respuesta verificada (modo evidencia; generación desactivada por defecto)
- [ ] Revisión final de la app completa (presentación, textos, accesibilidad)

## C. Repositorio
- [ ] README en inglés actualizado: problema, solución, capturas, URL de la demo, arquitectura (Cloud Run + GoDaddy), datos, equipo
- [x] Sin secretos ni datos crudos en Git; ningún archivo > 5 MB (artefacto M-01 v2: 60 KB)
- [ ] `make pipeline` / `uv run flamesafe ...` y pruebas desde un clon limpio en otra máquina
- [ ] Tag `v1.0`
- [ ] Créditos: NASA PSI (PSI-IDs, DOIs de datos), publicaciones citadas, ADR-0003 (repositorio de referencia), librerías y Cantera

## D. Ciencia
- [x] Hallazgos publicados con revisión PHY (F-01..F-05)
- [x] Model card completa (M-01 v2)
- [x] RECOMMENDATIONS.md con ≥ 5 recomendaciones con evidencia (7)
- [x] Limitaciones explícitas: sin gravedad parcial, llamas de gas de laboratorio, tamaños de muestra, hueco de O₂
- [ ] ◐ RQ2 (gotas, supresión por diluyentes) y DS-03 (ratificar RQs): fuera del alcance de la luz verde; declarar como trabajo futuro si no se completan

## E. Presentación
- [ ] Guion ([DEMO_SCRIPT.md](DEMO_SCRIPT.md)) reescrito alrededor de la idea central: "cuánto sabe NASA, con qué evidencia y dónde no sabe nada"
- [ ] Ensayado ≥ 2 veces
- [ ] Video con subtítulos en inglés, subido y con enlace público
- [ ] Página del proyecto enviada en Space Apps; captura de confirmación guardada
