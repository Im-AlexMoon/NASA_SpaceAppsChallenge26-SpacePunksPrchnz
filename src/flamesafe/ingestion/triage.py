"""DE-05 · Reproducible triage: rubric scores (configs/triage.yaml) -> weighted score -> gated tier.

score = Σ w_k · R_k / 3  ∈ [0, 1]
rubric tier: 1 if score ≥ thresholds.tier1, 2 if ≥ thresholds.tier2, else 3
gates: a tier is only kept if its gate holds; otherwise the record drops one tier (and the reason is recorded)
override: an explicit {tier, reason, by} (PHY) replaces the computed tier and is shown in the matrix
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from flamesafe import config

CRITERIA = ("R1", "R2", "R3", "R4", "R5", "R6")
AUTO_BEGIN = "<!-- TRIAGE:BEGIN — generado por `flamesafe triage` desde configs/triage.yaml -->"
AUTO_END = "<!-- TRIAGE:END -->"


class TriageError(ValueError):
    pass


def score(scores: dict[str, int], weights: dict[str, float]) -> float:
    return round(sum(weights[k] * scores[k] for k in CRITERIA) / 3, 3)


def gated_tier(s: dict[str, int], value: float, cfg: dict[str, Any]) -> tuple[int, int, list[str]]:
    th, gates = cfg["thresholds"], cfg.get("gates", {})
    rubric = 1 if value >= th["tier1"] else 2 if value >= th["tier2"] else 3
    tier, notes = rubric, []
    g1 = gates.get("tier1", {})
    if tier == 1:
        failed = [f"{k[:2]}<{v}" for k, v in g1.items() if s[k[:2]] < v]
        if failed:
            tier = 2
            notes.append("gate T1: " + ", ".join(failed))
    g2 = gates.get("tier2", {})
    if tier == 2 and "R3_or_R4_min" in g2 and max(s["R3"], s["R4"]) < g2["R3_or_R4_min"]:
        tier = 3
        notes.append(f"gate T2: R3 y R4 < {g2['R3_or_R4_min']}")
    return rubric, tier, notes


def validate(cfg: dict[str, Any], expected_ids: list[str]) -> None:
    inv = cfg.get("investigations") or {}
    problems = [f"falta {p}" for p in expected_ids if p not in inv]
    problems += [f"sobra {p}" for p in inv if p not in expected_ids]
    if abs(sum(cfg["weights"].values()) - 1) > 1e-9:
        problems.append(f"los pesos suman {sum(cfg['weights'].values())}")
    for p, d in inv.items():
        sc = d.get("scores", {})
        bad = [k for k in CRITERIA if not isinstance(sc.get(k), int) or not 0 <= sc[k] <= 3]
        if bad:
            problems.append(f"{p}: puntajes inválidos {bad}")
        if not d.get("justification"):
            problems.append(f"{p}: sin justificación")
        ov = d.get("override")
        if ov and not (ov.get("tier") in (1, 2, 3) and ov.get("reason") and ov.get("by")):
            problems.append(f"{p}: override requiere tier, reason y by")
    if problems:
        raise TriageError("configs/triage.yaml inválido:\n  " + "\n  ".join(problems))


def compute(cfg: dict[str, Any], investigations: pd.DataFrame) -> pd.DataFrame:
    validate(cfg, investigations["psi_id"].tolist())
    meta = investigations.set_index("psi_id")
    rows = []
    for psi_id, d in cfg["investigations"].items():
        s = d["scores"]
        value = score(s, cfg["weights"])
        rubric, tier, notes = gated_tier(s, value, cfg)
        ov = d.get("override")
        if ov:
            notes.append(f"override {ov['by']}: {ov['reason']}")
            tier = ov["tier"]
        rows.append({
            "psi_id": psi_id,
            "acronym": meta.loc[psi_id, "acronym"] if isinstance(meta.loc[psi_id, "acronym"], str) else None,
            "project_type": meta.loc[psi_id, "project_type"],
            "access_status": meta.loc[psi_id, "access_status"],
            **{k: s[k] for k in CRITERIA},
            "score": value,
            "tier_rubric": rubric,
            "tier": tier,
            "tier_notes": "; ".join(notes) or None,
            "pillars": ", ".join(d.get("pillars", [])),
            "environments": ", ".join(d.get("environments", [])),
            "rqs": ", ".join(d.get("rqs", [])),
            "justification": d["justification"],
        })
    df = pd.DataFrame(rows)
    df["_n"] = df["psi_id"].str.split("-").str[1].astype(int)
    return df.sort_values(["tier", "score", "_n"], ascending=[True, False, True]).drop(columns="_n").reset_index(drop=True)


def render_markdown(df: pd.DataFrame) -> str:
    head = ("| PSI | Acrónimo | R1 | R2 | R3 | R4 | R5 | R6 | Score | Tier | Pilar | Entornos | RQ | Justificación |\n"
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|---|")
    lines = [AUTO_BEGIN, "", head]
    for r in df.itertuples():
        notes = r.tier_notes if isinstance(r.tier_notes, str) else ""
        tier = f"**{r.tier}**" + (f" ⟵ {r.tier_rubric} ({notes})" if notes else "")
        acr = r.acronym if isinstance(r.acronym, str) else ("— (tierra)" if r.project_type == "Ground Investigation" else "—")
        lines.append(f"| [{r.psi_id}](investigations/{r.psi_id}.md) | {acr} | {r.R1} | {r.R2} | {r.R3} | {r.R4} | "
                     f"{r.R5} | {r.R6} | {r.score:.3f} | {tier} | {r.pillars} | {r.environments} | {r.rqs} | "
                     f"{str(r.justification).replace('|', '/')} |")
    counts = df["tier"].value_counts().sort_index()
    lines += ["", "Resumen: " + " · ".join(f"Tier {t}: {n}" for t, n in counts.items()), "", AUTO_END]
    return "\n".join(lines)


def write_outputs(df: pd.DataFrame, doc: Path | None = None, csv_path: Path | None = None) -> tuple[Path, Path]:
    base = config.ROOT / "docs" / "02_data_engineering"
    doc = doc or base / "TRIAGE_METHODOLOGY.md"
    csv_path = csv_path or base / "triage_matrix.csv"
    df.to_csv(csv_path, index=False, lineterminator="\n")
    text = doc.read_text(encoding="utf-8")
    block = render_markdown(df)
    if AUTO_BEGIN in text and AUTO_END in text:
        pre, rest = text.split(AUTO_BEGIN, 1)
        _, post = rest.split(AUTO_END, 1)
        text = pre + block + post
    else:
        raise TriageError(f"{doc} no tiene los marcadores {AUTO_BEGIN!r} … {AUTO_END!r}")
    with open(doc, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return doc, csv_path
