"""Versioned contracts shared by CLI, providers and HTTP API."""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class SourceRecord(Contract):
    source_id: str
    title: str
    source_type: str
    sha256: str
    locator: str
    language: str = "und"
    psi_ids: list[str] = Field(default_factory=list)
    original_url: str | None = None
    review_status: str = "source_reported"
    reviewed_by: str | None = None
    reviewed_at: str | None = None
    doi: str | None = None
    approved_sections: list[str] = Field(default_factory=list)
    aliases: list[str] = Field(default_factory=list)
    license_or_terms: str = "See original source"


class DocumentChunk(Contract):
    chunk_id: str
    source_id: str
    text: str
    section: str
    token_count: int
    language: str = "und"


ToolName = Literal[
    "find_investigations",
    "get_investigation",
    "find_publications",
    "summarize_gas_tests",
    "summarize_ignition_outcomes",
    "list_gas_tests",
    "summarize_droplet_tests",
    "summarize_reference_points",
    "get_variable_definition",
]


class QueryArgs(Contract):
    campaign: str | None = Field(default=None, max_length=80)
    flame_type: Literal["normal", "inverse"] | None = None
    fuel: str | None = Field(default=None, max_length=80)
    psi_id: str | None = Field(default=None, max_length=40)
    test_id: str | None = Field(default=None, max_length=80)
    ignition_outcome: Literal["yes", "no", "flash"] | None = None
    cohort: Literal["raw_gold", "audited_unique", "audited_verified_dates"] = "raw_gold"
    variable: str | None = Field(default=None, max_length=80)
    text: str | None = Field(default=None, max_length=200)
    limit: int = Field(default=30, ge=1, le=100)


class ToolRequest(Contract):
    tool: ToolName
    arguments: QueryArgs = Field(default_factory=QueryArgs)


class QueryPlan(Contract):
    route: Literal["documents", "structured", "mixed", "clarify", "prediction"]
    queries: list[ToolRequest] = Field(default_factory=list, max_length=2)
    clarification: str | None = Field(default=None, max_length=600)


class ToolResult(Contract):
    evidence_id: str
    tool_name: str
    template_version: str = "1"
    normalized_parameters: dict[str, Any]
    dataset_build_id: str
    population_or_cohort: str
    n_rows: int
    n_unique_tests: int | None = None
    n_operations: int | None = None
    n_valid_by_variable: dict[str, int] = Field(default_factory=dict)
    n_missing_by_variable: dict[str, int] = Field(default_factory=dict)
    units: dict[str, str] = Field(default_factory=dict)
    results: list[dict[str, Any]]
    warnings: list[str] = Field(default_factory=list)
    provenance_reference: str
    result_hash: str


class EvidenceBundle(Contract):
    build_id: str
    source_mode: Literal["sample", "full", "test"]
    chunks: list[DocumentChunk] = Field(default_factory=list)
    sources: list[SourceRecord] = Field(default_factory=list)
    tools: list[ToolResult] = Field(default_factory=list)


class Claim(Contract):
    kind: Literal["data", "interpretation", "limitation"]
    text: str = Field(max_length=1600)
    evidence_ids: list[str] = Field(min_length=1, max_length=8)
    numeric_fact_ids: list[str] = Field(default_factory=list)


class GeneratedAnswer(Contract):
    claims: list[Claim] = Field(max_length=8)


class ChatRequest(Contract):
    question: str = Field(min_length=1, max_length=2000)
    language: Literal["en", "es"] = "en"
    evidence_only: bool = True
    query: ToolRequest | None = None


class AnswerResult(Contract):
    status: Literal[
        "answered", "partial", "clarification_required", "insufficient_evidence", "unavailable"
    ]
    language: Literal["en", "es"]
    message: str
    claims: list[Claim] = Field(default_factory=list)
    evidence: EvidenceBundle
    navigation: str | None = None
    usage_tokens: int = 0


class BuildManifest(Contract):
    schema_version: str = "1"
    build_id: str
    created_at: str
    git_commit: str
    source_mode: Literal["sample", "full", "test"]
    retrieval_mode: Literal["hybrid", "lexical"]
    embedding_model: str | None = None
    embedding_revision: str | None = None
    row_counts: dict[str, int]
    input_hashes: dict[str, str]
    file_hashes: dict[str, str]
    settings: dict[str, Any]
    versions: dict[str, str]
