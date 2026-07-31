from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class RagChunk(BaseTool):
    """Chunk documents for RAG."""

    _name = "rag_chunk"
    _description = "Chunk documents: split, merge, list_chunks, get_chunk"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._chunks: list[dict[str, Any]] = []

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "action" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "")
        try:
            if action == "split":
                doc_id = params.get("doc_id", "")
                content = params.get("content", "")
                chunk_size = params.get("chunk_size", 500)
                overlap = params.get("overlap", 50)
                text_chunks = [content[i : i + chunk_size] for i in range(0, len(content), chunk_size - overlap)]
                chunks = []
                for i, text in enumerate(text_chunks):
                    chunk = {"id": f"chunk_{len(self._chunks) + 1}", "doc_id": doc_id, "index": i, "text": text}
                    self._chunks.append(chunk)
                    chunks.append(chunk)
                return {"success": True, "chunks": chunks, "count": len(chunks)}
            elif action == "merge":
                chunk_ids = params.get("chunk_ids", [])
                merged_text = " ".join(c["text"] for c in self._chunks if c.get("id") in chunk_ids)
                return {"success": True, "merged": merged_text}
            elif action == "list_chunks":
                return {"success": True, "chunks": self._chunks, "count": len(self._chunks)}
            elif action == "get_chunk":
                chunk_id = params.get("chunk_id", "")
                chunk = next((c for c in self._chunks if c.get("id") == chunk_id), None)
                if not chunk:
                    return {"success": False, "error": f"Chunk not found: {chunk_id}"}
                return {"success": True, "chunk": chunk}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._chunks.clear()

    async def cleanup(self) -> None:
        self._chunks.clear()
