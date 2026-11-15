"""Append the documented segmentation workflow without altering preceding cells.

Run from the repository root. Re-running replaces only this generated appendix.
The notebook remains the executable analysis; identity rules live in analysis/.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import nbformat

from flamesafe.analysis.notebook_sections import replace_section

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "notebooks" / "02_eda" / "02_eda_legit.ipynb"
MARKER = "<!-- FLAMESAFE:SEGMENTATION:BEGIN -->"


def main():
    nb = nbformat.read(PATH, as_version=4)
    old = next((i for i, c in enumerate(nb.cells) if MARKER in c.source), len(nb.cells))
    added = []

    def md(source):
        added.append(nbformat.v4.new_markdown_cell(textwrap.dedent(source).strip()))

    def code(source):
        added.append(nbformat.v4.new_code_cell(textwrap.dedent(source).strip()))

    md(r'''
    <!-- FLAMESAFE:SEGMENTATION:BEGIN -->
    ## Revisión del EDA y metodología de segmentación experimental

    **Fecha de revisión: 2026-11-15. Unidad de observación: una prueba experimental,
    identificada por `psi_id + test_id`.** Las celdas anteriores se conservan como
    exploración global; esta sección establece qué comparaciones son interpretables.

    ### Qué se ha explorado y cuáles son sus límites

    Hasta aquí se cargaron 660 pruebas mediante DuckDB y se revisaron tipos, ejemplos,
    histogramas, KDE, correlaciones con elipses, PCA estandarizado con imputación por
    mediana y pares correlacionados mediante densidades y violines. Es un mapa inicial,
    no evidencia de causalidad ni de capacidad predictiva. Los violines describen
    distribuciones marginales y no la relación emparejada entre dos variables.

    - Hay cuatro grupos de origen: CFI-G normal (179), CFI-G inversa (154), Flame
      Design normal (207) y Flame Design inversa (120). Campaña y combustible están
      parcialmente confundidos: etileno solo aparece en Flame Design; etano y butano,
      solo en CFI-G. Por ello una correlación global puede reflejar mezcla de diseños.
    - La etiqueta `ignited` no tiene una fuente equivalente entre campañas: CFI-G
      conserva `Hot ignition`; Flame Design deriva `Ignite` de EventData. Flame Design
      tiene 323 positivos y dos negativos entre 325 etiquetas conocidas; se conserva
      como contexto, sin combinarlo con CFI-G para el clasificador inicial.
    - Los ocho `flash` pertenecen a CFI-G inversa; se preservan como categoría y no se
      recodifican a positivo/negativo. No equiparar ignición con llama sostenida.
    - Normal e inversa intercambian el papel de la corriente del quemador y el ambiente.
      `xo2`, `x_fuel` y los caudales deben interpretarse según geometría. En particular,
      `po2_kpa` no se interpreta automáticamente como oxígeno de toda la cámara en inversas.
    - Los faltantes son parcialmente estructurales: `m_n2_mg_s` solo se incorpora desde
      Flame Design y los caudales de combustible/oxígeno dependen de la geometría.
      `RAMP`, `RAMPED` y `LOW O2` describen condiciones especiales, no valores numéricos
      para rellenar con una mediana. `cool_flame` tiene solo ocho respuestas informadas.
    - `po2_kpa` se calcula como `xo2 * p_kpa`; `zst` y `tad_k` son cantidades calculadas.
      Identificadores, `tier`, etiquetas y resultados posteriores a la prueba no son
      entradas intercambiables con condiciones iniciales. El PCA global anterior puede
      reflejar el patrón de faltantes y la imputación; no se usa para seleccionar predictores.
    - En la selección previa, `categorical_data` se sobrescribe con booleanos. Las nuevas
      celdas crean objetos independientes y distinguen booleanos anulables explícitamente.

    ### Reglas operativas, fijadas antes del análisis segmentado

    1. **Auditar el merge y la identidad.** Recargar gold y unir metadatos de investigación
       con `validate='many_to_one'`. Normalizar espacios/mayúsculas en los identificadores.
       Una copia solo se retira si comparte identidad y todos los campos científicos;
       cualquier diferencia científica bajo la misma identidad se deja en cuarentena.
       Se conserva el registro de filas retiradas y su procedencia.
    2. **Verificar cronología desde silver/EventData.** Usar `TP` para normales e `INV_TP`
       para inversas y unir por investigación/prueba sin multiplicar filas. Si EventData
       tiene versiones incompatibles de una prueba, no elegir arbitrariamente la primera.
       Conservar archivo/fila de ambos orígenes, inicio/fin GMT y banderas de calidad.
       Fechas desconocidas siguen desconocidas; no se deducen del identificador.
    3. **Distinguir duplicados, jornadas y réplicas.** Mismo día no significa misma prueba.
       Dos IDs distintos con condiciones registradas idénticas son candidatos a réplica,
       no duplicados demostrados. Se conservan para estimar variabilidad. La firma compara
       valores exactos, sin redondeo, con cobertura completa y dentro de una familia;
       no garantiza equivalencia de condiciones no registradas. Los casos cercanos pero
       no idénticos requieren tolerancias físicas acordadas antes de agruparlos.
    4. **Segmentación jerárquica.** Familia base = campaña × tipo de llama × combustible.
       Familia estricta añade porcentaje de combustible de botella, año observado en
       EventData, protocolo y origen de etiqueta. El porcentaje de botella no sustituye
       `x_fuel`. `no_informada` y `sin_fecha` se mantienen explícitos, sin asumir 100 %.
       Año es un bloqueo inicial de procedencia, no prueba de equivalencia instrumental.
       Flujo cero se etiqueta aparte como posible control; no se borra ni se supone que
       todos los registros sin qualifier sean estacionarios.
    5. **Control de calidad conservador.** Conflictos de identidad, operación incompatible,
       colisión temporal exacta o final anterior al inicio se apartan del análisis principal
       y permanecen disponibles para revisión/sensibilidad. Una fecha ausente, por sí sola,
       no invalida una prueba ni prueba duplicación. No se corrige la fuente desde el notebook.
    6. **EDA condicional.** Describir todas las familias y faltantes; separar protocolos
       especiales y controles. Recalcular distribuciones y correlaciones dentro de familias.
       Pearson/Spearman requieren al menos 20 pares y variación. El nuevo PCA usa condiciones
       aplicables por geometría, estandarización y casos completos, sin imputación estructural.
       Los grupos pequeños o constantes se documentan, no se fuerzan a un PCA.
    7. **Dependencia y validación futura.** No declarar independencia por haber eliminado
       duplicados. Mantener bloques de operación y secuencias relacionadas. El prefijo del ID
       se usa como token nominal del bloque, nunca como fecha UTC. Las jornadas pueden cruzar
       medianoche; `test_day` se conserva y se audita. La validación y los intervalos futuros
       deben agrupar por operación/campaña, con sensibilidad por fuente/periodo. Aquí se hace
       análisis descriptivo: no se presentan pruebas de hipótesis ni p-valores exploratorios.

    Las fuentes, conteos y anomalías se calculan de nuevo en las celdas siguientes.
    Los archivos gold/silver se leen sin modificarlos. Los resultados auxiliares se guardan
    en `artifacts/eda_segmentation/` y no sustituyen los datos originales.
    ''')

    code(r'''
    from pathlib import Path
    from itertools import combinations
    import hashlib
    import json
    import math

    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from IPython.display import display, Markdown
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler

    from flamesafe import config
    from flamesafe.analysis.segmentation import (
        audit_gas_observations, family_summary, condition_candidates,
    )

    sns.set_theme(style="whitegrid", context="notebook")
    ROOT_EDA = config.ROOT
    DATA_EDA = config.data_dir()
    OUT_EDA = ROOT_EDA / "artifacts" / "eda_segmentation"
    OUT_EDA.mkdir(parents=True, exist_ok=True)
    SEED_EDA = 42
    MIN_PARES_EDA = 20

    archivos_eda = [
        DATA_EDA / "gold" / "gas_flame_tests.parquet",
        DATA_EDA / "gold" / "investigations.parquet",
        DATA_EDA / "silver" / "tables" / "psi159__eventdata.parquet",
        DATA_EDA / "silver" / "tables" / "psi10__eventdata.parquet",
    ]
    for archivo in archivos_eda:
        if not archivo.exists():
            raise FileNotFoundError(f"Falta {archivo}; reconstruir el pipeline antes del EDA.")

    gas_origen_eda = pd.read_parquet(archivos_eda[0])
    investigaciones_eda = pd.read_parquet(archivos_eda[1])
    metadatos_eda = ["psi_id", "acronym", "tier", "hardware_family", "environments"]
    gas_base_segmentacion = gas_origen_eda.merge(
        investigaciones_eda[metadatos_eda], on="psi_id", how="left",
        validate="many_to_one", indicator="_metadata_merge",
    )
    assert gas_base_segmentacion["_metadata_merge"].eq("both").all(), "Metadatos sin correspondencia"
    gas_base_segmentacion = gas_base_segmentacion.drop(columns="_metadata_merge")
    eventos_eda = pd.concat([pd.read_parquet(p) for p in archivos_eda[2:]], ignore_index=True)
    auditoria_gas = audit_gas_observations(gas_base_segmentacion, eventos_eda)
    gas_auditado = auditoria_gas.observations
    gas_unicos = auditoria_gas.unique
    gas_segmentado = gas_unicos.loc[gas_unicos["audit_ok"]].copy()

    mapa_familias = pd.DataFrame({"family_id": sorted(gas_auditado["family_id"].unique())})
    mapa_familias["family_code"] = [f"F{i:02d}" for i in range(1, len(mapa_familias) + 1)]
    codigo_familia = mapa_familias.set_index("family_id")["family_code"]
    for tabla in [gas_auditado, gas_unicos, gas_segmentado]:
        tabla["family_code"] = tabla["family_id"].map(codigo_familia)

    manifiesto_eda = pd.DataFrame([{
        "file": str(p.relative_to(DATA_EDA)), "bytes": p.stat().st_size,
        "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
    } for p in archivos_eda])
    display(manifiesto_eda)
    display(auditoria_gas.summary)
    assert len(gas_auditado) == len(gas_base_segmentacion), "El enlace temporal multiplicó filas"
    assert not gas_unicos.duplicated(["psi_id", "test_id"]).any()
    ''')

    md(r'''
    ### Identidad, fechas y casos que requieren revisión

    La tabla siguiente separa ausencia de timestamp, inconsistencias y copias confirmadas.
    `duration_event_s` es la duración del evento operativo, **no** `burn_time_s`.
    No se restaura un fin incorrecto sumándole un día sin contrastar la fuente.
    ''')
    code(r'''
    columnas_revision = [
        "psi_id", "test_id", "campaign", "flame_type", "test_day", "identity_status",
        "t_start_gmt", "t_end_gmt", "duration_event_s", "event_op_mismatch",
        "negative_event_duration", "event_identity_conflict", "temporal_collision",
        "source_file", "source_row", "event_source_file", "event_source_row",
    ]
    gas_revision = gas_auditado.loc[~gas_auditado["audit_ok"], columnas_revision]
    gas_sin_timestamp = gas_unicos.loc[gas_unicos["t_start_gmt"].isna(), columnas_revision]
    display(Markdown("**Anomalías o conflictos (conservados para revisión):**"))
    display(gas_revision)
    display(Markdown("**Pruebas sin timestamp verificable:**"))
    display(gas_sin_timestamp)
    display(Markdown("**Copias idénticas retiradas, si las hay:**"))
    display(auditoria_gas.removed_copies)
    if not auditoria_gas.event_conflicts.empty:
        display(auditoria_gas.event_conflicts)

    # Ninguna de estas filas se elimina solo por compartir fecha.
    por_fecha_utc = (
        gas_unicos.dropna(subset=["utc_date"])
        .groupby(["psi_id", "campaign", "flame_type", "utc_date"], dropna=False)
        .agg(n_pruebas=("test_id", "nunique"), bloques=("operation_group", "nunique"))
        .reset_index()
    )
    por_operacion = (
        gas_unicos.groupby("operation_group")
        .agg(n_pruebas=("test_id", "nunique"), n_test_day=("test_day", "nunique"),
             n_fechas_utc=("utc_date", "nunique"),
             inicio=("t_start_gmt", "min"), fin=("t_start_gmt", "max"))
        .reset_index()
    )
    display(Markdown("**Bloques con pruebas en más de una fecha UTC:**"))
    display(por_operacion.loc[por_operacion["n_fechas_utc"] > 1])
    if por_operacion["n_test_day"].gt(1).any():
        print("ATENCIÓN: revisar bloques que reúnen varios test_day antes de validar modelos.")

    fig, ax = plt.subplots(figsize=(13, 4))
    for (campana, tipo), g in por_fecha_utc.groupby(["campaign", "flame_type"]):
        ax.scatter(pd.to_datetime(g["utc_date"]), [f"{campana} | {tipo}"] * len(g),
                   s=15 + 7 * g["n_pruebas"], alpha=0.6)
    ax.set(title="Cobertura temporal: tamaño del punto proporcional al número de pruebas",
           xlabel="Fecha UTC de inicio", ylabel="Grupo de origen")
    plt.tight_layout()
    plt.show()
    ''')

    md(r'''
    ### Familias y cohortes explícitas

    Se mantienen todas las pruebas únicas y se construyen vistas analíticas separadas.
    La cohorte binaria inicial excluye `flash`, posibles controles de flujo cero y
    anomalías de auditoría; esas observaciones siguen disponibles en tablas de revisión.
    Las fechas ausentes se mantienen en familias `sin_fecha` y se evalúan por sensibilidad.
    La dilución de botella es una etiqueta de procedencia, no una fracción medida en cámara.
    ''')
    code(r'''
    segmentos_gas = {nombre: g.copy() for nombre, g in gas_segmentado.groupby("family_id")}
    gas_cfig_eda = gas_segmentado.loc[
        gas_segmentado["campaign"].eq("CFI-G")
        & gas_segmentado["protocol_group"].eq("sin_anotacion")
    ].copy()
    gas_cfig_binario = gas_segmentado.loc[gas_segmentado["is_cfig_binary"]].copy()
    gas_flash = gas_segmentado.loc[gas_segmentado["ignition_outcome"].eq("flash")].copy()
    gas_contexto_fd = gas_segmentado.loc[gas_segmentado["campaign"].eq("Flame Design")].copy()
    gas_protocolos = gas_segmentado.loc[~gas_segmentado["protocol_group"].eq("sin_anotacion")].copy()

    resumen_familias = family_summary(gas_segmentado).merge(mapa_familias, on="family_id", validate="one_to_one")
    display(resumen_familias[["family_code", "family_id", "n", "operation_groups", "without_timestamp",
                              "yes", "no", "flash", "missing_label", "yes_pct_binary"]])
    display(pd.DataFrame({
        "vista": ["Original", "Únicos", "Sin anomalías", "CFI-G EDA sin controles",
                  "CFI-G binario", "Flash", "Contexto Flame Design", "Protocolos/controles"],
        "n": [len(gas_base_segmentacion), len(gas_unicos), len(gas_segmentado), len(gas_cfig_eda),
              len(gas_cfig_binario), len(gas_flash), len(gas_contexto_fd), len(gas_protocolos)],
    }))
    print("Las vistas se superponen: no sumar sus tamaños como si fueran particiones.")

    resultados_origen = pd.crosstab(
        [gas_unicos["campaign"], gas_unicos["flame_type"]],
        gas_unicos["ignition_outcome"].fillna("sin_resultado"),
    ).reindex(columns=["yes", "no", "flash", "sin_resultado"], fill_value=0)
    display(resultados_origen)
    resultados_origen.plot.bar(stacked=True, figsize=(11, 4),
                               color=["#2878B5", "#D55E00", "#E8B339", "#999999"])
    plt.ylabel("Número de pruebas únicas")
    plt.xlabel("Campaña y tipo de llama")
    plt.title("Balance observado: las etiquetas de las campañas no se presuponen equivalentes")
    plt.xticks(rotation=15, ha="right")
    plt.tight_layout()
    plt.show()
    ''')

    md(r'''
    ### Condiciones repetidas: candidatos a réplica y dependencia

    Se buscan coincidencias exactas en condiciones registradas completas dentro de
    la familia estricta. Cambiar de ID o de hora distingue ensayos; no se colapsan sus
    resultados. Las réplicas pueden revelar variabilidad real o condiciones omitidas.
    `hc_burnrate_mg_s` se usa solo para contrastar registros inversos CFI-G en esta
    auditoría; su semántica pendiente impide tratarlo como caudal de alimentación en PCA.
    ''')
    code(r'''
    candidatos_replicas = condition_candidates(gas_segmentado)
    if candidatos_replicas.empty:
        grupos_replicas = pd.DataFrame()
        print("No hay coincidencias exactas completas en las condiciones seleccionadas.")
    else:
        grupos_replicas = (
            candidatos_replicas.groupby(["family_id", "settings"])
            .agg(n_pruebas=("test_id", "size"),
                 n_bloques=("operation_group", "nunique"),
                 n_resultados=("ignition_outcome", "nunique"),
                 pruebas=("test_id", lambda s: ", ".join(s)))
            .reset_index()
        )
        grupos_replicas["family_code"] = grupos_replicas["family_id"].map(codigo_familia)
        display(grupos_replicas[["family_code", "n_pruebas", "n_bloques", "n_resultados", "pruebas", "settings"]])
        print(f"{len(candidatos_replicas)} filas en {len(grupos_replicas)} grupos de condiciones idénticas.")
        print("No se retira ninguna: son candidatos a réplica, no copias del mismo experimento.")
    display(gas_flash[["psi_id", "test_id", "family_code", "fuel", "xo2", "p_kpa",
                       "burn_time_s", "extinction_mode", "t_start_gmt"]])
    ''')

    md(r'''
    ### Faltantes y variables aplicables

    Las columnas de la matriz siguiente se seleccionan explícitamente como condiciones
    o resultados. Identificadores y metadatos numéricos no se grafican como mediciones.
    El nuevo EDA no rellena faltantes estructurales. Una columna nula no significa flujo cero.
    ''')
    code(r'''
    variables_cobertura = [
        "xo2", "p_kpa", "x_fuel", "m_fuel_mg_s", "m_o2_mg_s", "m_n2_mg_s",
        "zst", "tad_k", "ignited", "burn_time_s", "cool_flame",
    ]
    faltantes_por_origen = (
        gas_unicos.groupby(["campaign", "flame_type"])[variables_cobertura]
        .agg(lambda s: 100 * s.isna().mean())
    ).astype(float)
    fig, ax = plt.subplots(figsize=(13, 4))
    sns.heatmap(faltantes_por_origen, annot=True, fmt=".0f", vmin=0, vmax=100,
                cmap="YlOrRd", cbar_kws={"label": "% faltantes"}, ax=ax)
    ax.set_title("Ausencia de datos por grupo experimental")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

    variables_por_geometria = {
        "normal": ["xo2", "p_kpa", "x_fuel", "m_fuel_mg_s"],
        "inverse": ["xo2", "p_kpa", "x_fuel", "m_o2_mg_s"],
    }
    mediciones_eda = gas_segmentado.select_dtypes(include="number").drop(
        columns=["test_day", "source_row", "tier", "_input_row", "event_source_row"], errors="ignore"
    )
    booleanos_eda = gas_segmentado.select_dtypes(include=["bool", "boolean"])
    perfil_familias = []
    for familia, g in segmentos_gas.items():
        for variable in variables_por_geometria[g["flame_type"].iloc[0]]:
            valores = g[variable].replace([np.inf, -np.inf], np.nan)
            perfil_familias.append({
                "family_id": familia, "family_code": g["family_code"].iloc[0],
                "variable": variable, "n": len(g), "validos": valores.notna().sum(),
                "faltantes_pct": valores.isna().mean() * 100, "n_unicos": valores.nunique(),
                "min": valores.min(), "mediana": valores.median(), "max": valores.max(),
            })
    perfil_familias = pd.DataFrame(perfil_familias)
    display(perfil_familias.round(3))
    ''')

    md(r'''
    ### Distribuciones condicionales de CFI-G

    Las curvas acumuladas empíricas (ECDF) permiten comparar cobertura sin suavizar
    fuera de límites físicos. Cada curva mantiene combustible, dilución y periodo.
    Las muestras de una fila se muestran como puntos y no como densidades inferidas.
    ''')
    code(r'''
    fig, axes = plt.subplots(2, 3, figsize=(17, 9), layout="constrained")
    for fila, geometria in enumerate(["normal", "inverse"]):
        g_tipo = gas_cfig_eda.loc[gas_cfig_eda["flame_type"].eq(geometria)]
        for ax, variable in zip(axes[fila], ["xo2", "p_kpa", "x_fuel"]):
            for familia, g in g_tipo.groupby("family_id"):
                valores = np.sort(g[variable].dropna().to_numpy())
                if not len(valores):
                    continue
                etiqueta = f"{g['family_code'].iloc[0]}: {g['fuel'].iloc[0]}, {g['dilution_group'].iloc[0]}, {g['period_group'].iloc[0]} (n={len(valores)})"
                ax.step(valores, np.arange(1, len(valores) + 1) / len(valores), where="post", label=etiqueta)
                if len(valores) == 1:
                    ax.plot(valores, [1], "o")
            ax.set(title=f"CFI-G {geometria}: {variable}", xlabel=variable, ylabel="Fracción acumulada", ylim=(0, 1.05))
            ax.legend(fontsize=7, loc="best")
    plt.show()

    # Histogramas/KDE por familia: distribución del diseño experimental, no del riesgo poblacional.
    familias_graficables = [
        (nombre, g) for nombre, g in gas_cfig_eda.groupby("family_id") if len(g) >= MIN_PARES_EDA
    ]
    for comienzo in range(0, len(familias_graficables), 3):
        lote = familias_graficables[comienzo:comienzo + 3]
        fig, axes = plt.subplots(len(lote), 3, figsize=(15, 3.2 * len(lote)), squeeze=False, layout="constrained")
        for fila, (familia, g) in enumerate(lote):
            geometria = g["flame_type"].iloc[0]
            flujo = variables_por_geometria[geometria][-1]
            for ax, variable in zip(axes[fila], ["xo2", "p_kpa", flujo]):
                valores = g[variable].replace([np.inf, -np.inf], np.nan).dropna()
                sns.histplot(x=valores, stat="density", bins=min(15, max(4, valores.nunique())), ax=ax, color="#2878B5")
                if valores.nunique() >= 5 and len(valores) >= MIN_PARES_EDA:
                    sns.kdeplot(x=valores, cut=0, color="#D55E00", ax=ax, warn_singular=False)
                ax.set(title=f"{g['family_code'].iloc[0]} | {geometria} | {g['fuel'].iloc[0]} | {g['dilution_group'].iloc[0]}\n{variable}: n={len(valores)}", ylabel="Densidad", xlabel=variable)
        plt.show()
    ''')

    md(r'''
    ### Correlaciones dentro de familias y contraste con la mezcla global

    Solo condiciones aplicables por geometría, sin resultados ni `po2_kpa` derivada.
    Cada coeficiente informa su número de pares completos; Pearson y Spearman se
    calculan sin imputación. Las correlaciones siguen siendo descriptivas y pueden
    reflejar condiciones elegidas conjuntamente. No se comparan tamaños de coeficientes
    como si provinieran de muestras independientes ni se afirma una paradoja de Simpson.
    ''')
    code(r'''
    filas_corr = []
    for familia, g in gas_segmentado.loc[gas_segmentado["protocol_group"].eq("sin_anotacion")].groupby("family_id"):
        variables = variables_por_geometria[g["flame_type"].iloc[0]]
        for a, b in combinations(variables, 2):
            par = g[[a, b]].replace([np.inf, -np.inf], np.nan).dropna()
            if len(par) < MIN_PARES_EDA or par.nunique().min() < 2:
                continue
            global_par = gas_segmentado[[a, b]].replace([np.inf, -np.inf], np.nan).dropna()
            filas_corr.append({
                "family_id": familia, "family_code": g["family_code"].iloc[0],
                "variable_1": a, "variable_2": b, "n": len(par),
                "n_operaciones": g.loc[par.index, "operation_group"].nunique(),
                "pearson": par[a].corr(par[b]), "spearman": par[a].corr(par[b], method="spearman"),
                "pearson_mezcla_global": global_par[a].corr(global_par[b]),
                "n_mezcla_global": len(global_par),
            })
    correlaciones_familia = pd.DataFrame(filas_corr)
    if not correlaciones_familia.empty:
        correlaciones_familia["abs_r"] = correlaciones_familia["pearson"].abs()
        correlaciones_familia = correlaciones_familia.sort_values("abs_r", ascending=False).reset_index(drop=True)
        display(correlaciones_familia.drop(columns="family_id").round(3))

        seleccion_corr = correlaciones_familia.loc[correlaciones_familia["abs_r"] > 0.60].head(6)
        if len(seleccion_corr):
            fig, axes = plt.subplots(math.ceil(len(seleccion_corr) / 3), 3,
                                     figsize=(16, 4 * math.ceil(len(seleccion_corr) / 3)),
                                     squeeze=False, layout="constrained")
            for ax, r in zip(axes.flat, seleccion_corr.itertuples(index=False)):
                g = segmentos_gas[r.family_id]
                sns.scatterplot(data=g, x=r.variable_1, y=r.variable_2,
                                hue="ignition_outcome", hue_order=["yes", "no", "flash"],
                                palette={"yes": "#2878B5", "no": "#D55E00", "flash": "#E8B339"}, ax=ax, alpha=0.75)
                ax.set_title(f"{r.family_code}: r={r.pearson:.2f}, rho={r.spearman:.2f}\nn={r.n}; operaciones={r.n_operaciones}")
            for ax in axes.flat[len(seleccion_corr):]:
                ax.set_visible(False)
            plt.show()
    else:
        print("No hay familias con suficientes pares variables para correlación.")
    ''')

    md(r'''
    ### PCA por familia: sin imputación y con cobertura explícita

    Se exige al menos 80 % de cobertura por variable, variación en la familia y al menos
    20 casos completos. Se vuelve a comprobar variación y rango matricial después del
    filtro. No se rellenan caudales no aplicables. Familias con una sola operación no
    permiten evaluar generalización entre operaciones, aunque produzcan un PCA.
    El PCA representa variación del diseño y no importancia causal para la ignición.
    ''')
    code(r'''
    resultados_pca_familia = {}
    resumen_pca_filas = []
    diagnostico_pca = []
    for familia, g in gas_cfig_eda.groupby("family_id"):
        candidatas = variables_por_geometria[g["flame_type"].iloc[0]]
        x = g[candidatas].replace([np.inf, -np.inf], np.nan).astype(float)
        columnas = [c for c in x if x[c].notna().mean() >= 0.80 and x[c].nunique() > 1]
        completos = x[columnas].dropna()
        completos = completos.loc[:, completos.nunique() > 1]
        razon = "apta"
        if completos.shape[1] < 2:
            razon = "menos de dos condiciones con variación"
        elif len(completos) < MIN_PARES_EDA:
            razon = "menos de 20 casos completos"
        else:
            z = StandardScaler().fit_transform(completos)
            if np.linalg.matrix_rank(z) < 2:
                razon = "rango matricial menor de dos"
        diagnostico_pca.append({"family_code": g["family_code"].iloc[0], "n_familia": len(g),
                               "n_completos": len(completos), "variables": ", ".join(completos.columns), "estado": razon})
        if razon != "apta":
            continue
        modelo = PCA().fit(z)
        acumulada = modelo.explained_variance_ratio_.cumsum()
        pesos = pd.DataFrame(modelo.components_.T, index=completos.columns,
                             columns=[f"PC{i + 1}" for i in range(len(acumulada))])
        resultados_pca_familia[familia] = {"modelo": modelo, "pesos": pesos, "indices": completos.index,
                                          "scores": modelo.transform(z), "acumulada": acumulada}
        resumen_pca_filas.append({
            "family_id": familia, "family_code": g["family_code"].iloc[0],
            "n_familia": len(g), "n_completos": len(completos),
            "operaciones": g.loc[completos.index, "operation_group"].nunique(),
            "variables": ", ".join(completos.columns),
            "pc1_pct": 100 * modelo.explained_variance_ratio_[0],
            "k90": min(len(acumulada), int(np.searchsorted(acumulada, 0.90)) + 1),
        })
    resumen_pca = pd.DataFrame(resumen_pca_filas)
    diagnostico_pca = pd.DataFrame(diagnostico_pca)
    display(diagnostico_pca)
    display(resumen_pca.round(2))
    if resultados_pca_familia:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5), layout="constrained")
        for familia, resultado in resultados_pca_familia.items():
            pc = np.arange(1, len(resultado["acumulada"]) + 1)
            axes[0].plot(pc, 100 * resultado["modelo"].explained_variance_ratio_, "o-", label=codigo_familia[familia])
            axes[1].plot(pc, 100 * resultado["acumulada"], "o-", label=codigo_familia[familia])
        axes[0].set(title="Varianza por componente dentro de cada familia", xlabel="Componente", ylabel="Varianza (%)")
        axes[1].set(title="Varianza acumulada por familia", xlabel="Componentes", ylabel="Varianza (%)", ylim=(0, 105))
        axes[1].axhline(90, ls="--", color="gray")
        for ax in axes:
            ax.legend(fontsize=8)
        plt.show()
        for familia, resultado in resultados_pca_familia.items():
            print(codigo_familia[familia], "- pesos de los dos primeros componentes")
            display(resultado["pesos"].iloc[:, :2].round(3))
    ''')

    md(r'''
    ### Sensibilidad, conclusiones y trazabilidad

    No se descartan posibles réplicas para obtener artificialmente independencia.
    Las proporciones de positivos siguientes son descriptivas: el promedio por operación
    asigna igual peso a cada bloque, mientras el promedio por prueba pesa más los bloques
    con más ensayos. No son estimaciones de riesgo para una población de misiones.
    Se compara también la inclusión del registro con cronología incorrecta, sin corregirlo,
    y la exclusión de fechas no verificadas. `flash` continúa fuera del objetivo binario.
    ''')
    code(r'''
    base_sensibilidad = gas_unicos.loc[
        gas_unicos["campaign"].eq("CFI-G")
        & gas_unicos["outcome_source"].eq("experimental_table")
        & gas_unicos["ignited"].notna()
        & gas_unicos["protocol_group"].eq("sin_anotacion")
        & ~gas_unicos["event_identity_conflict"] & ~gas_unicos["event_op_mismatch"]
        & ~gas_unicos["temporal_collision"]
    ]
    escenarios = {
        "Principal: CFI-G binario sin controles ni anomalías": gas_cfig_binario,
        "Solo timestamps verificados": gas_cfig_binario.loc[gas_cfig_binario["timestamp_verified"]],
        "Sensibilidad: incluir fin anterior al inicio": base_sensibilidad,
        "Sensibilidad: incluir controles de flujo cero": gas_segmentado.loc[
            gas_segmentado["campaign"].eq("CFI-G") & gas_segmentado["ignited"].notna()
            & gas_segmentado["protocol_group"].isin(["sin_anotacion", "control_flujo_cero"])
        ],
    }
    filas_sensibilidad = []
    for nombre, g in escenarios.items():
        for geometria, sub in g.groupby("flame_type"):
            por_bloque = sub.groupby("operation_group")["ignited"].mean()
            filas_sensibilidad.append({
                "escenario": nombre, "flame_type": geometria, "n": len(sub),
                "operaciones": len(por_bloque), "positivos_pct_por_prueba": 100 * sub["ignited"].mean(),
                "positivos_pct_igual_peso_operacion": 100 * por_bloque.mean(),
            })
    sensibilidad = pd.DataFrame(filas_sensibilidad)
    display(sensibilidad.round(2))

    tablas_exportar = {
        "observaciones_auditadas": gas_auditado, "observaciones_unicas": gas_unicos,
        "familias": resumen_familias, "revision": gas_revision,
        "copias_retiradas": auditoria_gas.removed_copies,
        "conflictos_identidad": auditoria_gas.identity_conflicts,
        "conflictos_eventdata": auditoria_gas.event_conflicts,
        "sin_timestamp": gas_sin_timestamp, "bloques_operacion": por_operacion,
        "candidatos_replicas": candidatos_replicas, "grupos_condiciones": grupos_replicas,
        "perfil_familias": perfil_familias, "correlaciones_familia": correlaciones_familia,
        "pca_familias": resumen_pca, "pca_diagnostico": diagnostico_pca,
        "sensibilidad": sensibilidad, "fuentes": manifiesto_eda,
    }
    for nombre, tabla in tablas_exportar.items():
        tabla.to_csv(OUT_EDA / f"{nombre}.csv", index=False, encoding="utf-8-sig")
    reporte_eda = {
        "inputs": manifiesto_eda.to_dict(orient="records"),
        "audit": auditoria_gas.summary["n"].astype(int).to_dict(),
        "replica_candidate_rows": len(candidatos_replicas),
        "matching_settings_groups": len(grupos_replicas),
        "binary_cfig_rows": len(gas_cfig_binario),
        "flash_rows": len(gas_flash),
        "families_with_pca": len(resultados_pca_familia),
        "rules": {"min_pairs": MIN_PARES_EDA, "pca_min_coverage": 0.8,
                  "dates_imputed": False, "structural_missing_imputed": False,
                  "replicas_removed": False, "grouping": "operation_group"},
    }
    (OUT_EDA / "resumen.json").write_text(json.dumps(reporte_eda, indent=2, ensure_ascii=False), encoding="utf-8")

    display(Markdown(f"""
    ### Resultado de esta ejecución

    - **{len(gas_base_segmentacion)} filas originales; {len(gas_unicos)} identidades únicas.**
      Copias idénticas retiradas: **{len(auditoria_gas.removed_copies)}**.
    - **{len(gas_revision)} filas requieren revisión**; **{len(gas_sin_timestamp)}** no tienen
      timestamp de inicio verificable. No se inventan fechas ni se corrige EventData.
    - Se conservan **{len(candidatos_replicas)} pruebas** con condiciones coincidentes en
      **{len(grupos_replicas)} grupos candidatos a réplica**. Mismo día/condición no prueba duplicación.
      En **{int(grupos_replicas['n_resultados'].gt(1).sum()) if not grupos_replicas.empty else 0} grupos**
      hay resultados distintos con las mismas condiciones registradas: eliminarlos borraría
      información sobre variabilidad, condiciones omitidas o diferencias del protocolo.
    - La partición estricta deja **{len(resumen_familias)} familias sin anomalías** y
      **{gas_segmentado['operation_group'].nunique()} bloques de operación**. Familia no equivale a independencia.
      **{int(resumen_familias['n'].lt(MIN_PARES_EDA).sum())} familias** tienen menos de
      {MIN_PARES_EDA} pruebas y **{int(resumen_familias['operation_groups'].eq(1).sum())}**
      provienen de una sola operación. No deben tratarse como conjuntos suficientes para
      validación independiente, aunque su correlación sea fuerte.
    - La vista binaria inicial CFI-G contiene **{len(gas_cfig_binario)} pruebas** y mantiene
      fuera **{len(gas_flash)} flash**. Flame Design se conserva como contexto.
    - PCA pudo ejecutarse en **{len(resultados_pca_familia)} familias** con cobertura y variación
      suficientes. Sus componentes describen el diseño; no seleccionan causas de ignición.

    **Pendiente de revisión física:** significado de `flash`, equivalencia de `Ignite`,
    semántica de `HC burnrate`, interpretación de `po2_kpa` en inversas y tolerancias para
    considerar condiciones cercanas como réplicas. Antes de entrenar: validar agrupando
    por operación y revisar combustible/dilución/periodo como posibles confusores.

    Tablas auditables: `{OUT_EDA}`. Los conjuntos `segmentos_gas`, `gas_cfig_eda`,
    `gas_cfig_binario`, `gas_flash` y `gas_contexto_fd` quedan disponibles en memoria.
    """))
    ''')

    added[-1].source += "\n\n# <!-- FLAMESAFE:SEGMENTATION:END -->"
    nb.cells = replace_section(
        nb.cells, "SEGMENTATION", added, legacy_end_token="Tablas auditables:",
    )
    nbformat.validate(nb)
    nbformat.write(nb, PATH)
    print(f"Preserved {old} existing cells; appended {len(added)} cells: {PATH}")


if __name__ == "__main__":
    main()
