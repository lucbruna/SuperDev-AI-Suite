from __future__ import annotations

import subprocess
from typing import Any

from ...base.base_tool import BaseTool


class GitHistory(BaseTool):
    _name = "git_history"
    _description = "View and search Git commit history"
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
        count = params.get("count", 20)
        author = params.get("author")
        try:
            cmd = ["git", "log", f"-{count}", "--format=%H|%an|%ae|%ad|%s"]
            if author:
                cmd.extend([f"--author={author}"])
            r = subprocess.run(cmd, capture_output=True, text=True, cwd=path, timeout=15)
            commits = []
            for line in r.stdout.strip().split("\n"):
                if line and "|" in line:
                    parts = line.split("|", 4)
                    commits.append({"hash": parts[0], "author": parts[1], "email": parts[2], "date": parts[3], "message": parts[4] if len(parts) > 4 else ""})
            return {"success": r.returncode == 0, "commits": commits, "count": len(commits)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        pass
