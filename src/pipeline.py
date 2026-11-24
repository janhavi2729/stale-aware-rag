"""End-to-end Stale-Aware RAG application service."""

from typing import Iterable, Optional
from .cascade import CascadeEngine
from .generator import AnswerGenerator
from .models import DocumentChunk, QueryResult
from .retriever import HybridRetriever


class StaleAwareRAG:
    def __init__(self, documents: Optional[Iterable[DocumentChunk]] = None,
                 embedding_model: Optional[str] = None):
        docs = list(documents) if documents is not None else None
        self.retriever = HybridRetriever(docs, model_name=embedding_model)
        self.cascade = CascadeEngine(documents=docs)

    def answer(self, query: str, top_k: int = 5) -> QueryResult:
        candidates = self.retriever.retrieve(query, top_k=top_k)
        if not candidates:
            raise ValueError("No documents are available for retrieval.")
        retrieved = candidates[0]
        verification = self.cascade.run_cascade(retrieved, query=query)
        answer = AnswerGenerator.generate_answer(query, verification.repaired_chunk)
        cost = 2 if "Tier 1" in verification.tier_used else 12
        provenance = [{
            "doc_id": verification.repaired_chunk.doc_id,
            "canonical_uri": verification.repaired_chunk.canonical_uri,
            "version": verification.repaired_chunk.version,
            "release_date": verification.repaired_chunk.release_date,
            "source_url": verification.repaired_chunk.source_url,
            "status": verification.status,
        }]
        return QueryResult(
            system_name="Stale-Aware RAG",
            query=query,
            retrieved_chunk=retrieved,
            effective_chunk=verification.repaired_chunk,
            answer=answer,
            is_correct=verification.repaired_chunk.is_latest,
            cascade_tier=verification.tier_used,
            verification_latency_ms=verification.latency_ms,
            token_cost_units=cost,
            provenance=provenance,
            intent=verification.query_intent,
            retrieval_method="hybrid-dense+lexical" if self.retriever.model else "lexical-fallback",
        )
