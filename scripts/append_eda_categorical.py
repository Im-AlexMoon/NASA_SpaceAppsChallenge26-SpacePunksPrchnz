"""Append a reproducible descriptive categorical/numeric EDA to the existing notebook."""

from __future__ import annotations

import textwrap
from pathlib import Path

import nbformat

from flamesafe.analysis.notebook_sections import replace_section

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "notebooks/02_eda/02_eda_legit.ipynb"


def main():
    nb = nbformat.read(PATH, as_version=4)
    cells = []

    def md(source):
        cells.append(nbformat.v4.new_markdown_cell(textwrap.dedent(source).strip()))

    def code(source):
        cells.append(nbformat.v4.new_code_cell(textwrap.dedent(source).strip()))

    md(r'''
    <!-- FLAMESAFE:CATEGORICAL:BEGIN -->
    ## Variables categóricas frente a numéricas: asociaciones condicionales

    **Protocolo descriptivo fijado antes de esta ejecución · 2026-11-15.** Esta sección
    conserva el EDA anterior y reutiliza su auditoría. El objetivo es describir diferencias,
    cobertura y posibles confusores; no calcular significancia, intervalos, riesgos de misión
    ni modelos predictivos. «Interacción» significa aquí asociación condicional explorada.

    ### Preguntas y roles de las variables

    | Papel | Variables | Pregunta y uso |
    |---|---|---|
    | Diseño | `fuel`, `dilution_group` | ¿Qué condiciones se exploraron bajo cada categoría, fijando los demás factores? |
    | Geometría | `flame_type` | Paneles separados: cambia la corriente del quemador y la interpretación de composición/caudal. |
    | Procedencia/protocolo | `campaign`, `period_group`, `protocol_group`, `outcome_source` | Cobertura, composición y faltantes; no efectos físicos de campaña. |
    | Ignición | `ignition_outcome`, `ignited` | ¿Cómo se distribuyen las condiciones entre `yes`, `no`, `flash` dentro de CFI-G? |
    | Resultados posteriores | `extinction_mode`, `burn_time_s`, `peak_burner_t_k` | Descripción secundaria, solo CFI-G con ignición positiva. |
    | Escasos/no definidos | `cool_flame`, `tfp` | Frecuencias, faltantes y registros; no comparar efectos de un flag no definido. |
    | Dependencia/identidad | `test_id`, `operation_group`, fecha | Conteo de operaciones y trazabilidad, no mediciones físicas. |

    Condiciones principales: `xo2`, `p_kpa`, `x_fuel` y `m_fuel_mg_s` en normales o
    `m_o2_mg_s` en inversas. `m_n2_mg_s` solo se explora en Flame Design. `po2_kpa`,
    `zst` y `tad_k` se presentan aparte como cantidades derivadas/calculadas; `po2_kpa`
    en inversas no se supone oxígeno de toda la cámara. El porcentaje de combustible
    de botella no se interpreta automáticamente como `x_fuel` de la mezcla experimental.

    ### Comparabilidad y cohortes

    - **Combustible:** bloquear campaña, geometría, dilución, periodo, protocolo y fuente
      de etiqueta. **Dilución:** fijar además combustible y retirar dilución del bloque.
      Comparar una categoría exige que pueda variar; no se usa `family_id` fijo para ello.
    - **Ignición:** comparar categorías dentro de la familia estricta CFI-G. No recodificar
      los ocho `flash`. Flame Design es contexto; sus etiquetas no se homologan con CFI-G.
    - **Extinción:** solo CFI-G, ignición positiva y modo informado. Un final por corte de
      flujo termina la observación; no representa el tiempo de extinción natural. Duraciones
      cortas o largas entre SE/FT no se interpretan como eficiencia causal de supresión.
    - Principal: filas únicas sin anomalías y sin protocolos especiales ni flujo cero.
      Las cuatro fechas ausentes no se rellenan; se repite el resumen sin ellas.
      Controles, rampas, `LOW O2` y la cronología anómala se documentan por separado.
    - No eliminar posibles réplicas, redondear condiciones, muestrear filas ni imputar datos.
      Los valores no finitos cuentan como ausentes; los ceros se conservan.

    ### Reglas de resumen y visualización

    Cada celda categoría × bloque × variable informa n total/válido/faltante, operaciones,
    mediana, cuartiles y rango. Se muestran puntos individuales; boxplots desde cinco valores
    y violines solo desde 20 valores y cinco valores distintos. Las curvas ECDF no suavizan
    fuera del soporte observado. Los rombos representan medianas por operación.

    Para pares con al menos cinco valores válidos por categoría se informa diferencia de
    medianas **A − B** y delta de Cliff **P(A>B) − P(A<B)**. Son efectos descriptivos de estas
    pruebas, sin umbrales de significancia ni de importancia causal. Las categorías pequeñas,
    constantes o ausentes se identifican; su falta de soporte no se esconde con una prueba.

    El solapamiento de rangos se evalúa para cada variable por separado. No demuestra
    comparabilidad multidimensional, control de confusión ni intercambiabilidad de categorías.
    La mediana por observación y la mediana de medianas por operación tienen ponderaciones
    diferentes. Una familia de una operación no permite concluir generalización entre jornadas.
    Se informa además cuántas operaciones comparten las categorías de cada contraste:
    varias operaciones por categoría no eliminan la confusión si pertenecen a jornadas disjuntas.

    Todas las tablas y las figuras pertinentes se guardan en `artifacts/eda_categoricas_numericas/`.
    El notebook muestra un máximo configurable de cuatro figuras por pregunta, por cobertura
    y diversidad de bloques, no por magnitud del efecto. El manifiesto conserva las demás.
    ''')

    code(r'''
    from pathlib import Path
    import hashlib
    import json
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from IPython.display import display, Markdown
    from flamesafe import config
    from flamesafe.analysis.categorical import (
        describe_categories, plot_comparison, PRIMARY_VARIABLES, ORDERS,
    )

    requeridos_cn = ["gas_auditado", "gas_unicos", "gas_segmentado"]
    if any(nombre not in globals() for nombre in requeridos_cn):
        raise RuntimeError("Ejecuta primero la sección de segmentación, o Restart & Run All.")
    assert not gas_unicos.duplicated(["psi_id", "test_id"]).any()
    OUT_CN = config.ROOT / "artifacts" / "eda_categoricas_numericas"
    FIG_CN = OUT_CN / "figures"
    FIG_CN.mkdir(parents=True, exist_ok=True)
    MAX_FIGURAS_EN_NOTEBOOK_CN = 4
    sns.set_theme(style="whitegrid", context="notebook")

    entradas_cn = [config.data_dir() / p for p in [
        "gold/gas_flame_tests.parquet", "gold/investigations.parquet",
        "silver/tables/psi159__eventdata.parquet", "silver/tables/psi10__eventdata.parquet",
    ]]
    fuentes_cn = pd.DataFrame([{
        "archivo": str(p.relative_to(config.data_dir())), "bytes": p.stat().st_size,
        "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
    } for p in entradas_cn])
    display(fuentes_cn)
    principal_cn = gas_segmentado.loc[gas_segmentado["protocol_group"].eq("sin_anotacion")].copy()
    cfig_cn = principal_cn.loc[principal_cn["campaign"].eq("CFI-G")].copy()
    fd_cn = principal_cn.loc[principal_cn["campaign"].eq("Flame Design")].copy()
    extincion_cn = cfig_cn.loc[
        cfig_cn["ignited"].fillna(False) & cfig_cn["extinction_mode"].notna()
    ].copy()
    cohortes_cn = pd.DataFrame([
        {"cohorte": nombre, "n_pruebas": len(g), "n_operaciones": g["operation_group"].nunique(),
         "n_familias": g["family_id"].nunique(), "sin_timestamp": int(g["t_start_gmt"].isna().sum())}
        for nombre, g in [("Principal sin protocolos especiales", principal_cn),
                          ("CFI-G con yes/no/flash", cfig_cn), ("Flame Design contexto", fd_cn),
                          ("CFI-G ignición positiva y modo de final informado", extincion_cn)]
    ])
    display(cohortes_cn)
    print("Las cohortes se superponen: sus tamaños no se suman.")
    ''')

    md(r'''
    ### Construcción de bloques y resultados descriptivos completos

    La tabla de bloques informa qué comparaciones son posibles. Una categoría única
    se describe, pero no genera una comparación artificial. `yes/no/flash` y SE/FT
    ausentes aparecen con n=0. Faltantes de categoría se conservan en las tablas y
    quedan fuera de efectos/figuras comparativas. No se condiciona la comparación
    de combustible a que el combustible sea constante.
    ''')
    code(r'''
    especificaciones_cn = {
        "combustible": {"data": principal_cn, "category": "fuel"},
        "dilucion": {"data": principal_cn, "category": "dilution_group"},
        "ignicion_cfig": {"data": cfig_cn, "category": "ignition_outcome", "expected_levels": ORDERS["ignition_outcome"]},
        "extincion_cfig": {"data": extincion_cn, "category": "extinction_mode",
                           "numeric_columns": ["burn_time_s", "peak_burner_t_k"],
                           "expected_levels": ORDERS["extinction_mode"]},
        "derivadas_cfig": {"data": cfig_cn, "category": "ignition_outcome",
                           "numeric_columns": ["po2_kpa", "zst", "tad_k"], "expected_levels": ORDERS["ignition_outcome"]},
        "contexto_fd": {"data": fd_cn, "category": "ignition_outcome",
                        "numeric_columns": ["xo2", "p_kpa", "x_fuel", "m_fuel_mg_s", "m_o2_mg_s", "m_n2_mg_s"],
                        "expected_levels": ORDERS["ignition_outcome"]},
    }
    resultados_cn = {
        nombre: describe_categories(name=nombre, **especificacion)
        for nombre, especificacion in especificaciones_cn.items()
    }
    resumen_cn = pd.concat([r.summary for r in resultados_cn.values()], ignore_index=True)
    efectos_cn = pd.concat([r.effects for r in resultados_cn.values() if not r.effects.empty], ignore_index=True)
    operaciones_cn = pd.concat([r.operation_medians for r in resultados_cn.values()], ignore_index=True)
    catalogo_cn = pd.concat([r.panel_catalog for r in resultados_cn.values()], ignore_index=True)
    display(catalogo_cn.groupby(["analysis", "status"]).agg(paneles=("panel_id", "size"), bloques=("block_id", "nunique")))
    columnas_resumen_cn = ["block_id", "variable", "category_level", "n_total", "n_valid", "n_missing",
                            "n_operations_valid", "median", "q25", "q75", "min", "max",
                            "median_of_operation_medians", "largest_operation_share", "status"]
    for nombre, r in resultados_cn.items():
        display(Markdown(f"**{nombre}: resumen completo exportado; primeras 20 filas.**"))
        display(r.summary[columnas_resumen_cn].head(20).round(4))
    display(Markdown("**Pares de categorías: diferencia A − B y delta de Cliff, sin inferencia.**"))
    columnas_efecto_cn = ["analysis", "block_id", "variable", "category_a", "category_b", "n_a", "n_b",
                           "operations_a", "operations_b", "n_shared_operations", "operations_disjoint",
                           "median_difference_a_minus_b", "cliffs_delta_a_minus_b",
                           "effect_status", "single_operation_category", "univariate_ranges_overlap"]
    display(efectos_cn[columnas_efecto_cn].head(40).round(4))
    ''')

    md(r'''
    ### Distribuciones, pares de categorías y cobertura por operación

    Para no fabricar una matriz indiscriminada de gráficos, se preseleccionan variables
    por pregunta. Todas las restantes quedan en las tablas: combustible (`xo2`, presión,
    fracción de combustible); dilución (fracción y caudal); ignición (`xo2`, presión);
    extinción (duración y temperatura); calculadas (`tad_k`); contexto FD (flujo de N₂).

    Se guardan todas las figuras de esa selección con dos categorías válidas y al menos
    cinco valores en total. Una categoría de menos de cinco valores sigue visible como
    puntos, sin boxplot ni efecto. Las figuras mostradas aquí priorizan un primer panel
    por bloque y geometría; el manifiesto permite abrir todas las demás.
    ''')
    code(r'''
    variables_figura_cn = {
        "combustible": ["xo2", "p_kpa", "x_fuel"],
        "dilucion": ["x_fuel", "m_fuel_mg_s", "m_o2_mg_s"],
        "ignicion_cfig": ["xo2", "p_kpa"],
        "extincion_cfig": ["burn_time_s", "peak_burner_t_k"],
        "derivadas_cfig": ["tad_k"],
        "contexto_fd": ["m_n2_mg_s"],
    }
    manifiesto_figuras_cn = []
    for nombre, resultado in resultados_cn.items():
        display(Markdown(f"#### {nombre}"))
        seleccion = resultado.panel_catalog.copy()
        seleccion["selected_variable"] = seleccion["variable"].isin(variables_figura_cn[nombre])
        seleccion["render"] = seleccion["selected_variable"] & seleccion["n_levels_valid"].ge(2) & seleccion["n_valid"].ge(5)
        candidatos = seleccion.loc[seleccion["render"]].copy()
        if candidatos.empty:
            print("Sin comparaciones con cobertura suficiente; consultar las tablas de categorías ausentes.")
        # Coverage-based order; never rank by effect size or significance.
        candidatos["variable_priority"] = candidatos["variable"].map({v: i for i, v in enumerate(variables_figura_cn[nombre])})
        candidatos = candidatos.sort_values(["variable_priority", "n_operations", "n_valid", "block_id"],
                                             ascending=[True, False, False, True])
        primeros = candidatos.groupby("flame_type", sort=True).head(1)
        resto = candidatos.loc[~candidatos["panel_id"].isin(primeros["panel_id"])]
        mostrar = set(pd.concat([primeros, resto]).head(MAX_FIGURAS_EN_NOTEBOOK_CN)["panel_id"])
        for _, panel in seleccion.iterrows():
            record = panel.to_dict()
            record["shown_in_notebook"] = panel["panel_id"] in mostrar
            record["png"] = ""
            record["svg"] = ""
            if panel["render"]:
                figura = plot_comparison(resultado, panel["panel_id"])
                stem = panel["panel_id"].replace(":", "__")
                png, svg = FIG_CN / f"{stem}.png", FIG_CN / f"{stem}.svg"
                figura.savefig(png, dpi=120, bbox_inches="tight")
                figura.savefig(svg, bbox_inches="tight")
                record["png"], record["svg"] = str(png.relative_to(OUT_CN)), str(svg.relative_to(OUT_CN))
                if record["shown_in_notebook"]:
                    display(figura)
                plt.close(figura)
            record["render_reason"] = (
                "saved" if panel["render"] else "variable_not_selected" if not panel["selected_variable"]
                else "single_or_missing_category" if panel["n_levels_valid"] < 2 else "fewer_than_5_total_values"
            )
            manifiesto_figuras_cn.append(record)
        print(f"Figuras guardadas: {len(candidatos)}; mostradas: {len(mostrar)}.")
    manifiesto_figuras_cn = pd.DataFrame(manifiesto_figuras_cn)
    ''')

    md(r'''
    ### Procedencia, protocolos y variables con interpretación limitada

    La composición de los grupos ayuda a reconocer confusión entre combustible, periodo
    y campaña. Estos paneles no estiman un efecto de campaña ni comparan normal/inversa
    como si las composiciones describieran el mismo lugar físico. Las frecuencias de
    `cool_flame` y `tfp` incluyen explícitamente las respuestas ausentes.
    ''')
    code(r'''
    factores_procedencia_cn = ["campaign", "flame_type", "period_group", "protocol_group", "outcome_source"]
    composicion_cn = (
        gas_unicos.groupby(factores_procedencia_cn + ["fuel", "dilution_group"], dropna=False)
        .agg(n_pruebas=("test_id", "size"), n_operaciones=("operation_group", "nunique"),
             sin_timestamp=("timestamp_verified", lambda s: int((~s).sum())),
             n_anomalias=("audit_ok", lambda s: int((~s).sum())))
        .reset_index()
    )
    variables_procedencia_cn = ["xo2", "p_kpa", "x_fuel", "m_fuel_mg_s", "m_o2_mg_s", "m_n2_mg_s"]
    cobertura_procedencia_cn = (
        gas_unicos.groupby(factores_procedencia_cn, dropna=False)[variables_procedencia_cn]
        .agg(lambda s: 100 * s.replace([np.inf, -np.inf], np.nan).isna().mean()).astype(float)
        .reset_index()
    )
    display(composicion_cn)
    fig, ax = plt.subplots(figsize=(11, max(4, len(cobertura_procedencia_cn) * 0.30)))
    matriz_procedencia_cn = cobertura_procedencia_cn.set_index(factores_procedencia_cn)
    sns.heatmap(matriz_procedencia_cn, annot=True, fmt=".0f", vmin=0, vmax=100, cmap="YlOrRd",
                cbar_kws={"label": "% ausentes"}, ax=ax)
    ax.set(title="Cobertura según procedencia y protocolo", ylabel="Campaña | geometría | periodo | protocolo | fuente")
    plt.xticks(rotation=35, ha="right")
    fig.savefig(FIG_CN / "procedencia_faltantes.png", dpi=120, bbox_inches="tight")
    fig.savefig(FIG_CN / "procedencia_faltantes.svg", bbox_inches="tight")
    plt.show()
    plt.close(fig)

    # All nitrogen-feed observations stay in their original source/protocol blocks.
    nitrogeno_cn = (
        gas_unicos.loc[gas_unicos["campaign"].eq("Flame Design")]
        .groupby(factores_procedencia_cn, dropna=False)
        .agg(n_total=("test_id", "size"), n_valid=("m_n2_mg_s", "count"),
             n_operaciones=("operation_group", "nunique"),
             mediana_mg_s=("m_n2_mg_s", "median"), minimo_mg_s=("m_n2_mg_s", "min"), maximo_mg_s=("m_n2_mg_s", "max"))
        .reset_index()
    )
    display(Markdown("**Nitrógeno suministrado: resumen exclusivo de Flame Design.**"))
    display(nitrogeno_cn)
    frecuencias_flags_cn = []
    for variable in ["cool_flame", "tfp"]:
        for (campana, tipo), g in gas_unicos.groupby(["campaign", "flame_type"]):
            niveles = g[variable].astype("string").fillna("sin_respuesta")
            for nivel, n in niveles.value_counts().items():
                sub = g.loc[niveles.eq(nivel)]
                frecuencias_flags_cn.append({"variable": variable, "campaign": campana, "flame_type": tipo,
                                             "category_level": nivel, "n": int(n),
                                             "n_operations": sub["operation_group"].nunique(),
                                             "pct_grupo": 100 * n / len(g)})
    frecuencias_flags_cn = pd.DataFrame(frecuencias_flags_cn)
    display(frecuencias_flags_cn.round(2))
    columnas_flags_cn = ["psi_id", "test_id", "family_code", "operation_group", "cool_flame", "tfp",
                          "ignition_outcome", "xo2", "p_kpa", "source_file", "source_row"]
    registros_flags_cn = gas_unicos.loc[gas_unicos["cool_flame"].notna() | gas_unicos["tfp"].notna(), columnas_flags_cn]
    display(Markdown("**Todas las respuestas informadas de cool_flame:**"))
    display(registros_flags_cn.loc[registros_flags_cn["cool_flame"].notna()])
    print("Los registros TFP completos se exportan; su acrónimo sigue pendiente de definición.")
    ''')

    md(r'''
    ### Dependencia y análisis de sensibilidad

    Los rombos y las tablas por operación conservan las réplicas. La diferencia entre
    mediana de pruebas y mediana de medianas señala sensibilidad a la ponderación; no
    es una prueba estadística. La fracción de filas de la operación dominante se reporta
    para cada categoría. Sin fecha verificable y con cronología anómala son problemas
    distintos y se evalúan por separado.

    Las sensibilidades no renombran protocolos para mezclarlos: los controles y rampas
    conservan sus bloques y se describen como cohortes aparte. Al excluir fechas no
    verificadas se mantienen también las categorías y bloques que desaparecen, mediante
    un enlace externo de resúmenes que deja explícita su ausencia.
    ''')
    code(r'''
    escenarios_cn = {
        "principal": principal_cn,
        "solo_timestamp_verificado": principal_cn.loc[principal_cn["timestamp_verified"]].copy(),
        "incluir_cronologia_anomala": gas_unicos.loc[
            gas_unicos["protocol_group"].eq("sin_anotacion")
            & ~gas_unicos["event_identity_conflict"] & ~gas_unicos["event_op_mismatch"]
            & ~gas_unicos["temporal_collision"]
        ].copy(),
    }
    sensibilidad_cn = []
    for escenario, fuente in escenarios_cn.items():
        for nombre in ["combustible", "dilucion", "ignicion_cfig"]:
            fuente_actual = fuente.loc[fuente["campaign"].eq("CFI-G")] if nombre == "ignicion_cfig" else fuente
            spec = {k: v for k, v in especificaciones_cn[nombre].items() if k != "data"}
            resultado = resultados_cn[nombre] if escenario == "principal" else describe_categories(
                fuente_actual, name=nombre, scenario=escenario, **spec
            )
            sensibilidad_cn.append(resultado.summary)
    sensibilidad_cn = pd.concat(sensibilidad_cn, ignore_index=True)
    llaves_sensibilidad_cn = ["analysis", "block_label", "category", "category_level", "variable"]
    referencia_cn = sensibilidad_cn.loc[sensibilidad_cn["scenario"].eq("principal"),
        llaves_sensibilidad_cn + ["n_total", "n_valid", "n_operations_valid", "median", "median_of_operation_medians"]]
    cambios_sensibilidad_cn = []
    for escenario in ["solo_timestamp_verificado", "incluir_cronologia_anomala"]:
        actual = sensibilidad_cn.loc[sensibilidad_cn["scenario"].eq(escenario),
            llaves_sensibilidad_cn + ["n_total", "n_valid", "n_operations_valid", "median", "median_of_operation_medians"]]
        cambio = referencia_cn.merge(actual, on=llaves_sensibilidad_cn, how="outer",
                                    suffixes=("_principal", "_sensibilidad"), validate="one_to_one", indicator=True)
        cambio["scenario"] = escenario
        cambio["median_change"] = cambio["median_sensibilidad"] - cambio["median_principal"]
        cambios_sensibilidad_cn.append(cambio)
    cambios_sensibilidad_cn = pd.concat(cambios_sensibilidad_cn, ignore_index=True)
    diferencias_ponderacion_cn = resumen_cn.copy()
    diferencias_ponderacion_cn["median_difference_weighting"] = (
        diferencias_ponderacion_cn["median"] - diferencias_ponderacion_cn["median_of_operation_medians"]
    )
    display(diferencias_ponderacion_cn.loc[
        diferencias_ponderacion_cn["n_operations_valid"].le(1) | diferencias_ponderacion_cn["largest_operation_share"].gt(0.5),
        ["analysis", "block_id", "variable", "category_level", "n_valid", "n_operations_valid", "largest_operation_share"]
    ].head(30).round(3))
    mostrar_cambios_cn = cambios_sensibilidad_cn.loc[
        cambios_sensibilidad_cn["_merge"].ne("both")
        | cambios_sensibilidad_cn["n_valid_principal"].ne(cambios_sensibilidad_cn["n_valid_sensibilidad"])
    ]
    display(mostrar_cambios_cn[["analysis", "scenario", "category_level", "variable", "n_valid_principal",
                               "n_valid_sensibilidad", "median_principal", "median_sensibilidad", "_merge"]].head(40))
    protocolos_revision_cn = gas_unicos.loc[
        ~gas_unicos["protocol_group"].eq("sin_anotacion") | ~gas_unicos["audit_ok"]
    ].copy()
    resumen_protocolos_revision_cn = (
        protocolos_revision_cn.groupby(["campaign", "flame_type", "protocol_group", "audit_ok"], dropna=False)
        .agg(n=("test_id", "size"), operaciones=("operation_group", "nunique"),
             xo2_validos=("xo2", "count"), presion_validos=("p_kpa", "count"),
             x_fuel_validos=("x_fuel", "count"),
             etiquetas_conocidas=("ignition_outcome", "count"))
        .reset_index()
    )
    display(resumen_protocolos_revision_cn)
    ''')

    md(r'''
    ### Hallazgos descriptivos y límites antes del modelado

    Las conclusiones siguientes se calculan con la ejecución actual. No se ordenan
    variables por «significancia» ni se presentan diferencias de condiciones como efectos
    de cambiar el combustible. Se conservan las tablas completas para revisar cada bloque.
    ''')
    code(r'''
    tablas_cn = {
        "fuentes": fuentes_cn, "cohortes": cohortes_cn, "resumen_categorias": resumen_cn,
        "efectos_descriptivos": efectos_cn, "medianas_operacion": operaciones_cn,
        "catalogo_comparaciones": catalogo_cn, "manifiesto_figuras": manifiesto_figuras_cn,
        "composicion_procedencia": composicion_cn, "cobertura_procedencia": cobertura_procedencia_cn,
        "nitrogeno_fd": nitrogeno_cn, "frecuencias_flags": frecuencias_flags_cn,
        "registros_flags": registros_flags_cn, "sensibilidad_resumen": sensibilidad_cn,
        "sensibilidad_cambios": cambios_sensibilidad_cn, "ponderacion_operaciones": diferencias_ponderacion_cn,
        "protocolos_revision": protocolos_revision_cn, "protocolos_revision_resumen": resumen_protocolos_revision_cn,
    }
    for nombre, tabla in tablas_cn.items():
        tabla.to_csv(OUT_CN / f"{nombre}.csv", index=False, encoding="utf-8-sig")
    # Export point-level provenance for every panel, retaining trial identity.
    puntos_cn = pd.concat([
        puntos.assign(panel_id=panel_id, analysis=nombre)
        for nombre, resultado in resultados_cn.items() for panel_id, puntos in resultado.panels.items()
    ], ignore_index=True)
    puntos_cn.to_csv(OUT_CN / "observaciones_por_panel.csv", index=False, encoding="utf-8-sig")
    assert not puntos_cn.duplicated(["panel_id", "psi_id", "test_id"]).any(), "Filas multiplicadas dentro de un panel"
    for p, esperado in zip(entradas_cn, fuentes_cn["sha256"], strict=True):
        assert hashlib.sha256(p.read_bytes()).hexdigest() == esperado, "Cambió una fuente durante el análisis"
    efectos_validos_cn = efectos_cn.loc[efectos_cn["effect_status"].eq("descriptive_only")]
    flags_poca_info_cn = resumen_cn.loc[resumen_cn["n_operations_valid"].le(1) & resumen_cn["n_valid"].gt(0)]
    n_flash_cn = int(cfig_cn["ignition_outcome"].eq("flash").sum())
    combustibles_flash_cn = ", ".join(sorted(cfig_cn.loc[cfig_cn["ignition_outcome"].eq("flash"), "fuel"].unique()))
    reporte_cn = {
        "protocol": "descriptive_only", "inputs": fuentes_cn.to_dict(orient="records"),
        "n_source_trials": len(gas_unicos), "n_principal_trials": len(principal_cn),
        "n_summary_rows": len(resumen_cn), "n_pairwise_rows": len(efectos_cn),
        "n_descriptive_effects": len(efectos_validos_cn),
        "n_saved_comparison_figures": int(manifiesto_figuras_cn["render"].sum()),
        "n_shown_comparison_figures": int(manifiesto_figuras_cn["shown_in_notebook"].sum()),
        "pvalues_computed": False, "confidence_intervals_computed": False, "models_fitted": False,
        "imputation": False, "replicas_removed": False,
        "effect_orientation": "A minus B; Cliff delta = P(A>B)-P(A<B)",
        "thresholds": {"min_effect_per_category": 5, "min_boxplot": 5,
                       "min_violin": 20, "min_violin_unique": 5},
    }
    (OUT_CN / "resumen.json").write_text(json.dumps(reporte_cn, ensure_ascii=False, indent=2), encoding="utf-8")
    display(Markdown(f"""
    **Resultado de esta ejecución**

    - La cohorte principal reúne **{len(principal_cn)} pruebas**, separadas en bloques;
      no representa una muestra aleatoria de atmósferas de misión.
    - Se exportaron **{len(resumen_cn)} resúmenes categoría–variable–bloque** y
      **{len(efectos_validos_cn)} efectos descriptivos con al menos cinco valores por categoría**.
      Los pares restantes conservan el motivo por el que no se calcula el efecto.
    - **{len(flags_poca_info_cn)} celdas observadas de resumen** dependen de una sola operación.
      Una diferencia grande en esas celdas no demuestra reproducibilidad entre jornadas.
    - Los **{n_flash_cn} flash** observados en esta cohorte corresponden a **{combustibles_flash_cn}**.
      Su distribución de condiciones no permite atribuir el fenómeno exclusivamente al combustible.
    - Combustible, dilución, presión y composición pertenecen a un diseño experimental conjunto.
      Las diferencias observadas y el solapamiento de rangos no resuelven la confusión causal.
      En **{int(efectos_cn['operations_disjoint'].sum())} contrastes variable–par de categorías**
      no hay operaciones compartidas: no puede separarse el efecto de categoría del de jornada
      a partir de esa comparación descriptiva por sí sola.
    - `m_n2_mg_s` permanece como alimentación de Flame Design; `cool_flame` tiene cobertura
      muy limitada y `tfp` conserva una semántica pendiente. No se rellenan sus ausencias.
    - Los tiempos de final por corte de flujo no se interpretan como tiempos de extinción natural.
      No se calculan p-valores, intervalos ni modelos en esta sección.

    **Antes de modelar:** decidir la etiqueta `flash`, revisar equivalencia de resultados entre
    campañas, resolver la cronología anómala y comprobar soporte común y operaciones disponibles
    para cada pregunta. Una etapa posterior requerirá validación agrupada y definición del objetivo.

    Resultados y figuras: `{OUT_CN}`. Objetos principales: `resultados_cn`, `resumen_cn`,
    `efectos_cn`, `operaciones_cn`, `cambios_sensibilidad_cn` y `manifiesto_figuras_cn`.
    """))

    # A pre-specified scientific question from the project: flash versus yes/no in ethane.
    foco_flash_cn = resumen_cn.loc[
        resumen_cn["analysis"].eq("ignicion_cfig") & resumen_cn["flame_type"].eq("inverse")
        & resumen_cn["fuel"].eq("ethane") & resumen_cn["period_group"].eq("2021")
        & resumen_cn["variable"].eq("xo2"),
        ["block_id", "category_level", "n_valid", "n_operations_valid", "median", "q25", "q75", "min", "max"],
    ]
    display(Markdown("**Foco predefinido: oxígeno en CFI-G inversa con etano, por resultado.**"))
    display(foco_flash_cn.round(4))
    display(Markdown(
        "Estas distribuciones son condicionales a la familia y al diseño observado. "
        "La categoría `no` contiene pocas observaciones; una diferencia de medianas no establece "
        "un umbral de ignición, y flash sigue sin etiqueta binaria."
    ))
    # <!-- FLAMESAFE:CATEGORICAL:END -->
    ''')

    nb.cells = replace_section(nb.cells, "CATEGORICAL", cells)
    nbformat.validate(nb)
    nbformat.write(nb, PATH)
    print(f"Categorical appendix: {len(cells)} cells; notebook total: {len(nb.cells)}")


if __name__ == "__main__":
    main()
