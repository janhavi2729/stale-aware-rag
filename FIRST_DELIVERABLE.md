# First Deliverable: Project Overview — The "Why" and "What"

**Project Title:** Stale-Aware RAG over Versioned Documents  
**Academic Context:** B.Tech. in CSE (AI & ML) — Semester V Mini Project  
**Team Members:** Kaustubh Akash, Janhavi Rajpurohit, Kasissnu Ssinha, Chris John Paul  

---

### Part 1: The "WHY" — Problem, Gap, and Motivation

Standard Retrieval-Augmented Generation (RAG) relies on dense vector bi-encoders to identify the top-$k$ most semantically relevant text passages. However, dense vector similarity measures **topical closeness, not temporal currency**. 

In real-world corpora (such as API manuals, legal statutes, and product policies), documentation undergoes continual versioning. Because revisions of a document preserve substantially identical syntax and phrasing, historical versions ($v_{\text{old}}$) and current versions ($v_{\text{new}}$) map to almost identical points in embedding space. In practice, stale passages routinely outscore newer passages due to minor lexical matches.

* **The Silent Failure:** When asked *"What is the return window for this product today?"*, plain RAG may retrieve a 2023 policy chunk stating *"Returns accepted within 30 days"* over a 2026 update stating *"Returns accepted within 7 days"*. The generator outputs a fluent, authoritative, and factually obsolete answer without alerting the user or raising any retrieval anomaly.
* **Literature Gap:** While recent benchmarks (e.g., STALE, arXiv:2605.06527) expose temporal memory conflict in conversational agents, they offer no retrieval-time repair. Conversely, GUI-repair frameworks (REBASE, ACM 2026) are restricted to UI states, and computational budgeting frameworks (RAG-on-a-Diet, ACL 2026) allocate tokens for answer generation rather than temporal currency verification. **No lightweight, cost-aware currency checking and repair mechanism exists for document-level RAG.**

---

### Part 2: The "WHAT" — Proposed Solution and Methodology

We introduce **Stale-Aware RAG**, an augmented retrieval pipeline that intercepts retrieved passages, detects temporal obsolescence through an adaptive verification cascade, and swaps stale chunks with their authoritative revisions before context is passed to the language model.

```
[1. RETRIEVE]       Top-k candidate chunks fetched via dense embedding similarity
      ↓
[2. CHECK]          Cascade Controller chooses the cheapest sufficient verification tier
      ↓
[3. DETECT]         Determine if a newer document revision exists (URI, hash, or semantic diff)
      ↓
[4. REPAIR]         Hot-swap stale chunks with their latest authoritative versions
      ↓
[5. ANSWER]         Generator LLM produces answers strictly from verified, fresh context
```

#### Key Technical Contributions:
1. **Adaptive Multi-Tier Verification Cascade:**  
   Brute-force verification using an LLM on every retrieved chunk introduces latency and compute overhead. Our cascade stops at the earliest conclusive tier:
   * *Tier 1 (Zero-Cost / Metadata):* Canonical document URI match + release timestamp lookup.
   * *Tier 2 (Low-Cost / Heuristic Diff):* Fast section-level diffing to detect semantic alterations.
   * *Tier 3 (High-Fidelity / LLM Arbiter):* Micro-LLM verification invoked only when cross-version semantics remain ambiguous.
2. **Context Repair Operator:**  
   Instead of dropping stale chunks and degrading recall, the system queries the version index by canonical entity URI and substitutes the obsolete chunk with its corresponding latest counterpart.
3. **Four-System Empirical Benchmark:**  
   Evaluated across four real-world datasets exhibiting version shifts (Python Docs, Kubernetes Docs, Wikipedia Revisions, and STALE) across four comparative baselines:
   * **System A (Plain RAG):** Standard dense vector similarity ranking.
   * **System B (Recency Filter):** Naive chronological filter (prioritizing timestamp alone).
   * **System C (Always Full Check):** Full LLM verification on all retrieved chunks (upper bound accuracy, high cost).
   * **System D (Our Cascade):** Cost-aware dynamic cascade optimizing the Pareto frontier of accuracy vs. latency/token cost.
