"""Temporal verification cascade and provenance-preserving context repair."""

import time
from dataclasses import replace
from typing import Dict, Iterable, Optional

from .ingestion import build_version_catalog, content_hash
from .intent import classify_query
from .models import CascadeResult, DocumentChunk, QueryIntent
from .semantic_arbiter import HeuristicArbiter, SemanticArbiter
from .knowledge_base import VERSIONED_DOCUMENTS

class CascadeEngine:
    def __init__(self, catalog: Optional[Dict[str, DocumentChunk]] = None,
                 documents: Optional[Iterable[DocumentChunk]] = None,
                 arbiter: Optional[SemanticArbiter] = None):
        self.catalog = catalog or build_version_catalog(documents or VERSIONED_DOCUMENTS)
        self.arbiter = arbiter or HeuristicArbiter()

    def run_cascade(self, chunk: DocumentChunk, query: str = "",
                    intent: Optional[QueryIntent] = None) -> CascadeResult:
        start = time.perf_counter()
        intent = intent or classify_query(query)
        latest = self.catalog.get(chunk.canonical_uri)
        trace = []

        if not latest:
            return self._result(chunk, chunk, "Tier 0 (Unindexed)", "UNCHECKED", start, False,
                                "No version catalog entry found; retained original context.", trace, 0.0, intent)

        trace.append({"tier": "Tier 1", "check": "metadata", "version": chunk.version,
                      "latest_version": latest.version})
        if intent.label in {"HISTORICAL_STATE", "COMPARISON"}:
            return self._result(chunk, chunk, "Tier 1 (Temporal Scope)", "HISTORICAL_CONTEXT_PRESERVED",
                                start, False, f"Query intent is {intent.label}; historical context preserved.", trace, 1.0, intent)
        if chunk.version == latest.version and chunk.is_latest:
            return self._result(chunk, chunk, "Tier 1 (Metadata Check)", "VERIFIED_CURRENT", start, False,
                                "Metadata matches the active release.", trace, 1.0, intent)

        old_hash = chunk.content_hash or content_hash(chunk.content)
        new_hash = latest.content_hash or content_hash(latest.content)
        trace.append({"tier": "Tier 2", "check": "content_hash", "old_hash": old_hash, "new_hash": new_hash})
        if old_hash == new_hash:
            return self._result(chunk, chunk, "Tier 2 (Hash Check)", "CONTENT_EQUIVALENT", start, False,
                                "Version labels differ, but content is equivalent.", trace, 1.0, intent)

        decision = self.arbiter.decide(query, chunk, latest, intent)
        trace.append({"tier": "Tier 3", "provider": decision.provider,
                      "affects_query": decision.affects_query, "confidence": decision.confidence,
                      "rationale": decision.rationale})
        if not decision.affects_query:
            return self._result(chunk, chunk, "Tier 3 (Semantic Arbiter)", "CHANGE_NOT_RELEVANT", start, False,
                                decision.rationale, trace, decision.confidence, intent)

        repaired = replace(latest, similarity_score=chunk.similarity_score, content_hash=new_hash)
        return self._result(chunk, repaired, "Tier 2/3 (Diff & Context Repair)",
                            "STALE_DETECTED_AND_REPAIRED", start, True,
                            f"Replaced {chunk.version} with authoritative {latest.version}.", trace,
                            decision.confidence, intent)

    @staticmethod
    def _result(original, repaired, tier, status, start, stale, details, trace, confidence, intent):
        elapsed = (time.perf_counter() - start) * 1000
        return CascadeResult(original, repaired, tier, status, round(elapsed, 3), stale,
                             details, trace, confidence, intent.label)
