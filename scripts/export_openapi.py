"""Export the backend contract without loading models or reading API secrets."""

import json
from pathlib import Path

from flamesafe.api.main import create_app
from flamesafe.rag.settings import Settings

root = Path(__file__).resolve().parents[1]
target = root / "contracts" / "openapi.json"
target.parent.mkdir(exist_ok=True)
target.write_text(
    json.dumps(create_app(Settings(), token="").openapi(), indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)
