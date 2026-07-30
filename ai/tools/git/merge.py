from __future__ import annotations

import subprocess
from typing import Any

from ...base.base_tool import BaseTool


class GitMerge(BaseTool):
    _name = "git_merge"
    _description = "Merge Git branches"
    _permissions = ["execute"]

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "branch" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        branch = params["branch"]
        path = params.get("path", ".")
        try:
            r = subprocess.run(["git", "merge", branch], capture_output=True, text=True, cwd=path, timeout=30)
            return {
                "success": r.returncode == 0,
                "stdout": r.stdout,
                "stderr": r.stderr,
                "conflict": "CONFLICT" in r.stdout or "CONFLICT" in r.stderr,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        pass
