from __future__ import annotations

import fnmatch
import os
from typing import Any

from ...base.base_tool import BaseTool

_EXCLUDED_DIRS: set[str] = {
    "node_modules",
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "dist",
    "build",
    ".tox",
    ".mypy_cache",
    ".pytest_cache",
    ".eggs",
    ".idea",
    ".vscode",
    "coverage",
    ".nyc_output",
}


class FileSearch(BaseTool):
    _name = "file_search"
    _description = "Search files by pattern and content"
    _permissions = ["read"]

    def __init__(self) -> None:
        self._operations: list[dict[str, Any]] = []

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "pattern" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        pattern = params["pattern"]
        root = params.get("root", ".")
        content_pattern = params.get("content")
        results: list[str] = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in _EXCLUDED_DIRS and not d.endswith(".egg-info")]
            for filename in filenames:
                if fnmatch.fnmatch(filename, pattern):
                    full = os.path.join(dirpath, filename)
                    if content_pattern:
                        try:
                            with open(full, encoding="utf-8", errors="ignore") as f:
                                if content_pattern in f.read():
                                    results.append(full)
                        except Exception:
                            pass
                    else:
                        results.append(full)
        self._operations.append({"pattern": pattern, "root": root, "matches": len(results)})
        return {"success": True, "matches": results, "count": len(results)}

    async def rollback(self) -> None:
        self._operations.clear()

    async def cleanup(self) -> None:
        self._operations.clear()
