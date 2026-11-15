# Problem Statement: Stale-Aware Retrieval-Augmented Generation (RAG) over Versioned Documents

**Academic Program:** B.Tech. in Computer Science & Engineering (AI & ML) — Semester V  
**Project Track:** Mini Project / Capstone Stage 1  
**Project Title:** Stale-Aware RAG over Versioned Documents  
**Project Team:**  
- Kaustubh Akash  
- Janhavi Rajpurohit  
- Kasissnu Ssinha  
- Chris John Paul  

---

## 1. Problem Context and Motivation

Standard Retrieval-Augmented Generation (RAG) frameworks rely on dense vector embeddings (e.g., bi-encoders) to retrieve the top-$k$ most semantically relevant text passages from an external corpus. In production software ecosystems, legal frameworks, and technical documentation (e.g., Python, Kubernetes, API specs), corpora are inherently dynamic and continuously versioned. 

Dense semantic similarity algorithms evaluate *semantic relevance*, but are intrinsically agnostic to *temporal validity* and *version precedence*. When multiple versions of an evolving document exist in the corpus:
1. Historical and current passages often share near-identical phrasing, vocabulary, and structural layout.
2. Older text chunks frequently yield equal or higher cosine similarity scores compared to newer revisions.
3. Consequently, traditional retrieval pipelines silently retrieve outdated passages ($v_{\text{old}}$) instead of the latest authoritative versions ($v_{\text{current}}$).

### Illustrative Failure Case
Consider an automated customer support or API documentation assistant queried with:
> **User Query:** *"What is the return window for this product today?"*  
> **Retrieved Chunk ($v_1$, 2023):** *"Returns accepted within 30 days."* (Cosine similarity: 0.91)  
> **Authoritative Chunk ($v_3$, 2026):** *"Returns accepted within 7 days."* (Cosine similarity: 0.89)  
> **Model Output:** *"Returns are accepted within 30 days."*  

The model responds **fluently, confidently, and completely out of date**. Because semantic similarity measures topical overlap rather than temporal currency, plain RAG fails silently without raising retrieval exceptions.

---

## 2. Formal Problem Definition

Let $\mathcal{D} = \{d_1, d_2, \dots, d_N\}$ represent a versioned corpus where each document chunk $d_i$ is a tuple $(t_i, v_i, \tau_i, u_i)$ consisting of text content $t_i$, version identifier $v_i$, timestamp $\tau_i$, and canonical entity/document URI $u_i$.

Given a user query $q$, standard dense retrieval computes:
$$\mathcal{R}_{\text{top-}k}(q) = \operatorname{arg\,top-}k_{d \in \mathcal{D}} \cos(\mathbf{e}_q, \mathbf{e}_d)$$

where $\mathbf{e}_q$ and $\mathbf{e}_d$ are dense vector embeddings.

The objective of **Stale-Aware RAG** is to define a verification and repair operator $\mathcal{T}_{\text{currency}}$ such that for any retrieved passage $d_{\text{ret}} \in \mathcal{R}_{\text{top-}k}(q)$:
1. **Detection:** Determine whether $\exists\, d' \in \mathcal{D}$ such that $u_{d'} = u_{d_{\text{ret}}}$ and $\tau_{d'} > \tau_{d_{\text{ret}}}$ where factual divergence $\Delta(t_{d_{\text{ret}}}, t_{d'}) \neq \emptyset$.
2. **Adaptive Cascade:** Execute the minimum-cost verification step $c \in \{c_{\text{meta}}, c_{\text{diff}}, c_{\text{LLM}}\}$ necessary to confirm or refute staleness.
3. **Repair:** If $d_{\text{ret}}$ is stale, replace $d_{\text{ret}}$ with $d_{\text{current}}$ prior to context injection into the generation LLM.

---

## 3. Project Scope and Boundary Conditions

| Dimension | In Scope | Outside the Boundary |
|---|---|---|
| **Data Modality** | Versioned structured & semi-structured technical text (Markdown, HTML, Docs) | Multimodal content (images, audio, video) |
| **Failure Modes** | Temporal staleness caused by document evolution | Adversarial poisoning, hallucinations, unrelated noise |
| **Pipeline Architecture** | Modular RAG pipeline (Retrieval $\rightarrow$ Currency Check $\rightarrow$ Repair $\rightarrow$ Generation) | Pre-training or fine-tuning foundation LLMs from scratch |
| **Compute Constraints** | Quantized open-weight models (7B-8B parameter class, 4-bit) / standard APIs | Large-scale multi-node cluster training |

---

## 4. Key Research & Engineering Challenges

1. **High Semantic Overlap Between Versions:**  
   Newer and older revisions often differ by only a few tokens (e.g., deprecation flags, numeric thresholds). Standard embeddings cannot discriminate these micro-variations.
2. **Verification Latency & Cost Tradeoff:**  
   Invoking an LLM to verify every single retrieved chunk introduces prohibitive inference costs and latency. The system requires an adaptive cascade that terminates at the cheapest sufficient check.
3. **Ambiguity and Cross-Version Queries:**  
   Queries that explicitly ask for version comparisons (e.g., *"How did the return window change between 2023 and 2026?"*) require historical multi-version context rather than automated overwrites.

---

## 5. Objectives & Deliverable Success Metrics

- **Currency Accuracy:** $>90\%$ correct identification and automated repair of stale retrieved chunks across benchmark datasets (Python Docs, Kubernetes Docs, Wikipedia Revisions, STALE).
- **Cost Reduction via Cascade:** Achieve $\ge 60\%$ reduction in verification token cost compared to a brute-force LLM-based verification baseline.
- **Answer Correctness:** Statistically significant improvement in factual answer accuracy on temporal QA benchmarks relative to naive dense RAG.
