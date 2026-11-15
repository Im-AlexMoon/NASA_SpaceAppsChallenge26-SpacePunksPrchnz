# RAG: ejecución local y límites de esta entrega

El plan vigente sigue siendo [RAG_IMPLEMENTATION_PLAN.md](RAG_IMPLEMENTATION_PLAN.md)
y ADR-0004. Este documento explica la implementación y sus controles de publicación;
no sustituye la revisión científica ni declara superadas las fases de evaluación live.

## Componentes

- `src/flamesafe/rag`: contratos, corpus elegible, fragmentación, E5 local, BM25/LanceDB,
  snapshots, nueve herramientas de consulta, adaptadores Gemini/OpenAI, ledger y servicio.
- `src/flamesafe/api/main.py`: API `/v1`, autenticación, concurrencia y disponibilidad.
- `web/`: ocho rutas Next.js, gateway privado y tipos generados de OpenAPI.
- `configs/rag_sources.yaml`: campos PSI y diccionario; documentos adicionales requieren
  hash, revisión, derechos de envío al proveedor y secciones aprobadas. La lista inicial
  de documentos revisados está vacía. No se adquirieron abstracts ni se aprobaron findings.

Python sigue siendo la autoridad de consultas y auditoría. No se modifican gold/silver,
notebooks ni modelos científicos. Streamlit permanece durante la aceptación de la migración.

## 1. Instalar y construir

Desde la raíz del repositorio en PowerShell, con Python 3.12 y uv:

```powershell
uv sync --locked --extra pipeline --extra analysis --extra api --extra rag --extra rag-gemini --extra rag-openai --extra dev
uv run --no-sync flamesafe rag-index --source-mode sample --allow-model-download
uv run --no-sync flamesafe rag-validate
uv run --no-sync flamesafe rag-eval --offline
uv run --no-sync flamesafe rag-ask --language es --evidence-only --question "¿De dónde viene burn_time_s?"
```

La descarga explícita obtiene la revisión fijada en `configs/rag.yaml`; ocupa cientos
de MB. No consume API generativa. Builds posteriores reutilizan los pesos locales:

```powershell
uv run --no-sync flamesafe rag-index --source-mode full
```

`full` exige las cinco tablas gold; no sustituye silenciosamente por muestras. Si
están disponibles los dos EventData silver, incorpora la auditoría existente y
habilita `audited_unique` y `audited_verified_dates`. Sin EventData esos ámbitos
fallan explícitamente. Las operaciones no representan independencia estadística.

Para desarrollo sin pesos: `rag-index --source-mode sample --retrieval-mode lexical`.
Es una modalidad degradada explícita, no equivalente al RAG multilingüe híbrido.
Los builds viven en `artifacts/rag/<build_id>`; `CURRENT` se reemplaza solo tras validar.
No se escribe sobre entradas medallion. Conservar el build anterior para rollback.

## 2. Gemini u OpenAI: activación deliberada

La clave existente en `.env` se reutiliza; nunca pegarla en código, frontend o Git.
El SDK no elige modelo automáticamente. Configurar un ID de modelo disponible en la
cuenta, compatible con salidas estructuradas. Retirar cualquier antiguo valor Claude
de `FLAMESAFE_LLM_MODEL`; `GEMINI_MODEL` se usa solo si aquel está vacío.

```dotenv
FLAMESAFE_LLM_PROVIDER=gemini
GEMINI_API_KEY=valor_privado
FLAMESAFE_LLM_MODEL=modelo_verificado_en_tu_cuenta
FLAMESAFE_GENERATION_ENABLED=true
FLAMESAFE_BILLING_MODE=free
FLAMESAFE_DAILY_CALLS=10
FLAMESAFE_MONTHLY_CALLS=50
```

Usar `free` únicamente después de confirmar el tier de ese proyecto/modelo. La app no
cambia facturación ni convierte una cuenta pagada en gratuita. Las cuotas anteriores
son un ejemplo conservador, no una configuración que se haya activado automáticamente.
Para OpenAI seleccionar `openai` y `OPENAI_API_KEY`; no existe failover.

En modo `paid` se exigen `FLAMESAFE_CALL_RESERVATION_USD`, `FLAMESAFE_DAILY_BUDGET_USD`
y `FLAMESAFE_MONTHLY_BUDGET_USD` positivos. La reserva por llamada debe cubrir su coste
máximo según precios y límites vigentes del modelo. Son límites de **reservas locales**,
no un límite de facturación del proveedor: no cubren llamadas desde otros programas ni
una reserva mal estimada. Configurar también alertas/límites disponibles en el proveedor.
Cada intento consume una reserva, incluso si falla, sin reembolso automático.

```powershell
uv run --no-sync flamesafe rag-ask --generate --language es --question "¿De dónde viene burn_time_s?"
```

Hasta tres llamadas por pregunta (plan, respuesta, reparación), máximo dos herramientas
y ocho fragmentos. Sin habilitación/cuotas, el modo evidencia sigue funcionando.
Solo se envían pregunta y evidencia elegible; no se envían tablas completas ni claves.
No se persisten preguntas completas. El ledger debe mantenerse entre reinicios.

## 3. API y dashboard

Definir un token aleatorio de backend en `.env` (`FLAMESAFE_API_TOKEN`). En otra terminal:

```powershell
uv run --no-sync uvicorn flamesafe.api.main:app --host 127.0.0.1 --port 8000 --workers 1
```

Copiar `web/.env.example` a `web/.env.local`. Introducir URL de backend y el mismo token
de backend; elegir además un token de acceso al dashboard distinto. Nunca usar la clave
Gemini como token de acceso. Los tokens de servidor no llegan al navegador.

```powershell
npm --prefix web ci
npm --prefix web run dev
```

En el equipo de esta implementación se instaló un runtime local para verificación
en `artifacts/node-runtime`, sin modificar la instalación del sistema. Si `npm` no
está en PATH y ese directorio existe, ejecutar primero desde la raíz:

```powershell
$env:PATH = "$PWD\artifacts\node-runtime\Scripts;$env:PATH"
```

En otro equipo instalar Node LTS >=22; ese runtime local no se distribuye en Git.

Abrir `http://127.0.0.1:3000`, introducir el token del dashboard y pulsar **Connect**.
El token de usuario se mantiene solo en memoria de la página; una navegación completa
puede requerir introducirlo nuevamente. El chat usa evidencia local por defecto.
Activar generación en el checkbox solo tras configurar proveedor y presupuesto.
La herramienta exacta del chat permite consultar sin ninguna llamada generativa.

El gateway permite rutas fijas, valida método/origen y limita cuerpos a 16 KiB.
La API exige Bearer salvo health, limita chat a 20 solicitudes/minuto por instancia y
dos solicitudes concurrentes. Estos controles corresponden a un piloto privado, no a
autenticación multiusuario pública. Configuración de hosting: [deploy/README.md](../../deploy/README.md).

## 4. Interpretación y diferencias deliberadas de esta primera entrega

- Generación **extractiva**: cada afirmación documental debe ser un extracto literal
  de todos los fragmentos citados. Las citas permanecen en su idioma; mensajes y preguntas
  admiten español/inglés. No se publica paráfrasis interpretativa generada sin evaluación.
- Los números de tablas se presentan directamente con unidades, denominadores, filtros,
  faltantes, hash y build. El modelo no reconstruye esos valores.
- Las herramientas tienen agrupaciones fijas; no aceptan SQL, `group_by` arbitrario ni
  rangos numéricos de texto libre. Preguntas con condiciones numéricas no soportadas
  requieren aclaración. Los resúmenes no establecen efectos causales ni comparabilidad
  completa entre combustibles: también importan dilución, protocolo y operaciones.
- No hay caché de respuestas generativas. Resultados de herramientas se retienen en
  memoria hasta una hora, máximo 256; `/v1/evidence/{id}` devuelve 404 tras expiración
  o reinicio. Para reproducir, conservar build y `normalized_parameters` y volver a
  ejecutar la herramienta contra ese mismo snapshot.
- El chat no emite predicciones. `/habitat` mantiene el bloqueo de publicación de modelos
  de ADR-0007 hasta disponer de artefactos y revisión; no inventa valores A/B/C.
- La lista de documentos adicionales y findings aprobados está vacía; el diccionario y
  los campos PSI seleccionados son la base inicial. No indexar todo `docs` para llenarla.
- La evaluación offline inicial tiene 60 preguntas / 30 pares bilingües centrados en
  definiciones con identificadores explícitos. No acredita recuperación de preguntas
  abiertas, calidad de planificación LLM, traducción, entailment ni revisión científica.
- La partición del código agrupa adaptadores en `providers.py` y orquestación/validación
  en `service.py`; mantiene los contratos del plan sin crear módulos vacíos por función.

## 5. Verificación y pasos restantes de publicación

```powershell
uv run --no-sync ruff check src tests app
uv run --no-sync pytest -m "not integration"
uv run --no-sync python scripts/export_openapi.py
npm --prefix web run generate
npm --prefix web run typecheck
npm --prefix web run lint
npm --prefix web test
npm --prefix web run build
npm --prefix web run test:e2e
```

Las pruebas de navegador usan Edge instalado en Windows y Chromium de Playwright en
Linux (`npx playwright install chromium` desde `web`). CI verifica divergencias OpenAPI/TS.
No ejecutar live tests en CI con claves. Revisar que los archivos medallion no cambiaron.

Antes de publicación: aprobar documentos exactos, ampliar el conjunto de evaluación con
preguntas naturales y filtros ambiguos, evaluar Gemini y OpenAI bajo presupuesto explícito,
revisar respaldo semántico humano, medir latencia/RAM y validar despliegue Linux y persistencia.
La implementación local no sustituye esos gates y no autoriza publicación ni gasto.
