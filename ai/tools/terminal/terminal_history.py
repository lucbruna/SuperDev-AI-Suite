from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class TerminalHistory(BaseTool):
    _name = "terminal_history"
    _description = "Track and retrieve terminal command history"
    _permissions = ["read"]

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return True

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "list")
        if action == "list":
            limit = params.get("limit", 50)
            return {"success": True, "entries": self._entries[-limit:], "total": len(self._entries)}
        elif action == "clear":
            self._entries.clear()
            return {"success": True, "cleared": True}
        elif action == "search":
            query = params.get("query", "").lower()
            results = [e for e in self._entries if query in e.get("command", "").lower()]
            return {"success": True, "entries": results, "count": len(results)}
        return {"success": False, "error": f"Unknown action: {action}"}

    def add_entry(self, command: str, result: dict[str, Any]) -> None:
        self._entries.append({"command": command, "result": result})

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        self._entries.clear()
