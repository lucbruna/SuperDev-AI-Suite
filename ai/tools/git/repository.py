from __future__ import annotations

import subprocess
from typing import Any

from ...base.base_tool import BaseTool


class GitRepository(BaseTool):
    _name = "git_repository"
    _description = "Manage Git repository operations: init, clone, status"
    _permissions = ["execute"]

    def __init__(self) -> None:
        self._repos: list[str] = []

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "action" in params

    def _run(self, cmd: list[str], cwd: str | None = None) -> dict[str, Any]:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=30)
            return {"success": result.returncode == 0, "stdout": result.stdout, "stderr": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "")
        path = params.get("path", ".")
        try:
            if action == "init":
                result = self._run(["git", "init"], path)
                if result["success"]:
                    self._repos.append(path)
                return result
            elif action == "clone":
                url = params.get("url", "")
                result = self._run(["git", "clone", url, path])
                if result["success"]:
                    self._repos.append(path)
                return result
            elif action == "status":
                return self._run(["git", "status"], path)
            elif action == "log":
                count = params.get("count", 10)
                fmt = params.get("format", "oneline")
                return self._run(["git", "log", f"-{count}", f"--{fmt}"], path)
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        self._repos.clear()
