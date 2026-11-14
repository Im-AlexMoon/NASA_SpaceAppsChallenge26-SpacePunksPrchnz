"""Single entry point: `flamesafe <command>`. One command per pipeline stage (see Makefile)."""

from __future__ import annotations

from pathlib import Path

import typer

app = typer.Typer(help="flamesafe pipeline CLI", no_args_is_help=True)


def _todo(task_id: str) -> None:
    typer.secho(f"Not implemented yet — see task {task_id} in docs/00_executive/EXECUTIVE_PLAN.md",
                fg=typer.colors.YELLOW)
    raise typer.Exit(code=1)


@app.command("verify-api")
def verify_api(
    out: Path = typer.Option(None, help="Report path (default: docs/02_data_engineering/verification/)"),
    skip_downloads: bool = typer.Option(False, help="Do not download the experimental tables"),
) -> None:
    """F1 - DE-01: verify PSI endpoints and write a JSON evidence report (metadata only)."""
    from flamesafe.ingestion import verify

    report = verify.run(download_tables=not skip_downloads)
    path = verify.write(report, out or verify.default_output())
    c, t, e = report["collection"], report["totals"], report["endpoints"]
    typer.echo(f"Investigations: {c['total_investigations']} total, {c['combustion_count']} combustion")
    typer.echo(f"Detail 200: {e['investigation']['http_200']}/{e['investigation']['requested']} - "
               f"tables 200: {e['download']['tables_http_200']}/{e['download']['tables_requested']}")
    typer.echo(f"Access status: {t['access_status']}")
    for k in report["known_issue_rechecks"]:
        typer.echo(f"Re-check {k['psi_id']} '{k['file_name'][:50]}...': HTTP {k['http_status_now']}")
    typer.echo(f"Report: {path}  ({report['elapsed_s']} s)")


@app.command()
def catalog(
    refresh: bool = typer.Option(False, help="Re-fetch files already present in today's snapshot"),
) -> None:
    """F1 - DE-02: snapshot the PSI combustion catalog (metadata only) into data/bronze/catalog."""
    from flamesafe.ingestion import catalog as cat

    res = cat.run(refresh=refresh, progress=lambda pid, msg: typer.echo(f"  {pid:<8} {msg}"))
    typer.echo(f"Snapshot: {res.snapshot_dir}")
    typer.echo(f"Combustion records: {len(res.combustion_ids)} - fetched {len(res.fetched)}, "
               f"reused {len(res.reused)}, failed {len(res.failed)}")
    if res.drift:
        typer.echo(f"Drift vs {res.drift['compared_with'][0]}: changed={res.drift['changed']} "
                   f"added={res.drift['added']} missing={res.drift['missing']}")
    if not res.complete:
        typer.secho(f"Incomplete snapshot (LATEST not updated): {res.failed}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command()
def profile(
    docs: bool = typer.Option(True, help="Render docs/02_data_engineering/investigations/PSI-XX.md"),
) -> None:
    """F1 - DE-04: download L2 samples (configs/l2_samples.yaml), profile them, render investigation profiles."""
    import json
    from collections import Counter

    from flamesafe import config
    from flamesafe.ingestion import download as dl
    from flamesafe.ingestion import profile_docs
    from flamesafe.ingestion.profile import profile_file
    from flamesafe.pipeline.silver_catalog import silver_catalog_dir

    cfg = config.load("l2_samples")
    reqs = dl.requests_from_l2(cfg, silver_catalog_dir())
    total = dl.check_budget(reqs, cfg["budget"]["max_total_mb"], cfg["budget"]["max_file_mb"],
                            config.load("sources")["download_budget"]["deny_extensions"])
    typer.echo(f"L2 selection: {len(reqs)} files, {total / 1e6:.1f} MB (budget {cfg['budget']['max_total_mb']} MB)")
    results = dl.fetch(reqs, progress=lambda r, a: a in ("fetched", "reused") or typer.echo(f"  {r.psi_id} {r.file_name}: {a}"))
    report = dl.write_report(results, "l2_samples")
    by_key = {f"{r['psi_id']}/{r['file_name']}": r for r in results}
    profiles = {k: profile_file(dl.files_root() / k) for k, r in by_key.items() if r.get("http_status") == 200}
    prof_path = report.parent / "l2_profiles.json"
    prof_path.write_text(json.dumps(profiles, indent=1, default=str, ensure_ascii=False), encoding="utf-8")
    ok = sum(r.get("http_status") == 200 for r in results)
    typer.echo(f"Downloaded/verified {ok}/{len(results)} - profiled {sum(p.get('profiled', True) for p in profiles.values())}"
               f" - reports: {report.name}, {prof_path.name}")
    if docs:
        actions = profile_docs.render_all(silver_catalog_dir(), by_key, profiles)
        typer.echo(f"Investigation profiles: {dict(Counter(actions.values()))}")


@app.command()
def triage() -> None:
    """F1 - DE-05: score/tier the 24 investigations and resolve the L3 acquisition manifest (no download)."""
    import pandas as pd

    from flamesafe import config
    from flamesafe.ingestion import download as dl
    from flamesafe.ingestion import triage as tri
    from flamesafe.pipeline.silver_catalog import silver_catalog_dir

    inv = pd.read_parquet(silver_catalog_dir() / "investigations.parquet")
    df = tri.compute(config.load("triage"), inv)
    doc, csv_path = tri.write_outputs(df)
    typer.echo(f"Triage: {df['tier'].value_counts().sort_index().to_dict()} -> {csv_path.name}, {doc.name}")
    for t in (1, 2):
        typer.echo(f"  Tier {t}: " + ", ".join(f"{r.psi_id}({r.score:.2f})" for r in df[df.tier == t].itertuples()))

    man = config.load("acquisition_manifest")
    reqs = dl.requests_from_selection(man, silver_catalog_dir())
    b = man["budget"]
    total = dl.check_budget(reqs, b["max_total_mb"], b["max_file_mb"],
                            config.load("sources")["download_budget"]["deny_extensions"], b.get("max_files"))
    lock = dl.write_manifest_lock(reqs, config.ROOT / "docs" / "02_data_engineering" / "acquisition_manifest.csv")
    by = pd.DataFrame([{"group": r.reason, "bytes": r.expected_bytes} for r in reqs]).groupby("group")["bytes"].agg(["size", "sum"])
    typer.echo(f"Acquisition manifest: {len(reqs)} files, {total / 1e6:.1f} MB "
               f"(budget {b['max_total_mb']} MB / {b.get('max_files')} files) -> {lock.name}")
    for g, r in by.iterrows():
        typer.echo(f"  {g:<30} {int(r['size']):>4} files {r['sum'] / 1e6:>8.1f} MB")


@app.command()
def bronze() -> None:
    """F2 - DE-06: download manifest-selected files into bronze (sha256 + sidecar)."""
    _todo("DE-06")


@app.command()
def silver() -> None:
    """F1/F2 - DE-03 + DE-07: bronze -> silver (catalog flattening now; data-table parsers in DE-07)."""
    from flamesafe.pipeline import silver_catalog

    rep = silver_catalog.run()
    typer.echo(f"Catalog -> {rep['out_dir']}")
    for name, n in rep["row_counts"].items():
        typer.echo(f"  {name:<20} {n:>6} rows")
    bad = {k: v for k, v in rep["reconciliation"].items() if not v["ok"]}
    typer.echo(f"Reconciliation vs raw JSON: {bad or 'OK'} - issues: {len(rep['issues'])} "
               f"({rep['n_errors']} errors)")
    typer.secho("Experimental-table parsers: pending (DE-07)", fg=typer.colors.YELLOW)
    if rep["n_errors"]:
        raise typer.Exit(code=1)


@app.command()
def gold() -> None:
    """F2 - DE-08: build harmonized analysis-ready tables -> gold."""
    _todo("DE-08")


@app.command()
def train() -> None:
    """F4 - DS-08: train/evaluate models declared in configs/models.yaml."""
    _todo("DS-08")


@app.command("rag-index")
def rag_index() -> None:
    """F5 - RAG-02: build the hybrid retrieval index."""
    _todo("RAG-02")


if __name__ == "__main__":
    app()
