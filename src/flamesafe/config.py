"""Central configuration loader. All paths/params come from configs/*.yaml + .env."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "configs"

load_dotenv(ROOT / ".env")


@lru_cache
def load(name: str) -> dict:
    """Load configs/<name>.yaml as a dict."""
    with open(CONFIG_DIR / f"{name}.yaml", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def data_dir() -> Path:
    return Path(os.getenv("FLAMESAFE_DATA_DIR", ROOT / "data")).resolve()


def publication() -> dict:
    return load("publication")["blocks"]
