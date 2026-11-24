from src.cascade import CascadeEngine
from src.knowledge_base import VERSIONED_DOCUMENTS
from src.intent import classify_query
from src.pipeline import StaleAwareRAG
from src.retriever import HybridRetriever


def test_current_query_repairs_old_return_policy():
    service = StaleAwareRAG()
    result = service.answer("What is the return window for this product today?")
    assert result.retrieved_chunk.version != result.effective_chunk.version
    assert result.effective_chunk.version == "v3"
    assert "7 days" in result.answer
    assert result.provenance[0]["version"] == "v3"


def test_historical_query_preserves_old_context():
    old = next(d for d in VERSIONED_DOCUMENTS if d.doc_id == "policy_returns_v1")
    result = CascadeEngine().run_cascade(old, "What was the return policy in 2023?")
    assert result.status == "HISTORICAL_CONTEXT_PRESERVED"
    assert result.repaired_chunk.version == "v1"


def test_comparison_intent_is_detected():
    assert classify_query("How did the policy change from 2023 to 2026?").label == "COMPARISON"


def test_unchanged_content_is_not_marked_stale():
    old = next(d for d in VERSIONED_DOCUMENTS if d.doc_id == "policy_returns_v1")
    latest = old.__class__(**{**old.__dict__, "doc_id": "policy_returns_v2", "version": "v2", "is_latest": True})
    result = CascadeEngine(documents=[old, latest]).run_cascade(old, "What is the current policy?")
    assert result.status == "CONTENT_EQUIVALENT"
    assert not result.stale_detected


def test_retriever_returns_ranked_results():
    results = HybridRetriever().retrieve("What apiVersion should I use for Kubernetes Ingress?", top_k=3)
    assert len(results) == 3
    assert results[0].similarity_score >= results[1].similarity_score
