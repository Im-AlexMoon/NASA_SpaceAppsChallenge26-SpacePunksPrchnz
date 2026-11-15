"""API: ranking, atmosphere readings and findings served from an evidence snapshot, gated by configs/publication.yaml."""

from __future__ import annotations

from types import SimpleNamespace

import duckdb
import pandas as pd
import pytest

pytest.importorskip("fastapi")
pytest.importorskip("cantera")

from fastapi.testclient import TestClient  # noqa: E402

from flamesafe import config  # noqa: E402
from flamesafe.api import content  # noqa: E402
from flamesafe.api.main import create_app  # noqa: E402
from flamesafe.rag.settings import Settings  # noqa: E402

TOKEN = "test-token"
H = {"Authorization": f"Bearer {TOKEN}"}


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    bundle = tmp_path_factory.mktemp("bundle")
    sample = config.ROOT / "data" / "sample"
    with duckdb.connect(str(bundle / "query_snapshot.duckdb")) as con:
        for t in ("investigations", "gas_flame_tests"):
            df = pd.read_parquet(sample / f"gold_{t}.parquet")
            con.register("df", df)
            con.execute(f"CREATE TABLE {t} AS SELECT * FROM df")
            con.unregister("df")
    service = SimpleNamespace(bundle=bundle, manifest=SimpleNamespace(build_id="test", source_mode="sample",
                                                                       retrieval_mode="lexical", row_counts={}))
    with TestClient(create_app(Settings(), service=service, token=TOKEN)) as c:  # runs the app lifespan
        yield c


def test_auth_required(client):
    assert client.post("/v1/ranking", json={}).status_code == 401


def test_ranking_profiles_and_custom_weights(client):
    profiles = client.get("/v1/ranking/profiles", headers=H).json()
    assert "lunar_habitat_engineer" in profiles["profiles"] and "evidence" in profiles["dimensions"]
    r = client.post("/v1/ranking", headers=H, json={"profile": "lunar_habitat_engineer"}).json()
    assert r["rows"][0]["rank"] == 1 and r["sensitivity"]["n_perturbations"] == 14
    assert abs(sum(r["weights"].values()) - 1) < 1e-9
    custom = client.post("/v1/ranking", headers=H, json={"weights": {"pillar_deteccion": 1}, "environment": "nave"})
    assert custom.status_code == 200 and custom.json()["sensitivity"] is None
    assert client.post("/v1/ranking", headers=H, json={"weights": {"magic": 1}}).status_code == 422


def test_readings(client):
    ref = client.get("/v1/readings/atmospheres", headers=H).json()
    tiers = {r["key"]: r["tier"] for r in ref["readings"]}
    assert tiers["spacesuit"] == "C" and tiers["lunar_base_upper"] in {"A", "B"}
    suit = next(r for r in ref["readings"] if r["key"] == "spacesuit")
    assert suit["prediction"] is None and ref["review"]["status"] == "reviewed"
    one = client.post("/v1/readings/atmosphere", headers=H, json={"xo2": 0.30, "p_kpa": 70.3, "gravity": "moon"}).json()
    assert one["gravity_effect"]["tier"] == "C" and one["prediction"]["median_burn_s"] > 0
    bad = client.post("/v1/readings/atmosphere", headers=H, json={"xo2": 1.5, "p_kpa": 70})
    assert bad.status_code == 422


def test_findings(client):
    f = client.get("/v1/findings", headers=H).json()
    ids = [x["id"] for x in f["findings"]]
    assert ids == ["F-01", "F-02", "F-03", "F-04", "F-05"] and f["status"] == "reviewed"


def test_publication_switch(client, monkeypatch):
    blocks = content.publication()
    monkeypatch.setattr("flamesafe.api.main.publication",
                        lambda: {**blocks, "model_readings": {**blocks["model_readings"], "enabled": False}})
    assert client.get("/v1/readings/atmospheres", headers=H).status_code == 403
