# Despliegue separado

La ejecución local y los controles de publicación se describen en
[RAG_RUNBOOK.md](../docs/03_data_science/RAG_RUNBOOK.md).

`Dockerfile.api` prepara el proceso Python, sin secretos, pesos ni datos. Construir
desde la raíz: `docker build -f deploy/Dockerfile.api -t flamesafe-api .`.
Este Dockerfile se entrega para validación en un host Linux; no acredita un despliegue probado.

Montar un directorio de evidencias autorizado, en solo lectura, con `rag/CURRENT`,
el bundle completo seleccionado y `embedding-model/` (incluido el marcador de revisión).
Montar `/state` persistente y escribible por UID 10001 para el ledger SQLite.
Una instancia y un worker: no escalar horizontalmente con ledgers locales independientes.
Probar RAM, latencia, permisos de LanceDB sobre volumen de solo lectura y persistencia
tras reinicio antes de publicar. No exponer la API sin TLS/reverse proxy y autenticación.
La plataforma debe limitar tamaño de cuerpos HTTP y solicitudes por cliente.

Para Node: raíz `web/`, Node LTS >=22, `npm ci`, `npm run build`, `npm start`.
Configurar `FLAMESAFE_BACKEND_URL`, `FLAMESAFE_API_TOKEN` y un token de acceso de
dashboard distinto (`FLAMESAFE_WEB_ACCESS_TOKEN`) como secretos de servidor.
Verificar runtime, puerto y timeout de GoDaddy en la cuenta real. No usar variables
`NEXT_PUBLIC_` para secretos. El token compartido es adecuado para piloto privado;
un servicio público necesita identidad individual, sesiones y cuotas por usuario.

Readiness: `/health/ready`; liveness: `/health/live`. Sin bundle válido, readiness
responde 503, sin construir ni descargar durante una petición. Rotar secretos fuera
de Git. Para rollback, seleccionar un bundle anterior validado mediante reemplazo
atómico de `CURRENT` y reiniciar el worker; las peticiones en curso usan su snapshot.

No se han contratado servicios, publicado aplicaciones ni modificado DNS.
