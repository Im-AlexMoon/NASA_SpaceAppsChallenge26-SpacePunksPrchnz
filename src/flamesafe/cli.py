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


@app.command("video-samples")
def video_samples(dry_run: bool = typer.Option(False, help="Only resolve, lock and check the budget")) -> None:
    """ADR-0009: download the explicit video feasibility sample (exact file names only) into data/bronze/files."""
    from flamesafe import config
    from flamesafe.ingestion import download as dl
    from flamesafe.pipeline.silver_catalog import silver_catalog_dir

    man = config.load("video_samples")
    if any(isinstance(e, dict) for g in man["groups"] for es in g["files"].values() for e in es):
        raise typer.BadParameter("video_samples.yaml must list exact file names, never patterns (ADR-0009)")
    reqs = dl.requests_from_selection(man, silver_catalog_dir())
    unlocked = {e.lower() for e in man.get("unlock_extensions", [])}
    deny = [e for e in config.load("sources")["download_budget"]["deny_extensions"] if e.lower() not in unlocked]
    b = man["budget"]
    total = dl.check_budget(reqs, b["max_total_mb"], b["max_file_mb"], deny, b.get("max_files"))
    lock = dl.write_manifest_lock(reqs, config.ROOT / "docs" / "02_data_engineering" / "video_samples.csv")
    typer.echo(f"Video sample: {len(reqs)} files, {total / 1e6:.1f} MB (budget {b['max_total_mb']} MB) -> {lock.name}")
    if dry_run:
        return
    results = dl.fetch(reqs, workers=2)
    report = dl.write_report(results, "video_samples", extra={"lock": lock.name})
    ok = sum(r.get("http_status") == 200 for r in results)
    mism = [r for r in results if r.get("size_matches") is False]
    typer.echo(f"Acquired {ok}/{len(results)} ({sum(r.get('bytes', 0) for r in results) / 1e6:.1f} MB) - "
               f"size mismatches {len(mism)} - report {report.name}")
    if mism or ok < len(results):
        raise typer.Exit(code=1)


VIDEO_LOCK = ("docs", "02_data_engineering", "video_manifest.csv")


@app.command("video-manifest")
def video_manifest() -> None:
    """ADR-0009 phase 2: resolve every CFI-G video into the lock used by the Cloud Run Job (downloads nothing)."""
    from flamesafe import config
    from flamesafe.ingestion import download as dl
    from flamesafe.pipeline.silver_catalog import silver_catalog_dir

    man = config.load("video_manifest")
    reqs = dl.requests_from_selection(man, silver_catalog_dir())
    unlocked = {e.lower() for e in man.get("unlock_extensions", [])}
    deny = [e for e in config.load("sources")["download_budget"]["deny_extensions"] if e.lower() not in unlocked]
    b = man["budget"]
    total = dl.check_budget(reqs, b["max_total_mb"], b["max_file_mb"], deny, b.get("max_files"))
    lock = dl.write_manifest_lock(reqs, config.ROOT.joinpath(*VIDEO_LOCK))
    typer.echo(f"Video manifest: {len(reqs)} files, {total / 1e9:.2f} GB -> {lock.name} (task index = row number)")


@app.command("video-task")
def video_task(
    index: int = typer.Option(None, help="Row of the lock to process (default: $CLOUD_RUN_TASK_INDEX)"),
    output: str = typer.Option(None, help="Local folder or gs://bucket/prefix (default: $FLAMESAFE_VIDEO_OUTPUT)"),
    local_file: str = typer.Option(None, help="Measure this local video instead of downloading the row's file"),
    overwrite: bool = typer.Option(False, help="Re-process even if the summary already exists"),
) -> None:
    """ADR-0009: measure one CFI-G video (one Cloud Run task). The video is deleted after measuring."""
    import os
    from pathlib import Path

    import pandas as pd

    from flamesafe import config
    from flamesafe.pipeline import video

    index = index if index is not None else int(os.environ.get("CLOUD_RUN_TASK_INDEX", "0"))
    output = output or os.environ.get("FLAMESAFE_VIDEO_OUTPUT")
    if not output:
        raise typer.BadParameter("set --output or FLAMESAFE_VIDEO_OUTPUT")
    lock = pd.read_csv(config.ROOT.joinpath(*VIDEO_LOCK), dtype={"expected_bytes": "Int64"})
    if not 0 <= index < len(lock):
        raise typer.BadParameter(f"index {index} outside 0..{len(lock) - 1}")
    row = lock.iloc[index]
    expected = None if pd.isna(row.expected_bytes) else int(row.expected_bytes)
    res = video.process_file(row.psi_id, row.file_name, expected, video.Output(output),
                             local_path=Path(local_file) if local_file else None, overwrite=overwrite)
    typer.echo(f"task {index}: {row.file_name} -> {res}")


@app.command("video-collect")
def video_collect(
    source: str = typer.Option(None, help="Local folder or gs://bucket/prefix (default: $FLAMESAFE_VIDEO_OUTPUT)"),
) -> None:
    """ADR-0009: gather the per-video summaries into silver `acme__video_features`."""
    import os

    from flamesafe import config
    from flamesafe.pipeline import video

    source = source or os.environ.get("FLAMESAFE_VIDEO_OUTPUT")
    if not source:
        raise typer.BadParameter("set --source or FLAMESAFE_VIDEO_OUTPUT")
    table = video.collect(video.Output(source))
    out = config.data_dir() / "silver" / "tables" / "acme__video_features.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    table.to_parquet(out, index=False)
    seen = int(table["flame_seen"].sum()) if len(table) else 0
    typer.echo(f"Video features: {len(table)} videos, flame seen in {seen} -> {out.name}")


@app.command()
def timeseries(
    dry_run: bool = typer.Option(False, help="Only resolve the selection, write the lock and check the budget"),
    workers: int = typer.Option(6, help="Parallel downloads (keep small: PSI is a public NASA service)"),
) -> None:
    """ADR-0005: download the opt-in per-test time series (ACME CFI-G / Flame Design) into data/bronze/files."""
    import pandas as pd

    from flamesafe import config
    from flamesafe.ingestion import download as dl
    from flamesafe.pipeline.silver_catalog import silver_catalog_dir

    man = config.load("timeseries_manifest")
    reqs = dl.requests_from_selection(man, silver_catalog_dir())
    b = man["budget"]
    total = dl.check_budget(reqs, b["max_total_mb"], b["max_file_mb"],
                            config.load("sources")["download_budget"]["deny_extensions"], b.get("max_files"))
    lock = dl.write_manifest_lock(reqs, config.ROOT / "docs" / "02_data_engineering" / "timeseries_manifest.csv")
    typer.echo(f"Time-series manifest: {len(reqs)} files, {total / 1e6:.1f} MB "
               f"(budget {b['max_total_mb']} MB / {b['max_files']} files) -> {lock.name}")
    by = pd.DataFrame([{"group": r.reason, "bytes": r.expected_bytes} for r in reqs]).groupby("group")["bytes"]
    for g, r in by.agg(["size", "sum"]).iterrows():
        typer.echo(f"  {g:<22} {int(r['size']):>5} files {r['sum'] / 1e6:>8.1f} MB")
    if dry_run:
        return

    done = {"n": 0}

    def show(r, action):
        done["n"] += 1
        if action not in ("fetched", "reused"):
            typer.secho(f"  {r.psi_id} {r.file_name}: {action}", fg=typer.colors.YELLOW)
        if done["n"] % 250 == 0:
            typer.echo(f"  ... {done['n']}/{len(reqs)}")

    results = dl.fetch(reqs, progress=show, workers=workers)
    report = dl.write_report(results, "timeseries", extra={"lock": lock.name})
    ok = sum(r.get("http_status") == 200 for r in results)
    mism = [r for r in results if r.get("size_matches") is False]
    typer.echo(f"Acquired {ok}/{len(results)} ({sum(r.get('bytes', 0) for r in results) / 1e6:.1f} MB) - "
               f"size mismatches {len(mism)} - report {report.name}")
    if mism or ok < len(results):
        raise typer.Exit(code=1)


@app.command("ts-features")
def ts_features() -> None:
    """ADR-0005: reduce every downloaded ACME time series to one row (silver `acme__timeseries_features`)."""
    from flamesafe.pipeline import timeseries as ts

    table = ts.build_features()
    errors = int(table["parse_error"].notna().sum())
    typer.echo(f"Time-series features: {len(table)} tests ({table['psi_id'].value_counts().to_dict()}), "
               f"flame seen in {int(table['flame_seen'].fillna(False).sum())}, parse errors {errors}")
    if errors:
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
def rag_index(source_mode: str = "sample", retrieval_mode: str = "hybrid", allow_download: bool = typer.Option(False, "--allow-download", "--allow-model-download")) -> None:
    """Build an immutable RAG snapshot; downloads require an explicit flag."""
    from flamesafe.rag.index import build
    from flamesafe.rag.settings import settings
    typer.echo(build(settings(), source_mode, retrieval_mode, allow_download).model_dump_json(indent=2))


@app.command("rag-validate")
def rag_validate() -> None:
    """Validate hashes, citations and row counts of CURRENT."""
    from flamesafe.rag.index import current, validate
    from flamesafe.rag.settings import settings
    typer.echo(validate(current(settings().artifact_root)).model_dump_json(indent=2))


@app.command("rag-ask")
def rag_ask(question: str = typer.Option(..., "--question", "-q"), language: str = "en", evidence_only: bool = typer.Option(True, "--evidence-only/--generate")) -> None:
    """Ask locally. Evidence-only unless --generate is explicitly selected."""
    from flamesafe.rag.schemas import ChatRequest
    from flamesafe.rag.service import RagService
    from flamesafe.rag.settings import settings
    request = ChatRequest(question=question, language=language, evidence_only=evidence_only)
    typer.echo(RagService(settings()).ask(request).model_dump_json(indent=2))


@app.command("rag-eval")
def rag_eval(offline: bool = True) -> None:
    """Run the versioned bilingual offline definition/retrieval baseline."""
    from flamesafe import config
    from flamesafe.rag.evaluation import evaluate
    from flamesafe.rag.service import RagService
    from flamesafe.rag.settings import settings
    if not offline:
        raise typer.BadParameter("Live provider evaluation requires a separate reviewed budget and rubric.")
    report = evaluate(RagService(settings()), config.ROOT / "artifacts/rag_eval/report.json")
    typer.echo({key: value for key, value in report.items() if key != "cases"})


if __name__ == "__main__":
    app()
