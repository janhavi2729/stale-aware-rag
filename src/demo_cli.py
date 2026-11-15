"""
Live CLI Demonstration of Stale-Aware RAG vs. Plain RAG
"""

import time
from cascade import DocumentChunk, CascadeController

def run_demo():
    print("=" * 70)
    print("  STALE-AWARE RAG: LIVE APPLICATION PROTOTYPE DEMO")
    print("  Team: Kaustubh Akash, Janhavi Rajpurohit, Kasissnu Ssinha, Chris John Paul")
    print("=" * 70)

    # 1. Setup Version Catalog (Ground Truth Knowledge Base)
    version_catalog = {
        "policy://ecommerce/returns": {
            "latest_version": "v3",
            "latest_release_date": "2026-01-15",
            "latest_chunk_content": "Returns accepted within 7 days with valid receipt."
        }
    }

    controller = CascadeController(version_catalog)

    # 2. Simulated Retrieval from Dense Vector Index
    query = "What is the return window for this product today?"
    print(f"\n[QUERY] -> '{query}'")

    # In plain RAG, the old 2023 chunk had higher similarity (e.g. 0.92 vs 0.89)
    retrieved_chunk = DocumentChunk(
        doc_id="returns_v1_chunk_1",
        canonical_uri="policy://ecommerce/returns",
        version="v1",
        release_date="2023-04-10",
        content="Returns accepted within 30 days of purchase.",
        is_latest=False,
        similarity_score=0.92
    )

    print("\n--- 1. SYSTEM A: PLAIN RAG (Standard Bi-Encoder) ---")
    print(f"Retrieved Document: {retrieved_chunk.canonical_uri} [Version: {retrieved_chunk.version}, Date: {retrieved_chunk.release_date}]")
    print(f"Dense Similarity: {retrieved_chunk.similarity_score:.2f}")
    print(f"Context Provided to LLM: \"{retrieved_chunk.content}\"")
    print("Simulated LLM Answer: 'Returns are accepted within 30 days.'")
    print(">>> STATUS: [SILENT FAILURE] Outdated fact generated with high confidence.")

    print("\n" + "-" * 70)

    # 3. System D: Stale-Aware RAG with Cascade
    print("--- 2. SYSTEM D: STALE-AWARE RAG (Our Method) ---")
    start_time = time.perf_counter()
    repaired_chunk, tier, status_msg = controller.verify_and_repair(retrieved_chunk)
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    print(f"Cascade Decision: {tier}")
    print(f"Cascade Log: {status_msg}")
    print(f"Verification Latency: {elapsed_ms:.3f} ms")
    print(f"Context Provided to LLM: \"{repaired_chunk.content}\"")
    print(f"Active Version in Prompt: {repaired_chunk.version} ({repaired_chunk.release_date})")
    print("Simulated LLM Answer: 'Returns are accepted within 7 days with valid receipt.'")
    print(">>> STATUS: [SUCCESS] Stale chunk repaired. Accurate, authoritative answer produced.")
    print("=" * 70)

if __name__ == "__main__":
    run_demo()
