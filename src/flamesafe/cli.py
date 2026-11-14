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
