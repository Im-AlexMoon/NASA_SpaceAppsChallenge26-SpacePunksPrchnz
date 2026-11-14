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
def bronze(
    dry_run: bool = typer.Option(False, help="Only resolve + check budget and drift; download nothing"),
    verify_only: bool = typer.Option(False, help="Only re-hash existing files against their sidecars"),
) -> None:
    """F2 - DE-06: download the L3 manifest lock into data/bronze/files (sha256 sidecars, 404s recorded)."""
    from flamesafe import config
    from flamesafe.ingestion import download as dl
    from flamesafe.pipeline.silver_catalog import silver_catalog_dir

    if verify_only:
        integ = dl.verify_integrity()
        typer.echo(f"Integrity: {integ['files_checked']} files checked, problems={integ['problems']}, "
                   f"orphans={len(integ['orphans'])}, partials={integ['partials']}")
        raise typer.Exit(code=1 if integ["problems"] or integ["partials"] else 0)

    lock = config.ROOT / "docs" / "02_data_engineering" / "acquisition_manifest.csv"
    reqs = dl.requests_from_lock(lock)
    b = config.load("acquisition_manifest")["budget"]
    total = dl.check_budget(reqs, b["max_total_mb"], b["max_file_mb"],
                            config.load("sources")["download_budget"]["deny_extensions"], b.get("max_files"))
    drift = dl.lock_drift(reqs, silver_catalog_dir())
    typer.echo(f"Manifest lock: {len(reqs)} files, {total / 1e6:.1f} MB - drift vs catalog: {len(drift)}")
    for d in drift:
        typer.secho(f"  DRIFT {d}", fg=typer.colors.YELLOW)
    if dry_run:
        return

    def show(r, action):
        if action not in ("fetched", "reused"):
            typer.secho(f"  {r.psi_id} {r.file_name}: {action}", fg=typer.colors.YELLOW)

    results = dl.fetch(reqs, progress=show)
    integ = dl.verify_integrity()
    report = dl.write_report(results, "l3_manifest", extra={"lock": lock.name, "lock_drift": drift, "integrity": integ})
    ok = sum(r.get("http_status") == 200 for r in results)
    mism = [r for r in results if r.get("size_matches") is False]
    typer.echo(f"Acquired {ok}/{len(results)} ({sum(r.get('bytes', 0) for r in results) / 1e6:.1f} MB) - "
               f"size mismatches {len(mism)} - integrity problems {len(integ['problems'])} - report {report.name}")
    if mism or integ["problems"]:
        raise typer.Exit(code=1)


@app.command()
def silver(
    only: list[str] = typer.Option(None, help="Run only these table parsers (see silver_parsers REGISTRY)"),
    skip_catalog: bool = typer.Option(False, help="Skip the catalog flattening step (DE-03)"),
) -> None:
    """F1/F2 - DE-03 + DE-07: bronze -> silver (catalog tables + data-table parsers)."""
    from flamesafe.pipeline import silver, silver_catalog

    errors = 0
    if not skip_catalog:
        rep = silver_catalog.run()
        bad = {k: v for k, v in rep["reconciliation"].items() if not v["ok"]}
        typer.echo(f"Catalog -> {rep['out_dir']}: {rep['row_counts']} - reconciliation {bad or 'OK'}")
        errors += rep["n_errors"]
    trep = silver.run(only=only or None)
    typer.echo(f"Data tables -> {trep['out_dir']}")
    for name, t in trep["tables"].items():
        flagged = sum(t["flagged_values"].values())
        typer.echo(f"  {name:<44} {t['rows']:>6} rows {t['columns']:>4} cols  flagged values {flagged}")
    for i in trep["issues"]:
        if i["level"] != "info":
            typer.secho(f"  [{i['level']}] {i['table']}: {i['issue']}", fg=typer.colors.RED if i["level"] == "error" else typer.colors.YELLOW)
    errors += trep["n_errors"]
    typer.echo(f"Errors: {errors} - warnings: {trep['n_warnings']}")
    if errors:
        raise typer.Exit(code=1)


@app.command()
def gold() -> None:
    """F2 - DE-08: build harmonized analysis-ready tables -> data/gold (Parquet + DuckDB)."""
    from flamesafe.pipeline import gold as g

    rep = g.run()
    typer.echo(f"Gold -> {rep['out_dir']}: {rep['row_counts']}")
    for table, chk in rep["checks"].items():
        typer.echo(f"  {table}: {chk}")
    typer.echo(f"Outcome coverage: {rep['outcome_coverage']}")
    for i in rep["invariants"]:
        if i["violations"]:
            typer.secho(f"  INVARIANT {i['table']}: {i['rule']} -> {i['violations']} violation(s)", fg=typer.colors.YELLOW)
    typer.echo(f"Invariant violations: {rep['n_invariant_violations']}")


@app.command()
def validate() -> None:
    """F2 - DE-09/DE-10: G2 gate — pandera contracts, reconciliation, token->NULL, dictionary coverage."""
    from flamesafe.quality import validate as v

    rep = v.run()
    for k, ok in rep["gate"].items():
        typer.secho(f"  {'PASS' if ok else 'FAIL'}  {k}", fg=typer.colors.GREEN if ok else typer.colors.RED)
    for name, c in rep["contracts"].items():
        if not c["ok"]:
            typer.secho(f"    contract {name}: {c['n_failures']} failure(s) e.g. {c['failures'][:3]}", fg=typer.colors.RED)
    for r in rep["reconciliation"]:
        if not r["ok"]:
            typer.secho(f"    reconcile {r['stage']} {r['table']}: expected {r['expected']} got {r['actual']}", fg=typer.colors.RED)
    for t in rep["tokens_never_valued"]:
        if not t["ok"]:
            typer.secho(f"    token->value {t['gold_table']}.{t['column']}: {t['valued_in_gold']} rows", fg=typer.colors.RED)
    for c in rep["dictionary_coverage"]:
        if not c["ok"]:
            typer.secho(f"    dictionary {c['table']}: undocumented={c['undocumented']} missing={c['documented_but_missing']}",
                        fg=typer.colors.RED)
    n = len(rep["contracts"])
    typer.echo(f"Contracts {sum(c['ok'] for c in rep['contracts'].values())}/{n} - reconciliation "
               f"{sum(r['ok'] for r in rep['reconciliation'])}/{len(rep['reconciliation'])} - token checks "
               f"{len(rep['tokens_never_valued'])} - G2 data gate: {'PASSED' if rep['passed'] else 'FAILED'}")
    if not rep["passed"]:
        raise typer.Exit(code=1)


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
