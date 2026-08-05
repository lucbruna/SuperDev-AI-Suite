"""Knowledge Connector — facade over document search, RAG, semantic search and memory."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration.connector_base import DomainConnector
from modules.ai_video_studio.integration.knowledge.document_search import (
    get_document_search,
)
from modules.ai_video_studio.integration.knowledge.enterprise_memory import (
    get_enterprise_memory,
)
from modules.ai_video_studio.integration.knowledge.rag_connector import get_rag_connector
from modules.ai_video_studio.integration.knowledge.semantic_search import (
    get_semantic_search,
)


class KnowledgeConnector(DomainConnector):
    """Document search, RAG, semantic search and enterprise memory."""

    domain = "knowledge"
    description = "Document search, RAG, semantic search and enterprise memory"

    def __init__(self) -> None:
        super().__init__()
        self._register("index_document", self._index)
        self._register("search_documents", lambda d: get_document_search().search(
            d.get("query", ""), top_k=d.get("top_k", 5)))
        self._register("semantic_search", lambda d: get_semantic_search().search(
            d.get("query", ""), top_k=d.get("top_k", 5)))
        self._register("rag_context", lambda d: get_rag_connector().answer_context(
            d.get("question", ""), top_k=d.get("top_k", 3)))
        self._register("remember", self._remember)

    def _index(self, data: dict[str, Any]) -> dict[str, Any]:
        text = data.get("text", "")
        if not text:
            return {"ok": False, "error": "index_document: missing 'text'"}
        get_document_search().index(text, id=data.get("id"))
        get_semantic_search().index(text, id=data.get("id"))
        return {"ok": True, "indexed": text}

    def _remember(self, data: dict[str, Any]) -> dict[str, Any]:
        return get_enterprise_memory().remember(data.get("namespace", "default"),
                                                data.get("key", ""), data.get("value"))


_knowledge_connector: KnowledgeConnector | None = None


def get_knowledge_connector() -> KnowledgeConnector:
    global _knowledge_connector
    if _knowledge_connector is None:
        _knowledge_connector = KnowledgeConnector()
    return _knowledge_connector
