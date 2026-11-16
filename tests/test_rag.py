"""Offline contracts: no credentials, network, or production medallion writes."""

import json
import re
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from flamesafe.api.main import create_app
from flamesafe.rag.budget import Budget
from flamesafe.rag.index import build, current, validate
from flamesafe.rag.schemas import ChatRequest, Claim, GeneratedAnswer, QueryPlan, ToolRequest
from flamesafe.rag.service import RagService, validate_claims
from flamesafe.rag.settings import Settings


@pytest.fixture(scope="module")
def service(tmp_path_factory):
    root = tmp_path_factory.mktemp("rag")
    settings = Settings(artifact_root=root / "index", ledger_path=root / "usage.sqlite")
    build(settings, retrieval_mode="lexical")
    return RagService(settings)


@pytest.mark.parametrize(
    "tool,args",
    [
        ("find_investigations", {}),
        ("get_investigation", {"psi_id": "PSI-159"}),
        ("find_publications", {}),
        ("summarize_gas_tests", {}),
        ("summarize_ignition_outcomes", {}),
        ("list_gas_tests", {}),
        ("summarize_droplet_tests", {}),
        ("summarize_reference_points", {}),
        ("get_variable_definition", {"variable": "burn_time_s"}),
    ],
)
def test_tools(service, tool, args):
    result = service.tools.execute(ToolRequest(tool=tool, arguments=args))
    assert result.n_rows >= len(result.results)
    assert result.dataset_build_id == service.manifest.build_id
    assert result.result_hash and result.warnings
    json.loads(result.model_dump_json())


def test_sql_injection_is_a_value(service):
    result = service.tools.execute(
        ToolRequest(tool="list_gas_tests", arguments={"fuel": "' OR 1=1 --"})
    )
    assert result.n_rows == 0


@pytest.mark.parametrize(
    "args",
    [
        {"variable": "m_n2_mg_s"},
        {"variable": "m_fuel_mg_s", "flame_type": "inverse"},
        {"variable": "flex_burning_rate_unverified"},
        {"cohort": "audited_unique"},
    ],
)
def test_invalid_scopes_fail_closed(service, args):
    with pytest.raises(ValueError):
        service.tools.execute(ToolRequest(tool="summarize_gas_tests", arguments=args))


def test_ignition_preserves_missing_and_flash(service):
    result = service.tools.execute(ToolRequest(tool="summarize_ignition_outcomes"))
    assert sum(row["n"] for row in result.results) == result.n_rows
    assert (
        result.n_valid_by_variable["ignition_outcome"]
        + result.n_missing_by_variable["ignition_outcome"]
        == result.n_rows
    )
    assert any("Flash" in warning for warning in result.warnings)


def test_integrity(tmp_path):
    s = Settings(artifact_root=tmp_path)
    build(s, retrieval_mode="lexical")
    bundle = current(tmp_path)
    (bundle / "chunks.jsonl").write_text("tampered", encoding="utf-8")
    with pytest.raises(ValueError, match="integrity"):
        validate(bundle)


def test_no_provider_in_evidence_mode(service):
    response = service.ask(ChatRequest(question="burn_time_s", language="es"))
    assert response.evidence.chunks
    assert response.usage_tokens == 0
    assert response.status == "partial"
    assert not service.settings.ledger_path.exists()


def test_prediction_guard(service):
    response = service.ask(ChatRequest(question="Predict ignition on Mars"))
    assert response.navigation == "/atmosphere"
    assert not response.claims


def test_citation_and_number_validation(service):
    evidence = service.ask(ChatRequest(question="burn_time_s")).evidence
    chunk = evidence.chunks[0]
    validate_claims(
        GeneratedAnswer(
            claims=[Claim(kind="data", text=chunk.text[:80], evidence_ids=[chunk.chunk_id])]
        ),
        evidence,
    )
    for text, citation in [
        ("Invented result is 99999 s", chunk.chunk_id),
        (chunk.text[:80], "fake"),
    ]:
        with pytest.raises(ValueError):
            validate_claims(
                GeneratedAnswer(claims=[Claim(kind="data", text=text, evidence_ids=[citation])]),
                evidence,
            )


def test_atomic_budget(tmp_path):
    s = Settings(
        generation_enabled=True,
        billing_mode="free",
        daily_calls=3,
        monthly_calls=3,
        ledger_path=tmp_path / "ledger.sqlite",
    )

    def reserve(_):
        try:
            Budget(s).reserve()
            return True
        except ValueError:
            return False

    with ThreadPoolExecutor(max_workers=8) as pool:
        assert sum(pool.map(reserve, range(10))) == 3


def test_api_auth_and_readiness(service):
    app = create_app(service.settings, service=service, token="test-token")
    with TestClient(app) as client:
        assert client.get("/health/live").status_code == 200
        assert client.get("/health/ready").status_code == 200
        assert client.get("/v1/status").status_code == 401
        headers = {"Authorization": "Bearer test-token"}
        assert client.get("/v1/status", headers=headers).json()["source_mode"] == "sample"
        assert (
            client.post("/v1/data/query", headers=headers, json={"tool": "DROP TABLE"}).status_code
            == 422
        )
        assert (
            client.post("/v1/chat", headers=headers, json={"question": "burn_time_s"}).status_code
            == 200
        )


def test_provider_calls_bounded(service, tmp_path):
    class FakeProvider:
        calls = 0

        def generate(self, schema, instructions, payload):
            self.calls += 1
            if schema is QueryPlan:
                return QueryPlan(route="documents"), 10
            return GeneratedAnswer(
                claims=[Claim(kind="data", text="fabricated", evidence_ids=["invalid"])]
            ), 10

    fake = FakeProvider()
    settings = service.settings.model_copy(
        update={
            "generation_enabled": True,
            "billing_mode": "free",
            "daily_calls": 10,
            "monthly_calls": 10,
            "ledger_path": tmp_path / "ledger.sqlite",
        }
    )
    response = RagService(settings, provider=fake).ask(
        ChatRequest(question="burn_time_s", evidence_only=False)
    )
    assert fake.calls == 3
    assert not response.claims


def test_zero_missing_flash_and_repeated_identity_are_distinct(tmp_path):
    import pandas as pd

    from flamesafe import config
    from flamesafe.rag.tools import TABLES

    inputs = tmp_path / "inputs"
    inputs.mkdir()
    for table in TABLES:
        frame = pd.read_parquet(config.ROOT / "data/sample" / f"gold_{table}.parquet")
        if table == "gas_flame_tests":
            frame = frame.head(4).copy()
            frame["psi_id"] = "PSI-159"
            frame["test_id"] = [f"T{i}" for i in range(4)]
            frame["campaign"] = "CFI-G"
            frame["flame_type"] = "normal"
            frame["fuel"] = "fixture"
            frame["xo2"] = [0.0, 0.0, 1.0, None]
            frame["ignition_outcome"] = ["yes", "no", "flash", None]
            frame = pd.concat([frame, frame.iloc[[0]]], ignore_index=True)
        frame.to_parquet(inputs / f"{table}.parquet", index=False)
    s = Settings(artifact_root=tmp_path / "bundles")
    build(s, source_mode="test", retrieval_mode="lexical", input_dir=inputs)
    instance = RagService(s)
    summary = instance.tools.execute(ToolRequest(tool="summarize_gas_tests"))
    assert summary.n_rows == 5 and summary.n_unique_tests == 4
    assert summary.n_valid_by_variable["xo2"] == 4
    assert summary.n_missing_by_variable["xo2"] == 1
    assert summary.results[0]["median"] == 0
    assert summary.n_operations is None
    outcomes = instance.tools.execute(ToolRequest(tool="summarize_ignition_outcomes"))
    counts = {row["ignition_outcome"]: row["n"] for row in outcomes.results}
    assert counts == {"yes": 2, "no": 1, "flash": 1, None: 1}


def test_ambiguous_units_and_empty_query(service):
    response = service.ask(ChatRequest(question="oxígeno 34", language="es"))
    assert response.status == "clarification_required"
    response = service.ask(
        ChatRequest(
            question="tests",
            query=ToolRequest(tool="list_gas_tests", arguments={"fuel": "does-not-exist"}),
        )
    )
    assert response.status == "insufficient_evidence"


def test_retained_evidence(service):
    result = service.tools.execute(ToolRequest(tool="summarize_ignition_outcomes"))
    assert service.tools.retained(result.evidence_id) == result
    assert service.tools.retained("unknown") is None


def test_synthesized_claims_keep_numbers_grounded(service):
    evidence = service.ask(ChatRequest(question="burn_time_s")).evidence
    chunk = next(c for c in evidence.chunks if re.search(r"\d", c.text))
    number = re.search(r"\d+(?:[.,]\d+)?", chunk.text).group()
    ok = Claim(kind="interpretation", text=f"In short, the source reports {number}.", evidence_ids=[chunk.chunk_id])
    validate_claims(GeneratedAnswer(claims=[ok]), evidence)
    bad = Claim(kind="interpretation", text="In short, the source reports 987654.", evidence_ids=[chunk.chunk_id])
    with pytest.raises(ValueError):
        validate_claims(GeneratedAnswer(claims=[bad]), evidence)


def test_counts_of_findings_are_not_numeric_filters(service):
    for question in ("¿Cuáles son los 3 descubrimientos más relevantes?", "What are the 3 main findings?"):
        assert service.ask(ChatRequest(question=question)).status != "clarification_required"
    assert service.ask(ChatRequest(question="oxígeno 34", language="es")).status == "clarification_required"
