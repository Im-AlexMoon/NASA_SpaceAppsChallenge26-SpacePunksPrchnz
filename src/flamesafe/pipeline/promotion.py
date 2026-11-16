"""Publish a set of completed files and restore their previous versions on error."""

import shutil
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4


@contextmanager
def stage_files(parent: Path, prefix: str):
    """Stage next to the destination so promoted files inherit the same access policy."""
    parent = parent.resolve()
    stage = parent / f".{prefix}-{uuid4().hex}"
    stage.mkdir()
    retain = False
    try:
        yield stage
    except BaseException:
        retain = any(path.is_file() for path in (stage / ".previous").rglob("*"))
        raise
    finally:
        if stage.resolve().parent != parent:
            raise RuntimeError("Staging directory is outside the destination parent.")
        if not retain:
            shutil.rmtree(stage)


def promote_files(stage: Path, destination: Path) -> None:
    files = tuple(path for path in stage.rglob("*") if path.is_file())
    backup = stage / ".previous"
    prior = []
    installed = []
    try:
        for path in files:
            relative = path.relative_to(stage)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                original = backup / relative
                original.parent.mkdir(parents=True, exist_ok=True)
                target.replace(original)
                prior.append((original, target))
            path.replace(target)
            installed.append(target)
    except OSError:
        for target in reversed(installed):
            target.unlink()
        for original, target in reversed(prior):
            original.replace(target)
        raise
