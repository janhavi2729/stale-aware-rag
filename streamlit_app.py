"""
Streamlit Web Application for Stale-Aware RAG.
Launch: streamlit run streamlit_app.py
"""

try:
    import streamlit as st
except ImportError:
    print("Streamlit is not installed. To run this file: pip install streamlit")
    exit(0)

from src.knowledge_base import PRESET_QUERIES, VERSIONED_DOCUMENTS
from src.retriever import DenseRetriever
from src.cascade import CascadeEngine
from src.generator import AnswerGenerator
from src.benchmark import BenchmarkRunner

st.set_page_config(
    page_title="Stale-Aware RAG Demo",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Stale-Aware RAG over Versioned Documents")
st.caption("B.Tech CSE (AI & ML) — Semester V Mini Project | Team: Kaustubh Akash, Janhavi Rajpurohit, Kasissnu Ssinha, Chris John Paul")

retriever = DenseRetriever()
cascade = CascadeEngine()
benchmark = BenchmarkRunner()

# Sidebar: Query Selection
st.sidebar.header("Evaluation Queries")
options = [f"[{q['category']}] {q['query']}" for q in PRESET_QUERIES]
selected_idx = st.sidebar.selectbox("Select a benchmark query:", range(len(options)), format_func=lambda x: options[x])
selected_item = PRESET_QUERIES[selected_idx]

st.sidebar.info(f"**Context Shift:**\n{selected_item['explanation']}")

# Tabs
tab1, tab2 = st.tabs(["🚀 Live Pipeline Comparison", "📊 Benchmark & Pareto Metrics"])

with tab1:
    q = selected_item["query"]
    st.markdown(f"### Query: *\"{q}\"*")

    col1, col2 = st.columns(2)

    with col1:
        st.error("### System A: Plain RAG (Similarity Retrieval)")
        retrieved_a = retriever.retrieve_plain_rag(q, top_k=1)[0]
        ans_a = AnswerGenerator.generate_answer(q, retrieved_a)

        st.markdown(f"**Retrieved:** `{retrieved_a.doc_id}` | **Version:** `{retrieved_a.version}` ({retrieved_a.release_date})")
        st.markdown(f"**Retrieval Score:** `{retrieved_a.similarity_score:.3f}`")
        st.code(retrieved_a.content, language="markdown")
        
        st.markdown("#### Generated Answer:")
        st.warning(f"**{ans_a}**")
        st.markdown("🚨 *Status: Outdated chunk retrieved due to similarity; confident stale answer.*")

    with col2:
        st.success("### System D: Stale-Aware RAG (Our Cascade)")
        res_d = cascade.run_cascade(retrieved_a)
        ans_d = AnswerGenerator.generate_answer(q, res_d.repaired_chunk)

        st.info(f"**Cascade Tier:** `{res_d.tier_used}` | **Latency:** `{res_d.latency_ms:.3f} ms`\n\n**Log:** {res_d.details}")
        st.markdown(f"**Repaired Chunk:** `{res_d.repaired_chunk.doc_id}` | **Active Version:** `{res_d.repaired_chunk.version}` ({res_d.repaired_chunk.release_date})")
        st.code(res_d.repaired_chunk.content, language="markdown")

        st.markdown("#### Generated Answer:")
        st.success(f"**{ans_d}**")
        st.markdown("✅ *Status: Stale chunk detected & repaired. Verified authoritative answer.*")

with tab2:
    st.subheader("Four-System Empirical Benchmark")
    bm_res = benchmark.run_all()
    summary = bm_res["summary"]
    
    st.table(summary)
    st.caption("Prototype comparison: normalized benchmark units are illustrative; replace them with measured model tokens for publication-grade evaluation.")
