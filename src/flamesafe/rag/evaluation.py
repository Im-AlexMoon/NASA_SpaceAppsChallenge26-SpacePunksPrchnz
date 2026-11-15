"""Reproducible offline bilingual retrieval baseline; not a scientific release gate."""

import json
from time import perf_counter

from flamesafe import config
from flamesafe.rag.schemas import ChatRequest
from flamesafe.rag.utils import write_json


def evaluate(service, output=None):
    cases = config.ROOT / "docs/03_data_science/rag_eval.jsonl"
    results = []
    for line in cases.read_text(encoding="utf-8").splitlines():
        case = json.loads(line)
        started = perf_counter()
        answer = service.ask(
            ChatRequest(question=case["question"], language=case["language"], query=case["query"])
        )
        rows = [row for result in answer.evidence.tools for row in result.results]
        expected_sources = {
            row["source_id"] for row in rows if row["variable"] == case["expected_variable"]
        }
        retrieved = {chunk.source_id for chunk in answer.evidence.chunks}
        results.append(
            {
                "id": case["id"],
                "language": case["language"],
                "exact_definition": bool(expected_sources),
                "retrieval_hit_at_8": bool(expected_sources & retrieved),
                "seconds": perf_counter() - started,
            }
        )
    report = {
        "build_id": service.manifest.build_id,
        "source_mode": service.manifest.source_mode,
        "retrieval_mode": service.manifest.retrieval_mode,
        "provider_calls": 0,
        "n_cases": len(results),
        "n_semantic_pairs": len(results) // 2,
        "definition_success": sum(r["exact_definition"] for r in results) / len(results),
        "hit_at_8": sum(r["retrieval_hit_at_8"] for r in results) / len(results),
        "limitations": [
            "Definition-focused baseline with explicit variable identifiers.",
            "Does not evaluate natural-language tool planning, semantic entailment, live generation or scientific review.",
        ],
        "cases": results,
    }
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        write_json(output, report)
    return report
