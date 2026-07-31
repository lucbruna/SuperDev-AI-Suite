from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class DockerCompose(BaseTool):
    """Manage Docker Compose environments."""

    _name = "docker_compose"
    _description = "Manage Docker Compose: up, down, start, stop, ps, logs, build"
    _permissions = ["execute"]

    def __init__(self) -> None:
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
        project = params.get("project", "")
        params.get("file", "docker-compose.yml")
        try:
            if action == "up":
                detach = params.get("detach", True)
                self._operation_log.append(f"up {project}")
                return {"success": True, "message": f"Started compose project {project} (detach={detach})"}
            elif action == "down":
                self._operation_log.append(f"down {project}")
                return {"success": True, "message": f"Stopped compose project {project}"}
            elif action == "start":
                self._operation_log.append(f"start {project}")
                return {"success": True, "message": f"Started services for {project}"}
            elif action == "stop":
                self._operation_log.append(f"stop {project}")
                return {"success": True, "message": f"Stopped services for {project}"}
            elif action == "ps":
                return {"success": True, "services": [], "project": project}
            elif action == "logs":
                return {"success": True, "logs": f"[mock compose logs for {project}]"}
            elif action == "build":
                self._operation_log.append(f"build {project}")
                return {"success": True, "message": f"Built services for {project}"}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._operation_log.clear()

    async def cleanup(self) -> None:
        self._operation_log.clear()
