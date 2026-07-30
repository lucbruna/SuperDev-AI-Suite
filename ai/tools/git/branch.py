from __future__ import annotations

import subprocess
from typing import Any

from ...base.base_tool import BaseTool


class GitBranch(BaseTool):
    _name = "git_branch"
    _description = "Manage Git branches: create, delete, list, switch"
    _permissions = ["execute"]

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "action" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "list")
        name = params.get("name", "")
        path = params.get("path", ".")
        try:
            if action == "list":
                r = subprocess.run(["git", "branch"], capture_output=True, text=True, cwd=path, timeout=15)
                return {"success": r.returncode == 0, "branches": r.stdout.splitlines(), "stdout": r.stdout}
            elif action == "create":
                r = subprocess.run(["git", "branch", name], capture_output=True, text=True, cwd=path, timeout=15)
                return {"success": r.returncode == 0, "stdout": r.stdout}
            elif action == "delete":
                r = subprocess.run(["git", "branch", "-D", name], capture_output=True, text=True, cwd=path, timeout=15)
                return {"success": r.returncode == 0, "stdout": r.stdout}
            elif action == "switch":
                r = subprocess.run(["git", "checkout", name], capture_output=True, text=True, cwd=path, timeout=15)
                return {"success": r.returncode == 0, "stdout": r.stdout}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        pass
