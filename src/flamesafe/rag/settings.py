"""Settings are read at invocation, never secrets at import time."""

import os
from pathlib import Path

from pydantic import Field

from flamesafe import config
from flamesafe.rag.schemas import Contract


class Settings(Contract):
    provider: str = "gemini"
    model: str = ""
    generation_enabled: bool = False
    max_output_tokens: int = Field(default=1500, ge=128, le=4096)
    max_input_chars: int = Field(default=24000, ge=1000, le=50000)
    request_deadline_seconds: int = Field(default=65, ge=1, le=100)
    firestore_project: str | None = None
    cloud_runtime: bool = False
    timeout_seconds: int = Field(default=30, ge=1, le=120)
    daily_calls: int = Field(default=0, ge=0)
    monthly_calls: int = Field(default=0, ge=0)
    daily_budget_usd: float = Field(default=0, ge=0)
    monthly_budget_usd: float = Field(default=0, ge=0)
    reservation_usd: float = Field(default=0, ge=0)
    billing_mode: str = "disabled"
    artifact_root: Path = config.ROOT / "artifacts" / "rag"
    ledger_path: Path = config.ROOT / "artifacts" / "rag_usage.sqlite"
    embedding_model: str = "intfloat/multilingual-e5-small"
    embedding_revision: str = ""
    embedding_path: Path = config.ROOT / "artifacts" / "embedding-model"
    top_k: int = 8


def settings() -> Settings:
    raw = config.load("rag")
    return Settings(
        provider=os.getenv("FLAMESAFE_LLM_PROVIDER", raw["llm"]["provider"]),
        model=os.getenv("FLAMESAFE_LLM_MODEL") or os.getenv("GEMINI_MODEL", ""),
        generation_enabled=os.getenv("FLAMESAFE_GENERATION_ENABLED", "false").lower() == "true",
        max_output_tokens=raw["llm"]["max_tokens"],
        billing_mode=os.getenv("FLAMESAFE_BILLING_MODE", "disabled"),
        daily_calls=int(os.getenv("FLAMESAFE_DAILY_CALLS", "0")),
        monthly_calls=int(os.getenv("FLAMESAFE_MONTHLY_CALLS", "0")),
        daily_budget_usd=float(os.getenv("FLAMESAFE_DAILY_BUDGET_USD", "0")),
        monthly_budget_usd=float(os.getenv("FLAMESAFE_MONTHLY_BUDGET_USD", "0")),
        reservation_usd=float(os.getenv("FLAMESAFE_CALL_RESERVATION_USD", "0")),
        artifact_root=Path(
            os.getenv("FLAMESAFE_RAG_DIR", config.ROOT / "artifacts" / "rag")
        ).resolve(),
        firestore_project=os.getenv("FLAMESAFE_FIRESTORE_PROJECT"),
        cloud_runtime=bool(os.getenv("K_SERVICE")),
        ledger_path=Path(
            os.getenv("FLAMESAFE_LEDGER_PATH", config.ROOT / "artifacts" / "rag_usage.sqlite")
        ).resolve(),
        embedding_model=raw["embeddings"]["model"],
        embedding_revision=raw["embeddings"].get("revision", ""),
        embedding_path=Path(
            os.getenv("FLAMESAFE_EMBEDDING_PATH", config.ROOT / "artifacts" / "embedding-model")
        ).resolve(),
    )
