# Implementación de las mejoras de FlameSafe

## Lote 1. Ciencia, interfaz y entrega

- **FS-01, FS-02, FS-03, FS-04, FS-20, FS-21, FS-22, FS-24, FS-27, FS-28.** Reconciliación de las cohortes ISS y exploración con los notebooks, separación entre observaciones, dominio y gravedad, intervalos para persistencia condicionada y redacción revisada. El script de reconciliación reproduce las medianas, cuatro cortes y la ventana lunar. Quedan pendientes la calibración absoluta fuera de campaña y la validación independiente de la extrapolación.
- **FS-05, FS-06, FS-09, FS-41, FS-45.** Política de publicación aplicada al exportador, al corpus y a las rutas públicas. Contrato actualizado, identificador visible y comprobación de paridad en el gateway. El chat valida pasajes literales, con cifras exactas en herramientas tipadas. El registro YAML y el resumen bilingüe tienen una verificación localizada de cifras de referencia. Una entrega posterior puede terminar de derivar automáticamente las tablas de todas las fichas a partir de resultados versionados.
- **FS-07, FS-08, FS-38, FS-39, FS-40, FS-52.** La guía de release identifica comandos, revisión y responsables. El guion refleja la separación entre evidencia observada y lectura de modelo. Se preservaron los notebooks históricos. La asignación nominal y la revisión independiente siguen correspondiendo al equipo.

## Lote 2. Datos y procedencia

- **FS-10, FS-11, FS-12, FS-13, FS-15, FS-16, FS-17.** Paginación del catálogo, límites de descarga, staging, comprobación de identidades en Silver y Gold, excepción de diámetro y visibilidad del origen de pruebas en el mapa. Las discrepancias de ignición se conservan para adjudicación; faltan revisión manual y un registro público completo de hashes por fila.
- **FS-14, FS-18, FS-19, FS-23, FS-43, FS-50, FS-55.** Roles de referencias y ceros inferidos visibles para RQ2. Series y video conservan versión del extractor; se protege el modelo revisado y se registran diagnósticos de ajuste. El esquema de eventos y las condiciones de redistribución se describen en la agenda. La validación de calibración de sensores, verificación de licencias por archivo y adjudicación individual quedan pendientes.

## Lote 3. Uso para NASA

- **FS-29, FS-30, FS-31, FS-44, FS-46, FS-47, FS-48, FS-53.** Ficha compartible y exportable, mapa filtrable con tabla, comparación de investigaciones, ranking por PSI ID y sensibilidad conjunta. La agenda vincula las brechas con decisiones de prevención y cualificación. Quedan pendientes la validación entre evaluadores de las puntuaciones y confirmar el contexto de uso con equipos NASA.
- **FS-25, FS-26, FS-49, FS-51.** Scripts y protocolos para replay óptico causal, cobertura de gotas y evaluación de utilidad. El replay necesita fotogramas y etiquetas de término comparables. Una validación prospectiva o una calificación física requiere trabajo experimental adicional.

## Lote 4. Chat y operación

- **FS-32, FS-33, FS-34, FS-35.** Consultas filtradas y repetibles, resultados de cero filas preservados, benchmark bilingüe configurable por bundle y generación optativa en el benchmark. La evaluación comparativa híbrida y con proveedor real queda pendiente.
- **FS-36, FS-37, FS-42, FS-54.** Presupuesto total por petición, Firestore configurable, evidencia disponible si falla el ledger y métricas de estado y latencia sin registrar la pregunta. Se añadió un extra de presupuesto cloud. La reducción de tamaño del runtime, la provisión de Firestore y la promoción y reversión en producción quedan pendientes.
