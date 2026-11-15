"""Build/validate immutable snapshots, then atomically select CURRENT."""

import os
import re
import subprocess
import uuid
from contextlib import suppress
from datetime import UTC, datetime
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import duckdb
import pandas as pd

from flamesafe import config
from flamesafe.rag.corpus import build_corpus
from flamesafe.rag.schemas import BuildManifest, DocumentChunk, SourceRecord
from flamesafe.rag.tools import TABLES
from flamesafe.rag.utils import file_hash, write_json


def build(
    settings, source_mode="sample", retrieval_mode="hybrid", allow_download=False, input_dir=None
):
    if source_mode not in {"sample", "full", "test"}:
        raise ValueError("Explicit sample/full/test source mode required.")
    inputs = input_dir or (
        config.ROOT / "data" / "sample" if source_mode == "sample" else config.data_dir() / "gold"
    )
    tables, hashes = {}, {}
    for table in TABLES:
        path = inputs / (f"gold_{table}.parquet" if source_mode == "sample" else f"{table}.parquet")
        hashes[path.name] = file_hash(path)
        tables[table] = pd.read_parquet(path)
    model = None
    if retrieval_mode == "hybrid":
        from flamesafe.rag.embeddings import LocalEmbeddings

        model = LocalEmbeddings(settings, allow_download)
    elif retrieval_mode != "lexical":
        raise ValueError("Unknown retrieval mode.")
    count = model.count if model else lambda text: len(text.split())
    sources, chunks, definitions, doc_hashes = build_corpus(tables["investigations"], count)
    hashes.update(doc_hashes)
    # Capture uncommitted implementation changes as well as the Git base commit.
    for path in sorted((config.ROOT / "src/flamesafe/rag").glob("*.py")):
        hashes[path.relative_to(config.ROOT).as_posix()] = file_hash(path)
    for relative in ("src/flamesafe/analysis/segmentation.py", "uv.lock"):
        hashes[relative] = file_hash(config.ROOT / relative)
    for name in ("rag.yaml", "rag_sources.yaml"):
        hashes[f"configs/{name}"] = file_hash(config.CONFIG_DIR / name)
    if not chunks:
        raise ValueError("Eligible corpus is empty.")
    root = settings.artifact_root
    root.mkdir(parents=True, exist_ok=True)
    build_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:12]
    stage = root / (".building-" + build_id)
    stage.mkdir()
    with duckdb.connect(str(stage / "query_snapshot.duckdb")) as con:
        for table, frame in tables.items():
            con.register("input_frame", frame)
            con.execute(f"CREATE TABLE {table} AS SELECT * FROM input_frame")
        con.register("definitions", definitions)
        con.execute("CREATE TABLE variable_definitions AS SELECT * FROM definitions")
        if source_mode == "full":
            paths = [
                config.data_dir() / "silver" / "tables" / f"{prefix}__eventdata.parquet"
                for prefix in ("psi159", "psi10")
            ]
            if all(path.exists() for path in paths):
                from flamesafe.analysis.segmentation import audit_gas_observations

                events = pd.concat(
                    [
                        pd.read_parquet(path).assign(psi_id=psi)
                        for path, psi in zip(paths, ("PSI-159", "PSI-10"), strict=True)
                    ]
                )
                audit = audit_gas_observations(tables["gas_flame_tests"], events)
                con.register("audit_frame", audit.observations)
                con.execute("CREATE TABLE audited_gas AS SELECT * FROM audit_frame")
                for path in paths:
                    hashes[path.name] = file_hash(path)
    for filename, items in (("sources.jsonl", sources), ("chunks.jsonl", chunks)):
        (stage / filename).write_text(
            "".join(item.model_dump_json() + "\n" for item in items), encoding="utf-8"
        )
    if model:
        import lancedb

        vectors = model.encode([chunk.text for chunk in chunks])
        lancedb.connect(str(stage / "vectors")).create_table(
            "chunks",
            data=[
                {"chunk_id": chunk.chunk_id, "vector": vector}
                for chunk, vector in zip(chunks, vectors, strict=True)
            ],
        )
    versions = {}
    for package in ("flamesafe", "duckdb", "sentence-transformers", "rank-bm25", "lancedb"):
        with suppress(PackageNotFoundError):
            versions[package] = version(package)
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=config.ROOT, capture_output=True, text=True, check=False
    ).stdout.strip()
    manifest = BuildManifest(
        build_id=build_id,
        created_at=datetime.now(UTC).isoformat(),
        git_commit=commit,
        source_mode=source_mode,
        retrieval_mode=retrieval_mode,
        embedding_model=settings.embedding_model if model else None,
        embedding_revision=settings.embedding_revision if model else None,
        row_counts={name: len(frame) for name, frame in tables.items()},
        input_hashes=hashes,
        file_hashes={
            path.relative_to(stage).as_posix(): file_hash(path)
            for path in stage.rglob("*")
            if path.is_file()
        },
        settings={"chunk_max": 384, "rrf_constant": 60, "top_k": 8, "candidates": 30},
        versions=versions,
    )
    write_json(stage / "manifest.json", manifest.model_dump())
    validate(stage)
    stage.rename(root / build_id)
    pointer = root / ("CURRENT." + uuid.uuid4().hex)
    pointer.write_text(build_id, encoding="utf-8")
    os.replace(pointer, root / "CURRENT")
    return manifest


def current(root: Path) -> Path:
    build_id = (root / "CURRENT").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"[\w-]+", build_id):
        raise ValueError("Invalid build pointer.")
    return root / build_id


def load_records(bundle):
    return (
        [
            SourceRecord.model_validate_json(line)
            for line in (bundle / "sources.jsonl").read_text(encoding="utf-8").splitlines()
        ],
        [
            DocumentChunk.model_validate_json(line)
            for line in (bundle / "chunks.jsonl").read_text(encoding="utf-8").splitlines()
        ],
    )


def validate(bundle: Path):
    manifest = BuildManifest.model_validate_json(
        (bundle / "manifest.json").read_text(encoding="utf-8")
    )
    if not {"query_snapshot.duckdb", "sources.jsonl", "chunks.jsonl"}.issubset(
        manifest.file_hashes
    ):
        raise ValueError("Missing required bundle files.")
    for name, expected in manifest.file_hashes.items():
        path = (bundle / name).resolve()
        path.relative_to(bundle.resolve())
        if file_hash(path) != expected:
            raise ValueError(f"Artifact integrity failure: {name}")
    sources, chunks = load_records(bundle)
    ids = {source.source_id for source in sources}
    if len(ids) != len(sources) or any(chunk.source_id not in ids for chunk in chunks):
        raise ValueError("Invalid source references.")
    if len({chunk.chunk_id for chunk in chunks}) != len(chunks):
        raise ValueError("Duplicate chunk IDs.")
    with duckdb.connect(str(bundle / "query_snapshot.duckdb"), read_only=True) as con:
        for name in TABLES:
            if (
                con.execute(f"SELECT count(*) FROM {name}").fetchone()[0]
                != manifest.row_counts[name]
            ):
                raise ValueError("Snapshot row count mismatch.")
    return manifest
