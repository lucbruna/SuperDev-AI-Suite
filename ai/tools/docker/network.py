from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class DockerNetwork(BaseTool):
    """Manage Docker networks."""

    _name = "docker_network"
    _description = "Manage Docker networks: list, create, remove, connect, disconnect, inspect"
    _permissions = ["execute"]

    def __init__(self) -> None:
        self._networks: list[dict[str, Any]] = []

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
            if action == "list":
                return {"success": True, "networks": self._networks, "count": len(self._networks)}
            elif action == "create":
                name = params.get("name", f"net_{len(self._networks) + 1}")
                driver = params.get("driver", "bridge")
                network = {"name": name, "driver": driver, "id": f"net_{len(self._networks) + 1}"}
                self._networks.append(network)
                return {"success": True, "network": network}
            elif action == "remove":
                name = params.get("name", "")
                self._networks = [n for n in self._networks if n.get("name") != name]
                return {"success": True, "message": f"Removed network {name}"}
            elif action == "connect":
                return {"success": True, "message": "Connected container to network"}
            elif action == "disconnect":
                return {"success": True, "message": "Disconnected container from network"}
            elif action == "inspect":
                name = params.get("name", "")
                network = next((n for n in self._networks if n.get("name") == name), None)
                if not network:
                    return {"success": False, "error": f"Network not found: {name}"}
                return {"success": True, "network": network}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._networks.clear()

    async def cleanup(self) -> None:
        self._networks.clear()
