# IEEE Format Mini Project Report Outline (10 Pages)

**Project Title:** Stale-Aware RAG: Cost-Efficient Temporal Currency Verification and Context Repair over Versioned Document Corpora  
**Target Format:** Two-Column IEEE Conference / Transactions Template (10 Pages)  
**Authors:** Kaustubh Akash, Janhavi Rajpurohit, Kasissnu Ssinha, Chris John Paul  

---

## Page-by-Page Structure Breakdown

### Page 1: Title, Authors, Abstract & Introduction
* **Abstract (150–250 words):** Problem of silent temporal obsolescence in dense RAG, proposed multi-tier cascade, empirical results showing $>90\%$ staleness detection at $60\%$ cost reduction.
* **Keywords:** Retrieval-Augmented Generation (RAG), Document Versioning, Temporal Validity, Adaptive Cascade, Dense Bi-encoders.
* **Section I: Introduction**
  * Proliferation of dynamic knowledge corpora.
  * The fundamental limitation: semantic similarity $\neq$ temporal validity.
  * Illustrative case study.
  * Contributions summary (formal problem, cascade architecture, benchmark dataset).

### Page 2: Related Work & Background Study
* **Section II: Related Work**
  * II-A: Dense Retrieval & Semantic Overlap in RAG.
  * II-B: Temporal Knowledge & Memory Benchmarks (STALE, Beyond Prompts).
  * II-C: Agentic Verification & Dynamic Compute (REBASE, RAG-on-a-Diet).
  * Table I: Comparative Analysis of Related Work vs. Proposed Stale-Aware RAG.

### Page 3: Problem Formulation & Architecture Overview
* **Section III: Problem Formulation**
  * Mathematical model of versioned document space $\mathcal{D} = \{(t_i, v_i, \tau_i, u_i)\}$.
  * Formalization of silent retrieval error.
  * Objective function: maximize factual correctness while minimizing verification compute.
* **Section IV: System Architecture**
  * End-to-end pipeline diagram.
  * Retrieval module and versioned metadata store.

### Page 4–5: The Adaptive Verification Cascade & Repair Operator
* **Section IV-B: The Multi-Tier Verification Cascade**
  * Tier 1 (Zero-Cost / Metadata): Canonical URI match & release timeline lookup.
  * Tier 2 (Low-Cost / Heuristic Diff): Fast section-level hash & string diffing.
  * Tier 3 (High-Fidelity / Micro-LLM): Prompt design and disambiguation logic.
  * Algorithm 1: Dynamic Cascade Controller Decision Flow.
* **Section IV-C: Context Repair Operator**
  * Recall preservation via hot-swapping vs. naive chunk dropping.
  * Handling multi-version queries (comparative vs. authoritative).

### Page 6–7: Experimental Setup & Datasets
* **Section V: Experimental Setup**
  * V-A: Versioned Datasets (Python Docs, Kubernetes Docs, Wikipedia Revisions, STALE Benchmark).
  * V-B: Question-Answer Generation & Ground-Truth Annotation Protocol.
  * V-C: Baseline Systems (Plain RAG, Recency Filter, Full LLM Check).
  * V-D: Evaluation Metrics (Accuracy, Currency Detection F1, Latency, Token Cost).

### Page 8: Results & Performance Analysis
* **Section VI: Results & Discussion**
  * Table II: Overall Accuracy and Staleness Repair Rate across Datasets.
  * Figure 1: Accuracy vs. Per-Query Verification Cost (Pareto Frontier).
  * Figure 2: Latency Distribution across Cascade Tiers.
  * Analysis of when Tier 1 succeeds vs. when Tier 3 is triggered.

### Page 9: Ablation Studies, Error Analysis & Limitations
* **Section VII: Ablations & Error Analysis**
  * Impact of each tier in the cascade (Tier 1 only vs. Tier 1+2 vs. Full).
  * Failure cases: Ambiguous semantic shifts, unlabelled document forks.
* **Section VIII: Boundary Conditions & Scope Limitations**
  * Handling non-versioned corpora, multimodal constraints.

### Page 10: Conclusion, Future Work & References
* **Section IX: Conclusion**
  * Summary of findings and feasibility.
  * Recommendations for enterprise RAG deployment.
* **Section X: Future Work**
  * Extension to streaming documents and decentralized knowledge bases.
* **References (20–30 peer-reviewed papers in standard IEEE citation format).**
