from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class DockerContainer(BaseTool):
    """Manage Docker containers."""

    _name = "docker_container"
    _description = "Manage Docker containers: list, start, stop, restart, logs, exec"
    _permissions = ["execute"]

    def __init__(self) -> None:
        self._containers: list[dict[str, Any]] = []
        self._operation_log: list[str] = []

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
        container_id = params.get("container_id", "")
        try:
            if action == "list":
                return {"success": True, "containers": self._containers, "count": len(self._containers)}
            elif action == "start":
                self._operation_log.append(f"started {container_id}")
                return {"success": True, "message": f"Container {container_id} started"}
            elif action == "stop":
                self._operation_log.append(f"stopped {container_id}")
                return {"success": True, "message": f"Container {container_id} stopped"}
            elif action == "restart":
                self._operation_log.append(f"restarted {container_id}")
                return {"success": True, "message": f"Container {container_id} restarted"}
            elif action == "logs":
                return {"success": True, "logs": f"[mock logs for {container_id}]", "container_id": container_id}
            elif action == "exec":
                command = params.get("command", "")
                self._operation_log.append(f"exec {command} on {container_id}")
                return {"success": True, "output": f"[mock output of '{command}']"}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._operation_log.clear()

    async def cleanup(self) -> None:
        self._containers.clear()
        self._operation_log.clear()
