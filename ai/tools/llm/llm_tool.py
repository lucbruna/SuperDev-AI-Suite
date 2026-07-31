from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool
from .chat import LlmChat
from .completion import LlmCompletion
from .embedding import LlmEmbedding
from .model import LlmModel
from .tokenizer import LlmTokenizer


class LlmTool(BaseTool):
    """Composite LLM tool for language model operations."""

    _name = "llm"
    _description = "LLM operations: completion, chat, embedding, tokenizer, model management"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._completion = LlmCompletion()
        self._chat = LlmChat()
        self._embedding = LlmEmbedding()
        self._tokenizer = LlmTokenizer()
        self._model = LlmModel()

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

        if sub_tool == "completion" or action == "complete":
            return await self._completion.execute(params)
        elif sub_tool == "chat" or action == "chat":
            return await self._chat.execute(params)
        elif sub_tool == "embedding":
            return await self._embedding.execute(params)
        elif sub_tool == "tokenizer":
            return await self._tokenizer.execute(params)
        elif sub_tool == "model":
            return await self._model.execute(params)
        return {"success": False, "error": f"Unknown LLM action: {action}"}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        for tool in (self._completion, self._chat, self._embedding, self._tokenizer, self._model):
            await tool.cleanup()
