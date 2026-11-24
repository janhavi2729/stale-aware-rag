"""Optional FastAPI service for the Stale-Aware RAG pipeline.

Run with: uvicorn api:app --reload
"""

from dataclasses import asdict
from typing import Any, Dict

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except ImportError:  # Keep the core project runnable without web dependencies.
    FastAPI = None

from src.pipeline import StaleAwareRAG


if FastAPI:
    app = FastAPI(title="Stale-Aware RAG", version="1.0.0")
    service = StaleAwareRAG()

    class QueryRequest(BaseModel):
        query: str
        top_k: int = 5

    @app.get("/health")
    def health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.post("/answer")
    def answer(request: QueryRequest) -> Dict[str, Any]:
        try:
            result = service.answer(request.query, request.top_k)
            payload = asdict(result)
            return payload
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
else:
    app = None
