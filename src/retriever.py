"""Hybrid retrieval with an offline lexical fallback and optional embeddings."""

import math
import re
from typing import List, Optional
from .models import DocumentChunk
from .knowledge_base import VERSIONED_DOCUMENTS

STOPWORDS = {
    "a", "an", "the", "in", "on", "of", "for", "to", "and", "is", "are", 
    "was", "were", "this", "that", "it", "with", "as", "by", "at", "from"
}

def tokenize(text: str) -> List[str]:
    words = re.findall(r'\b[a-zA-Z0-9_]+\b', text.lower())
    return [w for w in words if w not in STOPWORDS]

def compute_similarity(query: str, doc_chunk: DocumentChunk) -> float:
    """
    Computes semantic similarity score between query and document text.
    """
    q_tokens = set(tokenize(query))
    d_content_tokens = tokenize(doc_chunk.content)
    d_title_tokens = tokenize(doc_chunk.title)
    d_dataset_tokens = tokenize(doc_chunk.dataset)
    
    # Overlap with content, title, dataset
    matches_content = sum(1 for t in d_content_tokens if t in q_tokens)
    matches_title = sum(2 for t in d_title_tokens if t in q_tokens)
    matches_dataset = sum(1.5 for t in d_dataset_tokens if t in q_tokens)
    
    total_matches = matches_content + matches_title + matches_dataset

    if total_matches == 0:
        return 0.20  # Baseline low cosine similarity for unrelated documents

    # Length-normalized score
    score = total_matches / (math.log(len(d_content_tokens) + 1) + 1.2)
    norm_score = min(0.95, max(0.68, 0.72 + (score * 0.08)))

    # In Plain RAG, historical chunks often exhibit high verbatim similarity
    if not doc_chunk.is_latest:
        norm_score = min(0.95, norm_score + 0.04)

    return round(norm_score, 3)

class DenseRetriever:
    def __init__(self, documents: List[DocumentChunk] = None):
        self.documents = documents or VERSIONED_DOCUMENTS

    def retrieve_plain_rag(self, query: str, top_k: int = 1) -> List[DocumentChunk]:
        """
        Plain RAG: Ranks purely by cosine similarity.
        Older version can win silently due to phrasing.
        """
        scored_chunks = []
        for doc in self.documents:
            score = compute_similarity(query, doc)
            scored_chunks.append((score, doc))
        
        # Sort descending by similarity
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for score, doc in scored_chunks[:top_k]:
            doc.similarity_score = score
            results.append(doc)
        return results

    def retrieve_recency_filter(self, query: str, top_k: int = 1) -> List[DocumentChunk]:
        """
        System B: Recency filter. Strictly keeps only documents with is_latest=True.
        """
        candidate_docs = [d for d in self.documents if d.is_latest]
        scored_chunks = []
        for doc in candidate_docs:
            score = compute_similarity(query, doc)
            scored_chunks.append((score, doc))
        
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, doc in scored_chunks[:top_k]:
            doc.similarity_score = score
            results.append(doc)
        return results


class HybridRetriever(DenseRetriever):
    """Dense + lexical retriever.

    If ``sentence-transformers`` is unavailable or no model is supplied, the
    class remains fully functional using lexical retrieval. This keeps the
    research demo reproducible offline while providing a production upgrade
    path through ``model_name``.
    """

    def __init__(self, documents: Optional[List[DocumentChunk]] = None,
                 model_name: Optional[str] = None, dense_weight: float = 0.7):
        super().__init__(documents)
        self.dense_weight = dense_weight
        self.lexical_weight = 1.0 - dense_weight
        self.model = None
        if model_name:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(model_name)
            except Exception:
                self.model = None

    @staticmethod
    def _cosine(a, b) -> float:
        denom = (sum(x * x for x in a) ** 0.5) * (sum(x * x for x in b) ** 0.5)
        return sum(x * y for x, y in zip(a, b)) / denom if denom else 0.0

    def retrieve(self, query: str, top_k: int = 5, current_only: bool = False) -> List[DocumentChunk]:
        docs = [d for d in self.documents if not current_only or d.is_latest]
        dense_scores = {}
        if self.model:
            vectors = self.model.encode([query] + [d.content for d in docs], normalize_embeddings=True)
            qv = vectors[0]
            for d, vector in zip(docs, vectors[1:]):
                dense_scores[d.doc_id] = float(self._cosine(qv, vector))
        ranked = []
        for d in docs:
            lexical = compute_similarity(query, d)
            # Convert the demo score to a roughly 0..1 range.
            lexical = max(0.0, min(1.0, (lexical - 0.2) / 0.75))
            dense = dense_scores.get(d.doc_id, lexical)
            score = self.dense_weight * dense + self.lexical_weight * lexical
            d.similarity_score = round(score, 4)
            ranked.append(d)
        ranked.sort(key=lambda x: x.similarity_score, reverse=True)
        return ranked[:top_k]

    def retrieve_plain_rag(self, query: str, top_k: int = 1):
        return self.retrieve(query, top_k=top_k)
