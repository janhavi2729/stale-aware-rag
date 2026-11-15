# Demo Instructions & Live Demonstration Guidelines

**Course:** B.Tech. CSE (AI & ML) — Semester V Mini Project  
**Project:** Stale-Aware RAG over Versioned Documents  
**Format:** Live interactive demonstration of working application (No slide/paper presentation required during demo).

---

## 1. Demo Objectives & Scoring Criteria

During the live evaluation, the panel will assess:
1. **Working Application:** A live, interactive interface demonstrating the problem and your solution in real time.
2. **Side-by-Side Comparison:** Clear visual proof that Plain RAG fails on a version-shifted query, while Stale-Aware RAG detects the staleness and retrieves the current authoritative fact.
3. **Execution Transparency:** Showing the cascade tiers at work (Tier 1 Metadata vs. Tier 2 Diff vs. Tier 3 LLM check), along with latency and token cost metrics.
4. **Codebase & Documentation:** Verified GitHub repository with all documentation (`README.md`, `FIRST_DELIVERABLE.md`, `PROBLEM_STATEMENT.md`, and 10-page IEEE Report).

---

## 2. Recommended Live Demo Architecture (Streamlit / Gradio)

Build a clean dual-pane UI:
- **Left Panel:** Query input + Dropdown of preset benchmark queries (e.g., Python 3.12 deprecated features, Kubernetes v1.28 API changes, E-Commerce Return Policy change).
- **Center Panel (Plain RAG):**
  - Shows retrieved chunk (e.g., $v_1$, 2023).
  - Shows generated answer (*Incorrect / Stale*).
  - Shows high confidence / high similarity score.
- **Right Panel (Stale-Aware RAG - Ours):**
  - Shows original retrieved chunk + alert: `[STALE DETECTED by Cascade Tier 1/2]`.
  - Shows swapped chunk ($v_3$, 2026).
  - Shows generated answer (*Correct / Current*).
  - Metrics banner: Checks executed, latency (ms), token savings vs. full check.

---

## 3. Demo Walkthrough Script (5–7 Minutes)

1. **Minute 0–1: Problem Demonstration**
   - Type query: *"What is the return window for this product today?"*
   - Trigger Plain RAG. Show the panel that outputs *"Returns accepted within 30 days"* from an old 2023 policy document.
   - Explain: *"Notice how fluent and confident the answer is, despite being 100% obsolete."*
2. **Minute 2–4: Solution & Cascade Execution**
   - Run the same query on Stale-Aware RAG.
   - Point out the Cascade Controller logs:
     - Tier 1: Canonical URI check triggers $\rightarrow$ Newer version $v_3$ detected in corpus.
     - Repair module hot-swaps the chunk.
     - LLM answers *"Returns accepted within 7 days."*
3. **Minute 5–6: Edge Cases & Tradeoff Plot**
   - Show a non-stale query (where Tier 1 immediately approves with zero overhead).
   - Display the Pareto frontier graph: Factual Accuracy vs. Verification Cost.
4. **Minute 7: Q&A with Evaluators**
   - Answer panel questions referencing GitHub code, commit history, and test logs.
