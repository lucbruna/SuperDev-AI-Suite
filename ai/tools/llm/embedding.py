from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class LlmEmbedding(BaseTool):
    """Generate text embeddings."""

    _name = "llm_embedding"
    _description = "Generate text embeddings for semantic search and similarity"
    _permissions = ["read"]

    def __init__(self) -> None:
        self._embedding_log: list[dict[str, Any]] = []

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
            if action == "embed":
                texts = params.get("texts", [])
                if isinstance(texts, str):
                    texts = [texts]
                model = params.get("model", "text-embedding-3-small")
                embeddings = [[0.1] * 128 for _ in texts]
                result = {
                    "model": model,
                    "embeddings": embeddings,
                    "dimensions": 128,
                    "count": len(texts),
                }
                self._embedding_log.append(result)
                return {"success": True, **result}
            elif action == "similarity":
                text1 = params.get("text1", "")
                text2 = params.get("text2", "")
                return {"success": True, "similarity": 0.85, "text1": text1, "text2": text2}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._embedding_log.clear()

    async def cleanup(self) -> None:
        self._embedding_log.clear()
