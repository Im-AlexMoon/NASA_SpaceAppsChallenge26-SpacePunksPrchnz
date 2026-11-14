from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def sample_dir() -> Path:
    """Tiny committed fixtures (data/sample/) — never real bronze data."""
    return ROOT / "data" / "sample"
