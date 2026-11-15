"""
Dense Vector & Semantic Retrieval Simulation Engine.
Computes semantic similarity between query and corpus chunks.
In real-world corpora, historical chunks often score equal or higher similarity
due to lexical match and sentence structure.
"""

import math
import re
from typing import List, Tuple
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
