"""
Adaptive Verification Cascade Controller
Evaluates whether a retrieved chunk is current or obsolete via a cost-aware hierarchy:
Tier 1: Canonical URI & release metadata check (Zero compute)
Tier 2: Fast heuristic string / hash diffing (Low compute)
Tier 3: Semantic LLM Arbiter (Conditional, high compute)
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple

@dataclass
class DocumentChunk:
    doc_id: str
    canonical_uri: str
    version: str
    release_date: str
    content: str
    is_latest: bool
    similarity_score: float

class CascadeController:
    def __init__(self, version_catalog: Dict[str, Dict[str, Any]]):
        """
        version_catalog: Map of canonical_uri -> {latest_version, latest_release_date, latest_chunk}
        """
        self.version_catalog = version_catalog

    def verify_and_repair(self, chunk: DocumentChunk) -> Tuple[DocumentChunk, str, str]:
        """
        Runs the cascade:
        Returns (repaired_or_original_chunk, tier_used, status_message)
        """
        uri = chunk.canonical_uri
        catalog_entry = self.version_catalog.get(uri)

        if not catalog_entry:
            # Cannot verify without catalog metadata
            return chunk, "Tier 0 (Unindexed)", "No version catalog found for URI."

        # Tier 1: Zero-Cost Release Metadata / Version Tag Check
        latest_ver = catalog_entry.get("latest_version")
        if chunk.version == latest_ver:
            return chunk, "Tier 1 (Metadata)", f"Chunk is authoritative ({chunk.version}). No repair needed."
        
        # Newer version exists in catalog!
        # Tier 2: Heuristic / Text Diff Check
        latest_chunk_content = catalog_entry.get("latest_chunk_content", "")
        if chunk.content == latest_chunk_content:
            # Text didn't change despite version bump
            return chunk, "Tier 2 (Heuristic Diff)", "Version differs but textual content identical. No repair needed."

        # Content has diverged between versions -> Repair needed!
        repaired_chunk = DocumentChunk(
            doc_id=f"{uri}_{latest_ver}",
            canonical_uri=uri,
            version=latest_ver,
            release_date=catalog_entry.get("latest_release_date", "current"),
            content=latest_chunk_content,
            is_latest=True,
            similarity_score=chunk.similarity_score
        )
        return repaired_chunk, "Tier 2 (Diff & Repair)", f"Stale chunk ({chunk.version}) repaired to latest version ({latest_ver})."
