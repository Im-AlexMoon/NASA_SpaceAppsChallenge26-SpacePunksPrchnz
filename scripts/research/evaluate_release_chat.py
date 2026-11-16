"""Run release questions against the selected lexical or hybrid evidence bundle."""

import argparse
from pathlib import Path
from time import perf_counter

from flamesafe.rag.schemas import ChatRequest, ToolRequest
from flamesafe.rag.service import RagService, validate_claims
from flamesafe.rag.settings import settings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate", action="store_true", help="Opt in to provider calls and configured quotas")
    parser.add_argument("--artifact-root", type=Path, help="Select a separate lexical or hybrid bundle root")
    args = parser.parse_args()
    setup = settings()
    if args.artifact_root:
        setup = setup.model_copy(update={"artifact_root": args.artifact_root})
    if args.generate and not setup.generation_enabled:
        raise SystemExit("Enable generation and configure provider quotas before running the live benchmark.")
    service = RagService(setup)
    questions = [
        ("en", "Where does burn_time_s come from?", ToolRequest(tool="get_variable_definition", arguments={"variable": "burn_time_s"})),
        ("es", "¿Cuál es el origen de burn_time_s?", ToolRequest(tool="get_variable_definition", arguments={"variable": "burn_time_s"})),
        ("en", "Count normal CFI-G ignition outcomes", ToolRequest(tool="summarize_ignition_outcomes", arguments={"campaign": "CFI-G", "flame_type": "normal"})),
        ("es", "Pruebas de un combustible ausente", ToolRequest(tool="list_gas_tests", arguments={"fuel": "NOT-IN-DATASET"})),
        ("en", "What are the key findings of the study?", None),
        ("es", "¿Cuáles son los principales hallazgos del estudio?", None),
        ("en", "What are the limits of the exploration cohort comparison?", None),
        ("es", "¿Puede predecir la duración en gravedad parcial?", None),
    ]
    print(service.manifest.build_id, service.manifest.retrieval_mode, service.manifest.source_mode)
    for lang, question, query in questions:
        started = perf_counter()
        reply = service.ask(ChatRequest(
            language=lang, question=question, query=query,
            evidence_only=bool(query) or not args.generate,
        ))
        validate_claims(reply, reply.evidence)
        print(f"{lang} {reply.status} in {perf_counter() - started:.2f} s: {question}")
        print(f"  sources={len(reply.evidence.sources)} claims={len(reply.claims)} queries={len(reply.evidence.tools)}")
        if query is not None and not reply.evidence.tools:
            raise SystemExit("Exact query did not return its result envelope.")


if __name__ == "__main__":
    main()
