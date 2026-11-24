"""Lightweight temporal query-intent classification.

The classifier is deliberately deterministic so the demo works offline. It can
be replaced by an LLM classifier without changing the rest of the pipeline.
"""

import re
from .models import QueryIntent


HISTORICAL = re.compile(r"\b(in|during|as of|before|until|back in)\s+(19|20)\d{2}\b|\b(previous|old|historical|then)\b", re.I)
COMPARISON = re.compile(r"\b(compare|difference|changed|change|between|from .* to|versus|vs\.?|how did .* evolve)\b", re.I)
CURRENT = re.compile(r"\b(today|now|currently|current|latest|modern|present|this version|as of today)\b", re.I)


def classify_query(query: str) -> QueryIntent:
    """Return CURRENT_STATE, HISTORICAL_STATE, COMPARISON, or UNKNOWN."""
    if COMPARISON.search(query):
        return QueryIntent("COMPARISON", 0.95, "The query asks how multiple versions differ.")
    if HISTORICAL.search(query):
        return QueryIntent("HISTORICAL_STATE", 0.95, "The query contains an explicit historical time reference.")
    if CURRENT.search(query):
        return QueryIntent("CURRENT_STATE", 0.95, "The query explicitly asks for the current state.")
    return QueryIntent("CURRENT_STATE", 0.60, "No historical scope was detected; current-state is the safe default.")
