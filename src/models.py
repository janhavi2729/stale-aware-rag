"""
Data models for Stale-Aware RAG.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

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

@dataclass
class CascadeResult:
    original_chunk: DocumentChunk
    repaired_chunk: DocumentChunk
    tier_used: str
    status: str
    latency_ms: float
    stale_detected: bool
    details: str

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
