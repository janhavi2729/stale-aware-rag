"""Domain models for version-aware retrieval and answer provenance."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class DocumentChunk:
    doc_id: str
    canonical_uri: str
    title: str
    dataset: str
    version: str
    release_date: str
    content: str
    is_latest: bool
    similarity_score: float = 0.0
    embedding: List[float] = field(default_factory=list)
    section_id: Optional[str] = None
    source_url: Optional[str] = None
    authority_score: float = 1.0
    content_hash: Optional[str] = None

@dataclass
class CascadeResult:
    original_chunk: DocumentChunk
    repaired_chunk: DocumentChunk
    tier_used: str
    status: str
    latency_ms: float
    stale_detected: bool
    details: str
    decision_trace: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 1.0
    query_intent: str = "CURRENT_STATE"

@dataclass
class QueryResult:
    system_name: str
    query: str
    retrieved_chunk: DocumentChunk
    effective_chunk: DocumentChunk
    answer: str
    is_correct: bool
    cascade_tier: str
    verification_latency_ms: float
    token_cost_units: int
    provenance: List[Dict[str, Any]] = field(default_factory=list)
    intent: str = "CURRENT_STATE"
    retrieval_method: str = "lexical"


@dataclass
class QueryIntent:
    """Temporal scope inferred from a user's question."""

    label: str
    confidence: float
    rationale: str = ""


@dataclass
class VerificationDecision:
    """Structured output from a semantic verification provider."""

    changed: bool
    affects_query: bool
    confidence: float
    rationale: str
    provider: str = "heuristic"
