from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class ApiClient(BaseTool):
    """API client management."""

    _name = "api_client"
    _description = "API client management: create, configure, list, remove"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._clients: dict[str, dict[str, Any]] = {}

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
        client_id = params.get("client_id", "default")
        try:
            if action == "create":
                client = {
                    "client_id": client_id,
                    "base_url": params.get("base_url", ""),
                    "timeout": params.get("timeout", 30),
                    "headers": params.get("headers", {}),
                }
                self._clients[client_id] = client
                return {"success": True, "client": client}
            elif action == "configure":
                client = self._clients.get(client_id)
                if not client:
                    return {"success": False, "error": f"Client not found: {client_id}"}
                if "timeout" in params:
                    client["timeout"] = params["timeout"]
                if "headers" in params:
                    client["headers"].update(params["headers"])
                return {"success": True, "client": client}
            elif action == "list":
                return {"success": True, "clients": list(self._clients.values()), "count": len(self._clients)}
            elif action == "remove":
                self._clients.pop(client_id, None)
                return {"success": True, "message": f"Removed client {client_id}"}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._clients.clear()

    async def cleanup(self) -> None:
        self._clients.clear()
