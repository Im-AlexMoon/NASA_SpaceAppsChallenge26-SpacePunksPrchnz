"""
Modelo de supervivencia de Cox para la persistencia de la llama (CFI-G, PSI-159).

Evento      : autoextinción de la llama (extinction_mode == "self_extinguished")
Censura     : corte del flujo (flow_terminated); la llama seguía encendida a T
Tiempo      : burn_time_s (> 0). Condicional a que hubo ignición.
Clasificación derivada: "la llama persiste más allá de t*" = S(t* | x) >= umbral.

Dependencias: lifelines, scikit-survival, statsmodels, scikit-learn, pandas, numpy, matplotlib
    pip install lifelines scikit-survival statsmodels

Supuestos que el código NO puede verificar por sí solo (revisar con los diagnósticos):
  1. Censura no informativa dado x (ver chequeo_censura y sensibilidad_censura).
  2. Riesgos proporcionales (ver chequeo_supuestos).
  3. Independencia entre pruebas; si hay dependencia dentro de `cluster` (p. ej. test_day),
     comparar errores estándar del modelo contra los robustos (comparar_errores_estandar).
  4. Las métricas IPCW usan la distribución de censura marginal (Kaplan-Meier de la censura);
     por eso los horizontes deben quedar ANTES del corte de protocolo (~66 s).
"""
from __future__ import annotations

import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter, KaplanMeierFitter
from lifelines.statistics import proportional_hazard_test
from lifelines.utils import concordance_index
from sklearn.model_selection import GroupKFold, StratifiedKFold
from sksurv.metrics import (
    brier_score,
    concordance_index_ipcw,
    cumulative_dynamic_auc,
    integrated_brier_score,
)
from sksurv.util import Surv
from statsmodels.nonparametric.smoothers_lowess import lowess
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.outliers_influence import variance_inflation_factor

# Malla de evaluación (s) y horizontes de clasificación (subconjunto de la malla).
GRID = np.arange(5.0, 61.0, 5.0)
HORIZONTES = (10.0, 30.0, 60.0)


# --------------------------------------------------------------------------------------
# 1. Datos
# --------------------------------------------------------------------------------------
def preparar_datos(gas, fuente="PSI-159", cluster_col="test_day", ref_fuel="butane", cov_extra=()):
    """Construye la muestra analítica. Devuelve (df, flujo_de_exclusiones).

    Escalas pensadas para interpretar los HR:
      xo2_5pp : xo2 en unidades de 5 puntos porcentuales de O2
      p_10kpa : presión en unidades de 10 kPa
    """
    flujo = {"filas_totales": len(gas)}
    d = gas[gas["source_file"].str.contains(fuente, na=False)]
    flujo[f"en_{fuente}"] = len(d)
    d = d[d["extinction_mode"].notna()]
    flujo["con_extinction_mode"] = len(d)
    d = d[d["burn_time_s"] > 0]
    flujo["con_tiempo_positivo"] = len(d)
    d = d.dropna(subset=["fuel", "flame_type", "xo2", "p_kpa", *cov_extra])
    flujo["casos_completos"] = len(d)

    out = pd.DataFrame(index=d.index)
    out["T"] = d["burn_time_s"].astype(float)
    out["E"] = (d["extinction_mode"] == "self_extinguished").astype(int)
    out["xo2_5pp"] = d["xo2"].astype(float) / 0.05
    out["p_10kpa"] = d["p_kpa"].astype(float) / 10.0
    out["normal"] = (d["flame_type"] == "normal").astype(int)
    niveles = sorted(d["fuel"].unique())
    if ref_fuel not in niveles:
        ref_fuel = niveles[0]
    for f in niveles:
        if f != ref_fuel:
            out[f"fuel_{f}"] = (d["fuel"] == f).astype(int)
    out["xo2_x_normal"] = out["xo2_5pp"] * out["normal"]
    for c in cov_extra:
        out[c] = d[c].astype(float)
    out["cluster"] = d[cluster_col].values if cluster_col else np.arange(len(d))
    out["fuel"] = d["fuel"].values
    out["flame_type"] = d["flame_type"].values
    flujo["combustible_referencia"] = ref_fuel
    return out.reset_index(drop=True), flujo


def construir_modelos(df):
    """Modelos preespecificados (no se seleccionan variables por p-valor)."""
    fuels = [c for c in df.columns if c.startswith("fuel_")]
    base = [*fuels, "normal"]
    return {
        "M1_diseno": base,
        "M2_atmosfera": [*base, "xo2_5pp", "p_10kpa"],
        "M3_interaccion": [*base, "xo2_5pp", "p_10kpa", "xo2_x_normal"],
    }



def diagnostico_previo(df, covs):
    """Tamaño efectivo, empates, censura y colinealidad antes de ajustar."""

    if df.empty:
        raise ValueError("El DataFrame no contiene observaciones.")

    if isinstance(covs, str):
        covs = [covs]

    # Verificar que las covariables existan
    faltantes = [c for c in covs if c not in df.columns]
    if faltantes:
        raise ValueError(f"Covariables inexistentes en df: {faltantes}")

    n, ev = len(df), int(df["E"].sum())

    res = {
        "n": n,
        "eventos": ev,
        "censuras": n - ev,
        "pct_censura": round(100 * (n - ev) / n, 1),
        "parametros": len(covs),
        "eventos_por_parametro": round(ev / max(len(covs), 1), 1),
        "pct_tiempos_empatados": round(
            100 * (1 - df["T"].nunique() / n), 1
        ),
    }

    cens = df.loc[df["E"] == 0, "T"]

    if len(cens):
        moda = cens.mode().iloc[0]
        res["censura_moda_s"] = float(moda)
        res["pct_censura_en_moda"] = round(
            100 * float((cens == moda).mean()), 1
        )

    if res["eventos_por_parametro"] < 10:
        warnings.warn(
            "Menos de 10 eventos por parámetro: estimaciones inestables."
        )

    X = df[covs].astype(float).assign(const=1.0)

    vif = pd.Series({
        c: variance_inflation_factor(X.values, i)
        for i, c in enumerate(X.columns)
        if c != "const"
    }).round(2)

    cobertura = pd.crosstab(
        df["fuel"],
        [df["flame_type"], df["E"]],
        rownames=["fuel"],
        colnames=["flame_type", "evento"]
    )

    return pd.Series(res), vif, cobertura


def soporte_horizontes(df, horizontes=HORIZONTES):
    """Sujetos en riesgo y eventos acumulados en cada horizonte (para elegirlos con criterio)."""
    filas = []
    for h in horizontes:
        filas.append({
            "t*": h,
            "en_riesgo": int((df["T"] >= h).sum()),
            "eventos_hasta_t*": int(((df["T"] <= h) & (df["E"] == 1)).sum()),
            "censuras_hasta_t*": int(((df["T"] <= h) & (df["E"] == 0)).sum()),
        })
    return pd.DataFrame(filas).set_index("t*")


# --------------------------------------------------------------------------------------
# 2. Ajuste e intervalos de confianza de los estimadores
# --------------------------------------------------------------------------------------
def ajustar_cox(df, covs, penalizer=0.0, robusto=False):
    """Cox con empates por Efron. robusto=True usa varianza sandwich agrupada por `cluster`."""
    cols = ["T", "E", *covs] + (["cluster"] if robusto else [])
    cph = CoxPHFitter(penalizer=penalizer)
    cph.fit(df[cols], duration_col="T", event_col="E",
            cluster_col="cluster" if robusto else None, robust=robusto)
    return cph


def tabla_estimadores(cph):
    """Coeficientes y razones de riesgo (HR) con IC 95 % de Wald y p ajustado por Holm."""
    s = cph.summary
    t = pd.DataFrame({
        "coef": s["coef"], "coef_IC_inf": s["coef lower 95%"], "coef_IC_sup": s["coef upper 95%"],
        "HR": s["exp(coef)"], "HR_IC_inf": s["exp(coef) lower 95%"], "HR_IC_sup": s["exp(coef) upper 95%"],
        "ee": s["se(coef)"], "p": s["p"],
    })
    if len(t) > 1:
        t["p_holm"] = multipletests(t["p"], method="holm")[1]
    return t


def resumen_global(cph):
    """Prueba de razón de verosimilitud global y criterios de información."""
    lr = cph.log_likelihood_ratio_test()
    return pd.Series({
        "LR_chi2": lr.test_statistic, "gl": lr.degrees_freedom, "p_LR": lr.p_value,
        "logLik_parcial": cph.log_likelihood_, "AIC_parcial": cph.AIC_partial_,
        "C_aparente": cph.concordance_index_,
    })


def comparar_errores_estandar(df, covs, penalizer=0.0):
    """Cociente ee_robusto / ee_modelo. Valores >> 1 sugieren dependencia dentro de cluster."""
    m = ajustar_cox(df, covs, penalizer)
    r = ajustar_cox(df, covs, penalizer, robusto=True)
    out = pd.DataFrame({
        "ee_modelo": m.standard_errors_, "ee_robusto": r.standard_errors_,
        "HR_IC_inf_rob": r.summary["exp(coef) lower 95%"], "HR_IC_sup_rob": r.summary["exp(coef) upper 95%"],
    })
    out["cociente"] = out["ee_robusto"] / out["ee_modelo"]
    return out


def bootstrap_parametros(df, covs, B=500, seed=0, penalizer=0.0, por_grupo=False):
    """IC percentil 95 % de los HR por bootstrap (sujetos o clusters completos)."""
    rng = np.random.default_rng(seed)
    grupos = df["cluster"].unique()
    filas = []
    for _ in range(B):
        if por_grupo:
            sel = rng.choice(grupos, size=len(grupos), replace=True)
            boot = pd.concat([df[df["cluster"] == g] for g in sel], ignore_index=True)
        else:
            boot = df.iloc[rng.integers(0, len(df), len(df))].reset_index(drop=True)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                filas.append(ajustar_cox(boot, covs, penalizer).params_)
        except Exception:
            continue
    res = pd.DataFrame(filas)
    out = pd.DataFrame({
        "HR_boot_inf": np.exp(res.quantile(0.025)),
        "HR_boot_sup": np.exp(res.quantile(0.975)),
    })
    out.attrs["replicas_validas"] = len(res)
    out.attrs["replicas_fallidas"] = B - len(res)
    return out


# --------------------------------------------------------------------------------------
# 3. Supuestos del modelo
# --------------------------------------------------------------------------------------
def chequeo_supuestos(cph, df, covs, graficar=True):
    """Riesgos proporcionales (Schoenfeld, Holm), forma funcional (martingala) e influencia (dfbetas)."""
    train = df[["T", "E", *covs]]
    ph = proportional_hazard_test(cph, train, time_transform="rank").summary
    ph["p_holm"] = multipletests(ph["p"], method="holm")[1]

    mart = cph.compute_residuals(train, "martingale")["martingale"]
    dfb = cph.compute_residuals(train, "delta_beta")
    dfbetas = dfb.abs() / cph.standard_errors_
    umbral = 2 / np.sqrt(len(df))
    influyentes = (dfbetas > umbral).sum()
    top = dfbetas.max(axis=1).sort_values(ascending=False).head(10)

    figs = {}
    if graficar:
        cont = [c for c in ("xo2_5pp", "p_10kpa") if c in covs]
        if cont:
            fig, ax = plt.subplots(1, len(cont), figsize=(5 * len(cont), 3.8), squeeze=False)
            for a, c in zip(ax[0], cont):
                a.scatter(df[c], mart, s=10, alpha=0.5)
                lw = lowess(mart, df[c], frac=0.6)
                a.plot(lw[:, 0], lw[:, 1], color="C3")
                a.axhline(0, color="gray", lw=0.8)
                a.set_xlabel(c); a.set_ylabel("residuo martingala")
            fig.suptitle("Forma funcional: una tendencia curva sugiere términos no lineales")
            fig.tight_layout()
            figs["martingala"] = fig
        sch = cph.compute_residuals(train, "scaled_schoenfeld")
        t_ev = df.loc[sch.index, "T"]
        fig2, ax2 = plt.subplots(1, len(covs), figsize=(3.2 * len(covs), 3.2), squeeze=False)
        for a, c in zip(ax2[0], covs):
            a.scatter(np.log(t_ev), sch[c], s=8, alpha=0.5)
            lw = lowess(sch[c], np.log(t_ev), frac=0.7)
            a.plot(lw[:, 0], lw[:, 1], color="C3")
            a.axhline(float(cph.params_[c]), color="gray", ls="--", lw=0.8)
            a.set_title(c, fontsize=9); a.set_xlabel("log(t)")
        fig2.suptitle("Schoenfeld escalado: pendiente nula = riesgos proporcionales")
        fig2.tight_layout()
        figs["schoenfeld"] = fig2
    return {"prueba_PH": ph, "n_influyentes_por_coef": influyentes, "umbral_dfbetas": umbral,
            "top_influyentes": top, "figuras": figs}


def chequeo_censura(df, covs):
    """Cox para el tiempo de CENSURA. Si las covariables lo predicen, la censura depende de x
    (aceptable si T y censura son independientes dado x); no sustituye el juicio sobre el protocolo."""
    d = df[["T", "E", *covs]].copy()
    d["Ec"] = 1 - d["E"]
    m = CoxPHFitter().fit(d.drop(columns="E"), duration_col="T", event_col="Ec")
    lr = m.log_likelihood_ratio_test()
    return tabla_estimadores(m), pd.Series({"LR_chi2": lr.test_statistic, "gl": lr.degrees_freedom, "p": lr.p_value})


def sensibilidad_censura(df, covs, penalizer=0.0):
    """HR bajo tres tratamientos de flow_terminated: censura (principal), evento y exclusión."""
    esc = {}
    esc["principal: censurado"] = df
    d_ev = df.copy(); d_ev["E"] = 1
    esc["extremo: tratado como evento"] = d_ev
    esc["excluir flow_terminated"] = df[df["E"] == 1]
    filas = []
    for nombre, d in esc.items():
        m = ajustar_cox(d, covs, penalizer)
        t = tabla_estimadores(m)[["HR", "HR_IC_inf", "HR_IC_sup"]].copy()
        t.insert(0, "escenario", nombre)
        t.insert(1, "n", len(d))
        filas.append(t.reset_index().rename(columns={"index": "covariable", "covariate": "covariable"}))
    return pd.concat(filas, ignore_index=True)


def grafico_km(df, por="fuel", t_max=None):
    """Kaplan-Meier descriptivo por grupo (con bandas de confianza)."""
    fig, ax = plt.subplots(figsize=(6, 4))
    for g, sub in df.groupby(por):
        KaplanMeierFitter(label=f"{g} (n={len(sub)})").fit(sub["T"], sub["E"]).plot_survival_function(ax=ax)
    if t_max:
        ax.set_xlim(0, t_max)
    ax.set_xlabel("tiempo (s)"); ax.set_ylabel("P(llama no se ha autoextinguido)")
    fig.tight_layout()
    return fig


# --------------------------------------------------------------------------------------
# 4. Validación cruzada y métricas
# --------------------------------------------------------------------------------------
def validacion_cruzada(df, covs, grid=GRID, k=5, penalizer=0.0, por_grupo=True, seed=0):
    """Predicciones fuera de muestra. Con por_grupo=True ningún cluster aparece en train y test."""
    X = df.reset_index(drop=True)
    grid = np.asarray(grid, dtype=float)
    if por_grupo:
        splitter = GroupKFold(n_splits=min(k, X["cluster"].nunique())).split(X, groups=X["cluster"])
    else:
        splitter = StratifiedKFold(k, shuffle=True, random_state=seed).split(X, X["E"])
    lp = np.full(len(X), np.nan)
    S = np.full((len(X), len(grid)), np.nan)
    S0 = np.full((len(X), len(grid)), np.nan)
    for tr, te in splitter:
        m = ajustar_cox(X.iloc[tr], covs, penalizer)
        # predictor lineal sin centrar: comparable entre folds
        lp[te] = X.iloc[te][covs].values @ m.params_[covs].values
        S[te] = m.predict_survival_function(X.iloc[te][covs], times=list(grid)).T.values
        km = KaplanMeierFitter().fit(X.iloc[tr]["T"], X.iloc[tr]["E"])
        S0[te] = km.predict(list(grid)).values
    oof = pd.DataFrame({"T": X["T"], "E": X["E"], "cluster": X["cluster"], "lp": lp})
    for j, t in enumerate(grid):
        oof[f"S_{t:g}"] = S[:, j]
        oof[f"S0_{t:g}"] = S0[:, j]
    return oof


def _y(oof):
    return Surv.from_arrays(event=oof["E"].astype(bool).values, time=oof["T"].values)


def metricas_oof(oof, grid=GRID, horizontes=HORIZONTES):
    """Discriminación (C de Harrell y de Uno, AUC(t)), error de predicción (Brier(t), IBS, IPA(t))."""
    grid = np.asarray(grid, dtype=float)
    hz = np.asarray(horizontes, dtype=float)
    y = _y(oof)
    lp = oof["lp"].values
    out = {"C_Harrell": concordance_index(oof["T"], -lp, oof["E"])}
    out["C_Uno"] = concordance_index_ipcw(y, y, lp, tau=float(hz.max()))[0]
    auc, auc_medio = cumulative_dynamic_auc(y, y, lp, hz)
    for h, a in zip(hz, auc):
        out[f"AUC_{h:g}"] = a
    out["AUC_medio"] = auc_medio
    est = oof[[f"S_{t:g}" for t in grid]].values
    est0 = oof[[f"S0_{t:g}" for t in grid]].values
    _, bs = brier_score(y, y, est, grid)
    _, bs0 = brier_score(y, y, est0, grid)
    for h in hz:
        j = int(np.argmin(np.abs(grid - h)))
        out[f"Brier_{h:g}"] = bs[j]
        out[f"IPA_{h:g}"] = 1 - bs[j] / bs0[j]
    out["IBS"] = integrated_brier_score(y, y, est, grid)
    out["IBS_nulo"] = integrated_brier_score(y, y, est0, grid)
    out["IPA_IBS"] = 1 - out["IBS"] / out["IBS_nulo"]
    return pd.Series(out)


def _remuestra(oof, rng, por_grupo):
    if por_grupo:
        gs = oof["cluster"].unique()
        sel = rng.choice(gs, size=len(gs), replace=True)
        return pd.concat([oof[oof["cluster"] == g] for g in sel], ignore_index=True)
    return oof.iloc[rng.integers(0, len(oof), len(oof))].reset_index(drop=True)


def ic_metricas(oof, grid=GRID, horizontes=HORIZONTES, B=500, seed=0, por_grupo=False):
    """Estimador puntual e IC percentil 95 % por bootstrap sobre las predicciones fuera de muestra.
    El IC refleja la variabilidad de la muestra de evaluación (no re-ajusta el modelo)."""
    rng = np.random.default_rng(seed)
    base = metricas_oof(oof, grid, horizontes)
    reps = []
    for _ in range(B):
        sub = _remuestra(oof, rng, por_grupo)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                reps.append(metricas_oof(sub, grid, horizontes))
        except Exception:
            continue
    R = pd.DataFrame(reps)
    out = pd.DataFrame({"estimador": base, "IC_inf": R.quantile(0.025), "IC_sup": R.quantile(0.975)})
    out.attrs["replicas_validas"] = len(R)
    return out


def calibracion(oof, t_star, bins=5):
    """Supervivencia predicha vs Kaplan-Meier observada por grupos de riesgo (IC Greenwood)."""
    col = f"S_{t_star:g}"
    q = pd.qcut(oof[col], q=bins, duplicates="drop")
    filas = []
    for g, sub in oof.groupby(q, observed=True):
        km = KaplanMeierFitter().fit(sub["T"], sub["E"])
        ci = km.confidence_interval_survival_function_
        lo, hi = ci.loc[:t_star].iloc[-1].values
        filas.append({"grupo": str(g), "n": len(sub), "eventos": int(sub["E"].sum()),
                      "S_predicha": sub[col].mean(), "S_observada_KM": float(km.predict(t_star)),
                      "IC_inf": lo, "IC_sup": hi})
    return pd.DataFrame(filas)


def grafico_calibracion(tabla, t_star):
    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    ax.plot([0, 1], [0, 1], "--", color="gray")
    err = [tabla["S_observada_KM"] - tabla["IC_inf"], tabla["IC_sup"] - tabla["S_observada_KM"]]
    ax.errorbar(tabla["S_predicha"], tabla["S_observada_KM"], yerr=err, fmt="o", capsize=3)
    ax.set_xlabel(f"S({t_star:g} s) predicha"); ax.set_ylabel(f"S({t_star:g} s) observada (KM, IC 95 %)")
    ax.set_title("Calibración fuera de muestra")
    fig.tight_layout()
    return fig


def clasificacion_ipcw(oof, t_star, umbral=0.5):
    """Clasificación binaria 'la llama persiste más allá de t*' (clase positiva) con ponderación IPCW.

    Los censurados antes de t* tienen estado desconocido y se excluyen (peso 0);
    el resto se re-pondera por 1/G(.), con G la supervivencia de la censura (Kaplan-Meier).
    Predicción positiva: S(t*|x) >= umbral.
    """
    col = f"S_{t_star:g}"
    T, E = oof["T"].values, oof["E"].values
    kmc = KaplanMeierFitter().fit(T, 1 - E)

    def G(t):
        return np.clip(kmc.predict(np.atleast_1d(np.maximum(t - 1e-9, 0))).values, 0.05, 1.0)

    persiste = T > t_star
    extinto = (E == 1) & (T <= t_star)
    w = np.zeros(len(T))
    w[extinto] = 1 / G(T[extinto])
    w[persiste] = 1 / G(np.full(persiste.sum(), t_star))
    y = persiste.astype(int)
    yhat = (oof[col].values >= umbral).astype(int)
    tp = w[(y == 1) & (yhat == 1)].sum(); fn = w[(y == 1) & (yhat == 0)].sum()
    tn = w[(y == 0) & (yhat == 0)].sum(); fp = w[(y == 0) & (yhat == 1)].sum()
    sens = tp / (tp + fn) if tp + fn else np.nan
    espec = tn / (tn + fp) if tn + fp else np.nan
    return pd.Series({
        "sensibilidad": sens, "especificidad": espec,
        "VPP": tp / (tp + fp) if tp + fp else np.nan,
        "VPN": tn / (tn + fn) if tn + fn else np.nan,
        "exactitud_balanceada": np.nanmean([sens, espec]),
        "prevalencia_persiste": (tp + fn) / w.sum(),
        "umbral": umbral,
    })


def ic_clasificacion(oof, t_star, umbrales=(0.3, 0.5, 0.7), B=500, seed=0, por_grupo=False):
    """Métricas de clasificación IPCW para varios umbrales, con IC percentil 95 % (bootstrap)."""
    rng = np.random.default_rng(seed)
    filas = []
    for u in umbrales:
        base = clasificacion_ipcw(oof, t_star, u)
        reps = []
        for _ in range(B):
            try:
                reps.append(clasificacion_ipcw(_remuestra(oof, rng, por_grupo), t_star, u))
            except Exception:
                continue
        R = pd.DataFrame(reps)
        for m in ["sensibilidad", "especificidad", "VPP", "VPN", "exactitud_balanceada"]:
            filas.append({"umbral": u, "metrica": m, "estimador": base[m],
                          "IC_inf": R[m].quantile(0.025), "IC_sup": R[m].quantile(0.975)})
    return pd.DataFrame(filas).pivot(index="umbral", columns="metrica", values=["estimador", "IC_inf", "IC_sup"])


# --------------------------------------------------------------------------------------
# 5. Comparación de modelos preespecificados
# --------------------------------------------------------------------------------------
def comparar_modelos(df, modelos, grid=GRID, horizontes=HORIZONTES, B=300, penalizer=0.0, seed=0):
    """AIC y métricas fuera de muestra (con IC 95 %) para cada modelo."""
    filas = []
    for nombre, covs in modelos.items():
        cph = ajustar_cox(df, covs, penalizer)
        oof = validacion_cruzada(df, covs, grid, penalizer=penalizer, seed=seed)
        ic = ic_metricas(oof, grid, horizontes, B=B, seed=seed)
        fila = {"modelo": nombre, "n_param": len(covs), "AIC_parcial": cph.AIC_partial_}
        for m in ["C_Harrell", "C_Uno", f"AUC_{max(horizontes):g}", "IBS", "IPA_IBS"]:
            r = ic.loc[m]
            fila[m] = f"{r['estimador']:.3f} [{r['IC_inf']:.3f}, {r['IC_sup']:.3f}]"
        filas.append(fila)
    return pd.DataFrame(filas).set_index("modelo")