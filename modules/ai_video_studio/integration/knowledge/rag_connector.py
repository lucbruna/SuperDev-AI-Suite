"""RAG Connector — retrieval-augmented context assembly."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration.knowledge.semantic_search import (
    get_semantic_search,
)


class RAGConnector:
    """Retrieves relevant chunks and assembles an LLM-ready context."""

    def answer_context(self, question: str, *, top_k: int = 3) -> dict[str, Any]:
        search = get_semantic_search()
        hits = search.search(question, top_k=top_k)["results"]
        context = "\n".join(f"- {h['text']}" for h in hits)
        return {
            "question": question,
            "retrieved": len(hits),
            "context": context or "(no matching documents)",
            "prompt": (
                f"Answer the question using only the context below.\n"
                f"Context:\n{context}\n\nQuestion: {question}"
            ),
        }


_rag_connector: RAGConnector | None = None


def get_rag_connector() -> RAGConnector:
    global _rag_connector
    if _rag_connector is None:
        _rag_connector = RAGConnector()
    return _rag_connector
