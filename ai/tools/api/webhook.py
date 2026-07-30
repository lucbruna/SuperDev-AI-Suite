from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class ApiWebhook(BaseTool):
    """Manage API webhooks."""

    _name = "api_webhook"
    _description = "Manage API webhooks: register, list, trigger, delete, history"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._webhooks: list[dict[str, Any]] = []
        self._history: list[dict[str, Any]] = []

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
            if action == "register":
                webhook = {
                    "id": f"wh_{len(self._webhooks) + 1}",
                    "url": params.get("url", ""),
                    "events": params.get("events", []),
                    "active": True,
                }
                self._webhooks.append(webhook)
                return {"success": True, "webhook": webhook}
            elif action == "list":
                return {"success": True, "webhooks": self._webhooks, "count": len(self._webhooks)}
            elif action == "trigger":
                event = params.get("event", "")
                data = params.get("data", {})
                entry = {"event": event, "data": data, "timestamp": "2024-01-01T00:00:00Z"}
                self._history.append(entry)
                return {"success": True, "triggered": event}
            elif action == "delete":
                webhook_id = params.get("webhook_id", "")
                self._webhooks = [w for w in self._webhooks if w.get("id") != webhook_id]
                return {"success": True, "message": f"Deleted webhook {webhook_id}"}
            elif action == "history":
                return {"success": True, "history": self._history, "count": len(self._history)}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._webhooks.clear()
        self._history.clear()

    async def cleanup(self) -> None:
        self._webhooks.clear()
        self._history.clear()
