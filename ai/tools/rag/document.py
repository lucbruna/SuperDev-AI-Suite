from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class RagDocument(BaseTool):
    """Manage RAG documents."""

    _name = "rag_document"
    _description = "Manage RAG documents: add, get, list, update, delete"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._documents: list[dict[str, Any]] = []

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
            if action == "add":
                doc = {
                    "id": f"doc_{len(self._documents) + 1}",
                    "title": params.get("title", ""),
                    "content": params.get("content", ""),
                    "metadata": params.get("metadata", {}),
                    "source": params.get("source", ""),
                }
                self._documents.append(doc)
                return {"success": True, "document": doc}
            elif action == "get":
                doc_id = params.get("doc_id", "")
                doc = next((d for d in self._documents if d.get("id") == doc_id), None)
                if not doc:
                    return {"success": False, "error": f"Document not found: {doc_id}"}
                return {"success": True, "document": doc}
            elif action == "list":
                return {"success": True, "documents": self._documents, "count": len(self._documents)}
            elif action == "update":
                doc_id = params.get("doc_id", "")
                for doc in self._documents:
                    if doc.get("id") == doc_id:
                        if "title" in params:
                            doc["title"] = params["title"]
                        if "content" in params:
                            doc["content"] = params["content"]
                        if "metadata" in params:
                            doc["metadata"].update(params["metadata"])
                        return {"success": True, "document": doc}
                return {"success": False, "error": f"Document not found: {doc_id}"}
            elif action == "delete":
                doc_id = params.get("doc_id", "")
                self._documents = [d for d in self._documents if d.get("id") != doc_id]
                return {"success": True, "message": f"Deleted document {doc_id}"}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._documents.clear()

    async def cleanup(self) -> None:
        self._documents.clear()
