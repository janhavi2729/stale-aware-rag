import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_footer(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        footer_text = f"Deliverable 1: Problem Statement & Solution Overview | Page {self._pageNumber} of {page_count}"
        self.drawRightString(8.5 * inch - 36, 20, footer_text)
        self.drawString(36, 20, "B.Tech CSE (AI & ML) | Sem V Mini Project")
        self.restoreState()

def build_pdf():
    pdf_path = r"C:\Users\dhanv\.gemini\antigravity\scratch\stale-aware-rag\First_Deliverable_One_Pager.pdf"
    
    # 0.45 in margins (32.4 pt)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=32,
        rightMargin=32,
        topMargin=26,
        bottomMargin=32
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=17,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=2
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#2563EB')
    )

    team_style = ParagraphStyle(
        'TeamText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#475569')
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=4,
        spaceAfter=2
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.2,
        textColor=colors.HexColor('#334155'),
        alignment=4 # Justified
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.8,
        leading=9.8,
        textColor=colors.HexColor('#1E293B')
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.8,
        leading=10,
        textColor=colors.HexColor('#0F172A')
    )

    story = []

    # Title & Header
    story.append(Paragraph("Stale-Aware RAG over Versioned Documents", title_style))
    story.append(Paragraph("FIRST DELIVERABLE: THE 'WHY' AND 'WHAT' OF THE SOLUTION", subtitle_style))
    story.append(Spacer(1, 2))
    
    # Team & Meta row
    meta_text = "<b>Program:</b> B.Tech CSE (AI & ML) — Semester V | <b>Team:</b> Kaustubh Akash, Janhavi Rajpurohit, Kasissnu Ssinha, Chris John Paul"
    story.append(Paragraph(meta_text, team_style))
    story.append(Spacer(1, 3))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=4, spaceBefore=1))

    # SECTION 1: THE WHY
    story.append(Paragraph("1. THE 'WHY' — Problem Statement, Motivation & Research Gap", h2_style))
    
    why_text = (
        "Standard Retrieval-Augmented Generation (RAG) relies on dense bi-encoder embeddings to fetch top-<i>k</i> "
        "semantically relevant passages. However, dense vector similarity evaluates <b>topical overlap, not temporal currency</b>. "
        "In rapidly evolving technical, legal, and operational corpora (e.g., Python, Kubernetes, API docs), newer and older "
        "revisions share near-identical phrasing, vocabulary, and structure. Consequently, obsolete historical passages (<i>v</i><sub>old</sub>) "
        "routinely score higher cosine similarity than updated passages (<i>v</i><sub>new</sub>), causing the generator to output "
        "<b>fluent, confident, yet factually wrong and stale answers silently</b>."
    )
    story.append(Paragraph(why_text, body_style))
    story.append(Spacer(1, 3))

    # Illustrative Box
    box_data = [
        [
            Paragraph("<b>Illustrative Failure:</b><br/>"
                      "<b>User Query:</b> <i>'What is the return window for this product today?'</i><br/>"
                      "• <b>Retrieved Chunk (v1, 2023):</b> 'Returns accepted within 30 days.' [Cos Sim: 0.92] (Stale, retrieved)<br/>"
                      "• <b>Actual Policy (v3, 2026):</b> 'Returns accepted within 7 days.' [Cos Sim: 0.89] (Current, missed)<br/>"
                      "• <b>RAG Answer:</b> 'Returns are accepted within 30 days.' <i>(Silent failure: high fluency, obsolete truth)</i>", callout_style)
        ]
    ]
    t_box = Table(box_data, colWidths=[546])
    t_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.75, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 4),
        ('LINELEFT', (0,0), (-1,-1), 2.5, colors.HexColor('#EF4444')),
    ]))
    story.append(t_box)
    story.append(Spacer(1, 3))

    lit_text = (
        "<b>Literature Gap:</b> While memory benchmarks (e.g., STALE, 2026) expose that agents fail to identify outdated facts, "
        "they provide no retrieval-time repair. GUI-repair tools (REBASE, 2026) address interface actions rather than text RAG. "
        "Dynamic compute approaches (RAG-on-a-Diet, ACL 2026) budget generation cost but overlook temporal verification. "
        "<i>Currently, no lightweight, cost-aware currency checking and repair framework exists for versioned RAG.</i>"
    )
    story.append(Paragraph(lit_text, body_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#E2E8F0'), spaceAfter=3, spaceBefore=1))

    # SECTION 2: THE WHAT
    story.append(Paragraph("2. THE 'WHAT' — Proposed Solution Architecture & Methodology", h2_style))
    
    what_text = (
        "We propose <b>Stale-Aware RAG</b>, an adaptive framework that intercepts retrieved chunks before LLM generation, "
        "determines whether each chunk is authoritative or obsolete via a <b>hierarchical verification cascade</b>, and "
        "repairs stale chunks by hot-swapping them with their latest revisions."
    )
    story.append(Paragraph(what_text, body_style))
    story.append(Spacer(1, 3))

    # Pipeline Steps Table
    pipeline_data = [
        [
            Paragraph("<b>1. RETRIEVE</b>", bullet_style),
            Paragraph("<b>2. CHECK (Cascade)</b>", bullet_style),
            Paragraph("<b>3. DETECT</b>", bullet_style),
            Paragraph("<b>4. REPAIR</b>", bullet_style),
            Paragraph("<b>5. ANSWER</b>", bullet_style)
        ],
        [
            Paragraph("Fetch top-<i>k</i> chunks via dense similarity.", bullet_style),
            Paragraph("Route chunk through cheapest conclusive check tier.", bullet_style),
            Paragraph("Ascertain whether a newer authoritative version exists.", bullet_style),
            Paragraph("Hot-swap stale chunk with latest canonical version.", bullet_style),
            Paragraph("Generate response from fresh, verified context.", bullet_style)
        ]
    ]
    t_pipeline = Table(pipeline_data, colWidths=[109, 110, 109, 109, 109])
    t_pipeline.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EFF6FF')),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#FFFFFF')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#93C5FD')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DBEAFE')),
        ('PADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_pipeline)
    story.append(Spacer(1, 3))

    # Key Mechanisms
    mech_text = (
        "<b>Core Innovations:</b><br/>"
        "• <b>Adaptive Verification Cascade:</b> Rather than running an expensive LLM verifier on every chunk, the cascade stops "
        "at the cheapest conclusive stage: <i>Tier 1 (Zero-Cost):</i> Release metadata/URI timestamp lookup → <i>Tier 2 (Low-Cost):</i> "
        "Fuzzy section diffing → <i>Tier 3 (High-Fidelity):</i> Micro-LLM semantic reconciliation only if ambiguity remains.<br/>"
        "• <b>Recall-Preserving Repair:</b> Instead of naive filtering (which discards relevant content and hurts recall), the system queries "
        "the document release index by URI and substitutes the stale text with its current version."
    )
    story.append(Paragraph(mech_text, body_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#E2E8F0'), spaceAfter=3, spaceBefore=1))

    # SECTION 3: EVALUATION & SCOPE
    story.append(Paragraph("3. EVALUATION PLAN, SCOPE & EXPECTED IMPACT", h2_style))
    
    eval_text = (
        "<b>Evaluation Framework:</b> We evaluate on version-shifting datasets: <b>Python Docs</b>, <b>Kubernetes Docs</b>, "
        "<b>Wikipedia Revisions</b>, and <b>STALE</b> across 4 comparative systems:<br/>"
        "• <b>System A (Plain RAG):</b> Dense similarity only (prone to silent staleness).<br/>"
        "• <b>System B (Recency Filter):</b> Timestamp filter only (discards valuable older unrevised docs).<br/>"
        "• <b>System C (Always Full Check):</b> Full LLM verification on all chunks (high accuracy, high token cost).<br/>"
        "• <b>System D (Our Cascade):</b> Cost-aware dynamic cascade aiming to match System C's accuracy at a fraction of its compute."
    )
    story.append(Paragraph(eval_text, body_style))
    story.append(Spacer(1, 3))

    scope_data = [
        [
            Paragraph("<b>In Scope:</b> Versioned technical text, modular RAG, currency detection & repair, small open LLM (7-8B).", bullet_style),
            Paragraph("<b>Feasibility & Timeline:</b> 3-week plan: W1 (Baselines & Corpus) → W2 (Detector & Repair) → W3 (Cascade & Report).", bullet_style)
        ]
    ]
    t_scope = Table(scope_data, colWidths=[273, 273])
    t_scope.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0,0), (-1,-1), 3),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_scope)

    doc.build(story, canvasmaker=NumberedCanvas)
    print("PDF build complete.")

if __name__ == '__main__':
    build_pdf()
