"""
Curated Versioned Knowledge Base & Ground Truth Catalog
Includes realistic version shifts across:
1. E-Commerce Policies (Illustrative Example from Presentation)
2. Python Documentation (Python 3.8 vs 3.12 asyncio / typing changes)
3. Kubernetes Concepts & Tasks (extensions/v1beta1 vs networking.k8s.io/v1 Ingress)
4. Wikipedia Revisions (Factual updates over time)
5. STALE Benchmark (Conversational memory conflict)
"""

from typing import List, Dict, Any
from .models import DocumentChunk

VERSIONED_DOCUMENTS: List[DocumentChunk] = [
    # 1. E-Commerce Return Policy
    DocumentChunk(
        doc_id="policy_returns_v1",
        canonical_uri="policy://ecommerce/returns",
        title="Store Return Policy",
        dataset="E-Commerce Policies",
        version="v1",
        release_date="2023-01-10",
        content="Returns accepted within 30 days of purchase with original receipt for a full refund.",
        is_latest=False
    ),
    DocumentChunk(
        doc_id="policy_returns_v3",
        canonical_uri="policy://ecommerce/returns",
        title="Store Return Policy",
        dataset="E-Commerce Policies",
        version="v3",
        release_date="2026-01-15",
        content="Returns accepted within 7 days of purchase. Items returned after 7 days are eligible for store credit only.",
        is_latest=True
    ),

    # 2. Python Documentation (asyncio.get_event_loop deprecation)
    DocumentChunk(
        doc_id="python_asyncio_3_8",
        canonical_uri="docs://python/library/asyncio",
        title="Asyncio Event Loop Lifecycle",
        dataset="Python Docs",
        version="3.8",
        release_date="2019-10-14",
        content="Call asyncio.get_event_loop() to get the current event loop. If no loop is running in the current OS thread, a new loop is created and set as current.",
        is_latest=False
    ),
    DocumentChunk(
        doc_id="python_asyncio_3_12",
        canonical_uri="docs://python/library/asyncio",
        title="Asyncio Event Loop Lifecycle",
        dataset="Python Docs",
        version="3.12",
        release_date="2023-10-02",
        content="Deprecated since 3.10: asyncio.get_event_loop() no longer implicitly creates a new loop if none is set. Use asyncio.run() or asyncio.new_event_loop() instead.",
        is_latest=True
    ),

    # 3. Kubernetes Ingress API Migration
    DocumentChunk(
        doc_id="k8s_ingress_1_18",
        canonical_uri="docs://k8s/networking/ingress",
        title="Kubernetes Ingress Resource Specification",
        dataset="Kubernetes Docs",
        version="v1.18",
        release_date="2020-03-25",
        content="apiVersion: extensions/v1beta1\nkind: Ingress\nmetadata:\n  name: test-ingress\nspec:\n  backend:\n    serviceName: test-svc\n    servicePort: 80",
        is_latest=False
    ),
    DocumentChunk(
        doc_id="k8s_ingress_1_28",
        canonical_uri="docs://k8s/networking/ingress",
        title="Kubernetes Ingress Resource Specification",
        dataset="Kubernetes Docs",
        version="v1.28",
        release_date="2023-08-15",
        content="apiVersion: networking.k8s.io/v1\nkind: Ingress\nmetadata:\n  name: test-ingress\nspec:\n  defaultBackend:\n    service:\n      name: test-svc\n      port:\n        number: 80",
        is_latest=True
    ),

    # 4. Wikipedia Revisions: Twitter / X Branding
    DocumentChunk(
        doc_id="wiki_twitter_2022",
        canonical_uri="wiki://tech/twitter_branding",
        title="Twitter Branding and Identity",
        dataset="Wikipedia Revisions",
        version="rev-2022",
        release_date="2022-05-01",
        content="The official brand identity of the microblogging service is Twitter, and its primary logo is Larry the blue bird.",
        is_latest=False
    ),
    DocumentChunk(
        doc_id="wiki_twitter_2026",
        canonical_uri="wiki://tech/twitter_branding",
        title="Twitter Branding and Identity",
        dataset="Wikipedia Revisions",
        version="rev-2026",
        release_date="2026-02-10",
        content="Following the corporate rebranding, the platform is officially named X, operated by X Corp, and the blue bird logo was retired in favor of the stylized X glyph.",
        is_latest=True
    ),

    # 5. STALE Benchmark: Personal Workspace Fact
    DocumentChunk(
        doc_id="stale_chat_turn_14",
        canonical_uri="chat://user/residence",
        title="User Personal Profile",
        dataset="STALE Benchmark",
        version="turn_14",
        release_date="2024-03-01",
        content="The user lives in Seattle, Washington and works remotely for an e-commerce firm.",
        is_latest=False
    ),
    DocumentChunk(
        doc_id="stale_chat_turn_82",
        canonical_uri="chat://user/residence",
        title="User Personal Profile",
        dataset="STALE Benchmark",
        version="turn_82",
        release_date="2026-01-20",
        content="The user relocated from Seattle to Austin, Texas in late 2025 and founded an AI analytics startup.",
        is_latest=True
    )
]

PRESET_QUERIES = [
    {
        "id": "q1",
        "category": "E-Commerce Policies",
        "query": "What is the return window for this product today?",
        "canonical_uri": "policy://ecommerce/returns",
        "stale_expected_ans": "Returns are accepted within 30 days of purchase.",
        "fresh_expected_ans": "Returns are accepted within 7 days of purchase (store credit thereafter).",
        "explanation": "Return policy was shortened from 30 days (2023) to 7 days (2026)."
    },
    {
        "id": "q2",
        "category": "Python Docs",
        "query": "How does asyncio.get_event_loop() handle threads without a running loop?",
        "canonical_uri": "docs://python/library/asyncio",
        "stale_expected_ans": "It automatically creates a new event loop and sets it as the current loop.",
        "fresh_expected_ans": "It is deprecated and raises a RuntimeError; you must explicitly call asyncio.new_event_loop() or asyncio.run().",
        "explanation": "Implicit loop creation was deprecated in 3.10 and changed in 3.12."
    },
    {
        "id": "q3",
        "category": "Kubernetes Docs",
        "query": "What apiVersion should I declare in my YAML for a Kubernetes Ingress resource?",
        "canonical_uri": "docs://k8s/networking/ingress",
        "stale_expected_ans": "Use apiVersion: extensions/v1beta1.",
        "fresh_expected_ans": "Use apiVersion: networking.k8s.io/v1 (extensions/v1beta1 was deprecated and removed).",
        "explanation": "extensions/v1beta1 was removed in modern Kubernetes releases."
    },
    {
        "id": "q4",
        "category": "Wikipedia Revisions",
        "query": "What is the official brand name and logo of the microblogging platform formerly known as Twitter?",
        "canonical_uri": "wiki://tech/twitter_branding",
        "stale_expected_ans": "The platform is Twitter and uses the blue bird logo.",
        "fresh_expected_ans": "The platform is officially X (operated by X Corp) and uses the stylized X glyph.",
        "explanation": "Rebranding occurred in late 2023 and finalized in current revisions."
    },
    {
        "id": "q5",
        "category": "STALE Benchmark",
        "query": "Where does the user currently reside and what is their occupation?",
        "canonical_uri": "chat://user/residence",
        "stale_expected_ans": "The user lives in Seattle, WA and works remotely for an e-commerce firm.",
        "fresh_expected_ans": "The user lives in Austin, TX and founded an AI analytics startup.",
        "explanation": "User relocated to Austin in 2025 as recorded in later chat turns."
    }
]

def build_version_catalog() -> Dict[str, DocumentChunk]:
    """
    Returns mapping of canonical_uri -> latest DocumentChunk
    """
    catalog = {}
    for doc in VERSIONED_DOCUMENTS:
        if doc.is_latest:
            catalog[doc.canonical_uri] = doc
    return catalog
