from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class LlmChat(BaseTool):
    """LLM chat interactions."""

    _name = "llm_chat"
    _description = "Multi-turn LLM chat with message history"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._conversations: dict[str, list[dict[str, str]]] = {}

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
        conversation_id = params.get("conversation_id", "default")
        try:
            if conversation_id not in self._conversations:
                self._conversations[conversation_id] = []

            if action == "send":
                message = params.get("message", "")
                self._conversations[conversation_id].append({"role": "user", "content": message})
                reply = f"Mock reply to: {message[:50]}..."
                self._conversations[conversation_id].append({"role": "assistant", "content": reply})
                return {"success": True, "reply": reply, "conversation_id": conversation_id}
            elif action == "history":
                return {
                    "success": True,
                    "messages": self._conversations[conversation_id],
                    "count": len(self._conversations[conversation_id]),
                }
            elif action == "clear":
                self._conversations[conversation_id] = []
                return {"success": True, "message": "Conversation cleared"}
            elif action == "list":
                return {"success": True, "conversations": list(self._conversations.keys())}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._conversations.clear()

    async def cleanup(self) -> None:
        self._conversations.clear()
