"""Semantic verification providers.

The default provider is offline and conservative. An application can inject a
real provider that implements the same interface (for example, an API or local
small language model) without changing cascade logic.
"""

import re
from typing import Protocol
from .models import DocumentChunk, QueryIntent, VerificationDecision


class SemanticArbiter(Protocol):
    def decide(self, query: str, old: DocumentChunk, new: DocumentChunk, intent: QueryIntent) -> VerificationDecision:
        ...


class HeuristicArbiter:
    """Offline semantic fallback based on changed facts and query terms."""

    def decide(self, query: str, old: DocumentChunk, new: DocumentChunk, intent: QueryIntent) -> VerificationDecision:
        old_numbers = set(re.findall(r"\b\d+(?:\.\d+)?\b", old.content))
        new_numbers = set(re.findall(r"\b\d+(?:\.\d+)?\b", new.content))
        changed_numbers = old_numbers != new_numbers
        old_tokens = set(re.findall(r"\b[a-z0-9_]+\b", old.content.lower()))
        new_tokens = set(re.findall(r"\b[a-z0-9_]+\b", new.content.lower()))
        overlap = len(old_tokens & new_tokens) / max(1, len(old_tokens | new_tokens))
        affects_query = changed_numbers or overlap < 0.92
        if intent.label in {"HISTORICAL_STATE", "COMPARISON"}:
            affects_query = False
        return VerificationDecision(
            changed=old.content.strip() != new.content.strip(),
            affects_query=affects_query,
            confidence=0.75 if changed_numbers else 0.60,
            rationale="Changed numeric or low-overlap facts are potentially answer-affecting.",
            provider="offline-heuristic",
        )
