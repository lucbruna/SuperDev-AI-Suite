from __future__ import annotations

import subprocess
from typing import Any

from ...base.base_tool import BaseTool


class GitDiff(BaseTool):
    _name = "git_diff"
    _description = "Show Git diffs between commits, branches, or working tree"
    _permissions = ["read"]

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return True

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        path = params.get("path", ".")
        target = params.get("target", "HEAD")
        staged = params.get("staged", False)
        try:
            cmd = ["git", "diff"]
            if staged:
                cmd.append("--cached")
            if target != "HEAD":
                cmd.append(target)
            r = subprocess.run(cmd, capture_output=True, text=True, cwd=path, timeout=15)
            return {"success": r.returncode == 0, "diff": r.stdout, "stderr": r.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        pass
