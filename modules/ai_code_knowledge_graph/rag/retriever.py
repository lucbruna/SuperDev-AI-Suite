"""RAG retriever — embed a query, retrieve top-k items, answer via the LLM.

Works fully offline: retrieval uses the embedding service, and answers come
from the configured LLM client (the deterministic echo fallback when no real
provider is available), so tests never depend on network access.
"""
from __future__ import annotations

from typing import Any

from modules.ai_code_knowledge_graph.embeddings.service import EmbeddingService
from modules.ai_code_knowledge_graph.llm.client import LLMClient
from modules.ai_code_knowledge_graph.rag.context import build_context

_SYSTEM_PROMPT = (
    "You answer questions about a codebase using only the provided context. "
    "Keep answers short and reference files by path."
)


class RagRetriever:
    """Retrieve knowledge-base items for a query and optionally answer it."""

    def __init__(
        self,
        embeddings: EmbeddingService,
        llm: LLMClient | None = None,
        *,
        k: int = 5,
    ) -> None:
        self.embeddings = embeddings
        self.llm = llm or LLMClient()
        self.k = max(1, k)

    def retrieve(self, query: str, k: int | None = None) -> list[tuple[str, float, dict[str, Any]]]:
        """Return the top-k embedded items most relevant to the query."""
        return self.embeddings.search(query, k=k or self.k)

    def ask(self, query: str, k: int | None = None) -> dict[str, Any]:
        """Retrieve context and produce ``{answer, results, context}``."""
        results = self.retrieve(query, k=k or self.k)
        context = build_context(results)
        answer = self.llm.complete(_SYSTEM_PROMPT, query) if results else None
        return {
            "query": query,
            "answer": answer,
            "context": context,
            "results": [
                {"id": item_id, "score": round(score, 4), "payload": payload}
                for item_id, score, payload in results
            ],
        }
