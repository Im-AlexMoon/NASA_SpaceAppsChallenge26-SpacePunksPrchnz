"""DE-04 · Render investigation profiles: docs/02_data_engineering/investigations/PSI-XX.md

Each profile has an AUTO block (regenerated from silver catalog + L2 file profiles) and a MANUAL block
(written by DE/PHY, preserved across regenerations). Only the text between the AUTO markers is replaced.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from flamesafe import config

AUTO_BEGIN = "<!-- AUTO:BEGIN — generado por `flamesafe profile`; no editar a mano dentro de este bloque -->"
AUTO_END = "<!-- AUTO:END -->"

MANUAL_TEMPLATE = """
## Evaluación (manual — DE/PHY)

> Completar a partir del bloque automático y de la lectura de la documentación del registro.
> Clasificar cada variable relevante como **Medida**, **Calculada** o **Log de prueba**.

### Resumen propio (2–3 líneas)
_por completar_

### Granularidad y variables clave
| Archivo | Fila = … | Variables de condición | Variables de resultado (medidas) | Calculadas | Notas |
|---|---|---|---|---|---|

### Problemas de calidad / acceso
_por completar_

### Valor para el proyecto
- **Pilar:** · **Entornos:**
- **RQ que habilita:**
- **Puntaje de triage R1–R6 (borrador):**
- **Tier propuesto:**
"""


def profiles_dir() -> Path:
    return config.ROOT / "docs" / "02_data_engineering" / "investigations"


def _gb(b: float | int | None) -> str:
    return "—" if b is None or pd.isna(b) else f"{b / 1e9:,.2f}"


def _fmt_num(x: Any) -> str:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return ""
    if isinstance(x, float):
        return f"{x:.4g}"
    return str(x)


def _esc(s: Any) -> str:
    return str(s).replace("|", "/").replace("\n", " ") if s is not None else ""


def _columns_table(cols: list[dict[str, Any]], limit: int = 60) -> str:
    lines = ["| # | Columna | Unidad (encabezado) | Tipo | No vacíos | Únicos | Rango / ejemplos | Tokens no numéricos |",
             "|---|---|---|---|---:|---:|---|---|"]
    for i, c in enumerate(cols[:limit], 1):
        rng = (f"{_fmt_num(c.get('min'))} … {_fmt_num(c.get('max'))}" if c["kind"] in ("numeric", "mixed")
               and "min" in c else ", ".join(c.get("examples", [])))
        toks = ", ".join(f"`{_esc(k)}`×{v}" for k, v in (c.get("non_numeric_tokens") or {}).items())
        lines.append(f"| {i} | {_esc(c['name'])} | {_esc(c.get('unit_in_header') or '')} | {c['kind']} | "
                     f"{c['non_empty']} | {c['n_unique']} | {_esc(rng)} | {toks} |")
    if len(cols) > limit:
        lines.append(f"| … | _{len(cols) - limit} columnas más_ | | | | | | |")
    return "\n".join(lines)


def _file_section(name: str, meta: dict[str, Any], prof: dict[str, Any]) -> str:
    head = (f"#### `{name}`\n\n- Lista: `{meta.get('list_source')}` · {meta.get('bytes', 0):,} bytes · "
            f"sha256 `{(meta.get('sha256') or '')[:16]}…` · HTTP {meta.get('http_status')}")
    if meta.get("http_status") != 200:
        return head + "\n- **No descargable en la verificación.**\n"
    if prof.get("profiled") is False:
        return head + f"\n- No perfilado: {prof.get('reason')}\n"
    if prof["format"] == "csv":
        s = (f"\n- CSV · encoding `{prof['encoding']}` · delimitador `{prof['delimiter']}` · encabezado en fila "
             f"{prof['header_row']} · filas no vacías **{prof['nonempty_rows']}** / físicas {prof['physical_rows']} · "
             f"**{prof['n_columns']}** columnas · bloques lado a lado: {prof['n_blocks']}")
        if prof.get("metadata_preamble"):
            kv = ", ".join(f"{k}={v}" for k, v in list(prof["metadata_preamble"].items())[:8])
            s += f"\n- Preámbulo de metadatos (fila 1): {_esc(kv)}…"
        body = _columns_table(prof["columns"])
        wrap = len(prof["columns"]) > 20
        table = f"<details><summary>Columnas ({len(prof['columns'])})</summary>\n\n{body}\n\n</details>" if wrap else body
        return f"{head}{s}\n\n{table}\n"
    parts = [f"{head}\n- {prof['format'].upper()} · **{prof['n_sheets']}** hojas"]
    for sh in prof["sheets"]:
        parts.append(f"\n<details><summary>Hoja <b>{_esc(sh['sheet'])}</b> — encabezado fila {sh.get('header_row', '—')}, "
                     f"{sh['nonempty_rows']} filas no vacías × {sh['n_columns']} columnas</summary>\n\n"
                     f"{_columns_table(sh['columns'], limit=40) if sh['columns'] else '_vacía_'}\n\n</details>")
    return "\n".join(parts) + "\n"


def render_auto(inv: pd.Series, files: pd.DataFrame, tables: pd.DataFrame, pubs: pd.DataFrame,
                sampled: list[tuple[str, dict, dict]]) -> str:
    psi = inv["psi_id"]
    added = files[(files["psi_id"] == psi) & (files["inventory"] == "added")]
    cats = added.groupby("category").agg(n=("file_name", "size"), b=("file_bytes", "sum")).sort_values("n", ascending=False)
    exts = added["extension"].value_counts().head(8)
    my_pubs = pubs[pubs["psi_id"] == psi]
    out = [AUTO_BEGIN, ""]
    out.append("| Campo | Valor (PSI) |\n|---|---|")
    for label, key in [("DOI de datos", "doi"), ("Tipo", "project_type"), ("Sub-área", "sub_research_area"),
                       ("Programa / plataforma", None), ("Hardware", "experiment_hardware"),
                       ("Centro", "managing_center"), ("Periodo", None), ("Licencia", "license_name"),
                       ("Investigaciones relacionadas", None), ("Snapshot", "snapshot")]:
        if key:
            val = inv.get(key)
        elif label.startswith("Programa"):
            val = f"{inv.get('flight_program') or '—'} / {inv.get('flight_platform') or '—'}"
        elif label == "Periodo":
            s, e = inv.get("start_date"), inv.get("end_date")
            val = f"{s.date() if pd.notna(s) else '—'} → {e.date() if pd.notna(e) else '—'}"
        else:
            rel = inv.get("related_investigations")
            val = ", ".join(list(rel) if rel is not None else []) or "—"
        out.append(f"| {label} | {_esc(val) if val is not None and not (isinstance(val, float) and pd.isna(val)) else '—'} |")

    out += ["", "### Inventario (L1)", "",
            "| Archivos `added` | Tablas exp. (fuera de `added`) | `removed` | Publicaciones (con DOI) | GB expuestos | GB registrados | Acceso |",
            "|---:|---:|---:|---:|---:|---:|---|",
            f"| {inv['n_added_files']:,} | {inv['n_experimental_tables']} ({inv['n_tables_not_in_added']}) | "
            f"{inv['n_removed_files']:,} | {inv['n_publications']} ({inv['n_publications_with_doi']}) | "
            f"{_gb(inv['added_bytes'])} | {_gb(inv['registered_total_bytes'])} | `{inv['access_status']}` |", ""]
    if len(cats):
        out.append("Categorías: " + " · ".join(f"{c} {r.n:,} ({_gb(r.b)} GB)" for c, r in cats.iterrows()))
        out.append("Extensiones: " + " · ".join(f"`.{e}` {n:,}" for e, n in exts.items()))
        out.append("")

    for label, key in [("Objetivo", "objective"), ("Hipótesis", "hypothesis")]:
        txt = inv.get(key)
        if isinstance(txt, str) and txt:
            short = txt if len(txt) <= 700 else txt[:700].rsplit(" ", 1)[0] + " …"
            out += [f"**{label} (texto PSI):**", "", "> " + _esc(short), ""]

    out += ["### Archivos perfilados (L2)", ""]
    if not sampled:
        out += ["_Ningún archivo tabular muestreado para este registro._", ""]
    for name, meta, prof in sampled:
        out.append(_file_section(name, meta, prof))

    with_doi = my_pubs[my_pubs["doi"].notna()].head(8)
    if len(with_doi):
        out += ["### Publicaciones con DOI (primeras 8)", ""]
        out += [f"- {_esc(r.title)} — doi:{r.doi}" for r in with_doi.itertuples()]
        out.append("")
    out.append(AUTO_END)
    return "\n".join(out)


def write_profile(path: Path, title: str, auto: str) -> str:
    """Create or update a profile, preserving everything outside the AUTO block. Returns action."""
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if AUTO_BEGIN in text and AUTO_END in text:
            pre, rest = text.split(AUTO_BEGIN, 1)
            _, post = rest.split(AUTO_END, 1)
            lines = pre.splitlines()
            pre = "\n".join([title] + lines[1:]) + ("\n" if lines else "")
            new = pre + auto + post
            action = "updated"
        else:
            new = f"{title}\n\n{auto}\n\n<!-- contenido previo sin marcadores -->\n{text}"
            action = "wrapped"
    else:
        new = f"{title}\n\n{auto}\n{MANUAL_TEMPLATE}"
        action = "created"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(new if new.endswith("\n") else new + "\n")
    return action


def render_all(silver_dir: Path, file_results: dict[str, dict], file_profiles: dict[str, dict],
               out_dir: Path | None = None) -> dict[str, str]:
    out_dir = out_dir or profiles_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    inv = pd.read_parquet(silver_dir / "investigations.parquet")
    files = pd.read_parquet(silver_dir / "files.parquet")
    tables = pd.read_parquet(silver_dir / "experimental_tables.parquet")
    pubs = pd.read_parquet(silver_dir / "publications.parquet")
    actions = {}
    for _, row in inv.iterrows():
        psi = row["psi_id"]
        sampled = sorted(
            [(k.split("/", 1)[1], file_results[k], file_profiles.get(k, {})) for k in file_results if k.startswith(psi + "/")],
            key=lambda t: (t[1].get("list_source") != "experimentalTable", t[0]),
        )
        acronym = row["acronym"] if isinstance(row["acronym"], str) else "(sin acrónimo)"
        title = f"# {psi} — {acronym} · {row['title']}"
        actions[psi] = write_profile(out_dir / f"{psi}.md",
                                     title, render_auto(row, files, tables, pubs, sampled))
    return actions
