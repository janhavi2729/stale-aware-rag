import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def build_docx():
    doc = docx.Document()
    
    # Set page margins to 0.5 in
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.4)
        section.bottom_margin = Inches(0.4)
        section.left_margin = Inches(0.45)
        section.right_margin = Inches(0.45)

    # Styles
    # Title
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(1)
    run_title = p_title.add_run("Stale-Aware RAG over Versioned Documents")
    run_title.font.name = "Arial"
    run_title.font.size = Pt(15)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(15, 23, 42)

    # Subtitle
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(2)
    run_sub = p_sub.add_run("FIRST DELIVERABLE: THE 'WHY' AND 'WHAT' OF THE SOLUTION")
    run_sub.font.name = "Arial"
    run_sub.font.size = Pt(9)
    run_sub.font.bold = True
    run_sub.font.color.rgb = RGBColor(37, 99, 235)

    # Metadata
    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_before = Pt(0)
    p_meta.paragraph_format.space_after = Pt(4)
    run_meta = p_meta.add_run("B.Tech CSE (AI & ML) — Semester V Mini Project | Team: Kaustubh Akash, Janhavi Rajpurohit, Kasissnu Ssinha, Chris John Paul")
    run_meta.font.name = "Arial"
    run_meta.font.size = Pt(8.5)
    run_meta.font.color.rgb = RGBColor(71, 85, 105)

    # Divider line
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_before = Pt(0)
    p_div.paragraph_format.space_after = Pt(3)
    r_div = p_div.add_run("―" * 78)
    r_div.font.size = Pt(7)
    r_div.font.color.rgb = RGBColor(203, 213, 225)

    # Heading 1
    p_h1 = doc.add_paragraph()
    p_h1.paragraph_format.space_before = Pt(2)
    p_h1.paragraph_format.space_after = Pt(2)
    r_h1 = p_h1.add_run("1. THE 'WHY' — Problem Definition, Real-World Impact & Literature Gap")
    r_h1.font.name = "Arial"
    r_h1.font.size = Pt(10)
    r_h1.font.bold = True
    r_h1.font.color.rgb = RGBColor(30, 41, 59)

    # Body 1
    p_b1 = doc.add_paragraph()
    p_b1.paragraph_format.space_before = Pt(0)
    p_b1.paragraph_format.space_after = Pt(3)
    p_b1.paragraph_format.line_spacing = 1.05
    r_b1 = p_b1.add_run(
        "Standard Retrieval-Augmented Generation (RAG) relies on dense bi-encoder embeddings to retrieve top-k semantically relevant passages. "
        "However, dense vector similarity evaluates topical overlap, not temporal currency. In real-world technical documentation, legal codes, "
        "and product manuals, documents undergo continuous revisions. Newer and older versions often share near-identical phrasing, structure, "
        "and vocabulary. Consequently, outdated historical chunks (v_old) frequently score higher cosine similarity than updated chunks (v_new), "
        "causing the generator to emit fluent, confident, but factually obsolete answers silently."
    )
    r_b1.font.name = "Arial"
    r_b1.font.size = Pt(8)
    r_b1.font.color.rgb = RGBColor(51, 65, 85)

    # Callout table
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F8FAFC")
    p_cell = cell.paragraphs[0]
    p_cell.paragraph_format.space_before = Pt(2)
    p_cell.paragraph_format.space_after = Pt(2)
    p_cell.paragraph_format.line_spacing = 1.05
    r_c = p_cell.add_run(
        "Illustrative Failure Case:\n"
        "• Query: 'What is the return window for this product today?'\n"
        "• Retrieved (v1, 2023): 'Returns accepted within 30 days.' [Similarity: 0.92] (Stale, retrieved)\n"
        "• Authoritative (v3, 2026): 'Returns accepted within 7 days.' [Similarity: 0.89] (Current, missed)\n"
        "• Model Output: 'Returns are accepted within 30 days.' (Silent failure: high fluency, obsolete fact)"
    )
    r_c.font.name = "Arial"
    r_c.font.size = Pt(7.5)
    r_c.font.italic = True
    r_c.font.color.rgb = RGBColor(15, 23, 42)

    # Gap text
    p_gap = doc.add_paragraph()
    p_gap.paragraph_format.space_before = Pt(3)
    p_gap.paragraph_format.space_after = Pt(4)
    p_gap.paragraph_format.line_spacing = 1.05
    r_gap = p_gap.add_run(
        "Research Gap: Existing benchmarks like STALE (arXiv:2605.06527) expose temporal memory conflict but offer no retrieval-time repair. "
        "REBASE (ACM 2026) repairs GUI agents but is not applicable to text RAG. RAG-on-a-Diet (ACL 2026) budgets tokens for answer generation "
        "rather than temporal currency verification. No lightweight, cost-aware currency check-and-repair pipeline exists for document RAG."
    )
    r_gap.font.name = "Arial"
    r_gap.font.size = Pt(8)
    r_gap.font.color.rgb = RGBColor(51, 65, 85)

    # Heading 2
    p_h2 = doc.add_paragraph()
    p_h2.paragraph_format.space_before = Pt(2)
    p_h2.paragraph_format.space_after = Pt(2)
    r_h2 = p_h2.add_run("2. THE 'WHAT' — Proposed Solution Architecture & Cascade Methodology")
    r_h2.font.name = "Arial"
    r_h2.font.size = Pt(10)
    r_h2.font.bold = True
    r_h2.font.color.rgb = RGBColor(30, 41, 59)

    # Pipeline description
    p_pipe = doc.add_paragraph()
    p_pipe.paragraph_format.space_before = Pt(0)
    p_pipe.paragraph_format.space_after = Pt(3)
    p_pipe.paragraph_format.line_spacing = 1.05
    r_pipe = p_pipe.add_run(
        "We introduce Stale-Aware RAG, an augmented pipeline that intercepts retrieved passages, detects temporal staleness through an adaptive "
        "verification cascade, and hot-swaps stale chunks with their current authoritative versions prior to LLM generation:\n"
        "1. Retrieve: Dense bi-encoder retrieves top-k chunks from versioned vector index.\n"
        "2. Check (Cascade): Dynamic controller selects the cheapest sufficient verification tier.\n"
        "3. Detect: Evaluates whether a newer version of the chunk exists via URI, timestamp, or semantic diff.\n"
        "4. Repair: Swaps outdated chunks for their latest counterpart, maintaining context recall.\n"
        "5. Answer: Generation LLM constructs the final answer exclusively from fresh, validated context."
    )
    r_pipe.font.name = "Arial"
    r_pipe.font.size = Pt(8)
    r_pipe.font.color.rgb = RGBColor(51, 65, 85)

    # Key innovations
    p_inno = doc.add_paragraph()
    p_inno.paragraph_format.space_before = Pt(0)
    p_inno.paragraph_format.space_after = Pt(3)
    p_inno.paragraph_format.line_spacing = 1.05
    r_inno = p_inno.add_run(
        "Cost-Aware Cascade Tiers: Tier 1 (Zero-Cost): Canonical URI & release metadata check. "
        "Tier 2 (Low-Cost): Section diff & hash comparison. "
        "Tier 3 (High-Fidelity): Micro-LLM arbiter for ambiguous cross-version conflicts."
    )
    r_inno.font.name = "Arial"
    r_inno.font.size = Pt(8)
    r_inno.font.color.rgb = RGBColor(51, 65, 85)

    # Heading 3
    p_h3 = doc.add_paragraph()
    p_h3.paragraph_format.space_before = Pt(2)
    p_h3.paragraph_format.space_after = Pt(2)
    r_h3 = p_h3.add_run("3. EVALUATION PLAN, DATASETS & FEASIBILITY")
    r_h3.font.name = "Arial"
    r_h3.font.size = Pt(10)
    r_h3.font.bold = True
    r_h3.font.color.rgb = RGBColor(30, 41, 59)

    # Eval text
    p_ev = doc.add_paragraph()
    p_ev.paragraph_format.space_before = Pt(0)
    p_ev.paragraph_format.space_after = Pt(0)
    p_ev.paragraph_format.line_spacing = 1.05
    r_ev = p_ev.add_run(
        "• Baselines: System A (Plain RAG), System B (Naive Recency Filter), System C (Always Full LLM Check), System D (Our Cascade Check).\n"
        "• Datasets: Python Docs, Kubernetes Docs, Wikipedia Revisions, and STALE Benchmark (all with authentic version shifts).\n"
        "• Target Metrics: Answer Accuracy vs. Verification Compute Cost (token & latency Pareto frontier).\n"
        "• Feasibility & Stack: 3-week execution plan utilizing open-weight LLMs (7-8B 4-bit), FAISS/Chroma, and Python RAG pipeline."
    )
    r_ev.font.name = "Arial"
    r_ev.font.size = Pt(8)
    r_ev.font.color.rgb = RGBColor(51, 65, 85)

    docx_path = r"C:\Users\dhanv\.gemini\antigravity\scratch\stale-aware-rag\First_Deliverable_One_Pager.docx"
    doc.save(docx_path)
    print("DOCX build complete.")

if __name__ == "__main__":
    build_docx()
