"""Version-aware document ingestion helpers."""

import hashlib
from dataclasses import replace
from typing import Dict, Iterable, List
from .models import DocumentChunk


def content_hash(content: str) -> str:
    return hashlib.sha256(content.strip().encode("utf-8")).hexdigest()


def prepare_chunks(chunks: Iterable[DocumentChunk]) -> List[DocumentChunk]:
    """Normalize hashes and section IDs without mutating caller-owned objects."""
    prepared = []
    for index, chunk in enumerate(chunks):
        prepared.append(replace(
            chunk,
            section_id=chunk.section_id or f"section-{index + 1}",
            content_hash=chunk.content_hash or content_hash(chunk.content),
        ))
    return prepared


def build_version_catalog(chunks: Iterable[DocumentChunk]) -> Dict[str, DocumentChunk]:
    """Return the latest chunk per canonical URI, using date as a fallback."""
    catalog: Dict[str, DocumentChunk] = {}
    for chunk in prepare_chunks(chunks):
        current = catalog.get(chunk.canonical_uri)
        if chunk.is_latest or current is None or chunk.release_date > current.release_date:
            catalog[chunk.canonical_uri] = chunk
    return catalog
