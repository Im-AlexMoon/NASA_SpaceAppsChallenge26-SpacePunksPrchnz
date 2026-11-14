"""Single entry point: `flamesafe <command>`. One command per pipeline stage (see Makefile)."""

from __future__ import annotations

import typer

app = typer.Typer(help="flamesafe pipeline CLI", no_args_is_help=True)


def _todo(task_id: str) -> None:
    typer.secho(f"Not implemented yet — see task {task_id} in docs/00_executive/EXECUTIVE_PLAN.md",
                fg=typer.colors.YELLOW)
    raise typer.Exit(code=1)


@app.command()
def catalog() -> None:
    """F1 - DE-02: fetch the PSI combustion catalog (metadata only) into bronze."""
    _todo("DE-02")


@app.command()
def bronze() -> None:
    """F2 - DE-06: download manifest-selected files into bronze (sha256 + sidecar)."""
    _todo("DE-06")


@app.command()
def silver() -> None:
    """F2 - DE-07: parse, type, clean and unit-annotate bronze -> silver."""
    _todo("DE-07")


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
