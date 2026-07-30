from __future__ import annotations

import subprocess
from typing import Any

from ...base.base_tool import BaseTool


class GitStash(BaseTool):
    _name = "git_stash"
    _description = "Manage Git stash: push, pop, list, drop"
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
        path = params.get("path", ".")
        message = params.get("message", "")
        try:
            if action == "push":
                cmd = ["git", "stash", "push"]
                if message:
                    cmd.extend(["-m", message])
                r = subprocess.run(cmd, capture_output=True, text=True, cwd=path, timeout=15)
                return {"success": r.returncode == 0, "stdout": r.stdout}
            elif action == "pop":
                r = subprocess.run(["git", "stash", "pop"], capture_output=True, text=True, cwd=path, timeout=15)
                return {"success": r.returncode == 0, "stdout": r.stdout}
            elif action == "list":
                r = subprocess.run(["git", "stash", "list"], capture_output=True, text=True, cwd=path, timeout=15)
                return {"success": True, "stashes": r.stdout.splitlines() if r.stdout else []}
            elif action == "drop":
                ref = params.get("ref", "stash@{0}")
                r = subprocess.run(["git", "stash", "drop", ref], capture_output=True, text=True, cwd=path, timeout=15)
                return {"success": r.returncode == 0, "stdout": r.stdout}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        pass
