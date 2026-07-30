from __future__ import annotations

import subprocess
from typing import Any

from ...base.base_tool import BaseTool


class GitCommit(BaseTool):
    _name = "git_commit"
    _description = "Stage and commit changes in Git"
    _permissions = ["execute"]

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "message" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        message = params["message"]
        path = params.get("path", ".")
        files = params.get("files", [])
        try:
            if files:
                for f in files:
                    subprocess.run(["git", "add", f], cwd=path, capture_output=True, text=True, timeout=15)
            else:
                subprocess.run(["git", "add", "-A"], cwd=path, capture_output=True, text=True, timeout=15)
            r = subprocess.run(["git", "commit", "-m", message], cwd=path, capture_output=True, text=True, timeout=15)
            return {"success": r.returncode == 0, "stdout": r.stdout, "stderr": r.stderr, "hash": r.stdout.split()[0] if r.returncode == 0 else ""}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        pass
