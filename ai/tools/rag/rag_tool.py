from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool
from .document import RagDocument
from .chunk import RagChunk
from .vector_store import RagVectorStore
from .retriever import RagRetriever
from .index import RagIndex


class RagTool(BaseTool):
    """Composite RAG tool for retrieval-augmented generation."""

    _name = "rag"
    _description = "RAG operations: documents, chunks, vector store, retrieval, indexing"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._document = RagDocument()
        self._chunk = RagChunk()
        self._vector_store = RagVectorStore()
        self._retriever = RagRetriever()
        self._index = RagIndex()

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "action" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        sub_tool = params.get("sub_tool", "")
        action = params.get("action", "")

        if sub_tool == "document":
            return await self._document.execute(params)
        elif sub_tool == "chunk":
            return await self._chunk.execute(params)
        elif sub_tool == "vector_store":
            return await self._vector_store.execute(params)
        elif sub_tool == "retriever" or action == "retrieve":
            return await self._retriever.execute(params)
        elif sub_tool == "index":
            return await self._index.execute(params)
        return {"success": False, "error": f"Unknown RAG action: {action}"}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        for tool in (self._document, self._chunk, self._vector_store, self._retriever, self._index):
            await tool.cleanup()
