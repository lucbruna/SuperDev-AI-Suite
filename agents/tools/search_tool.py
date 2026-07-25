from __future__ import annotations

import fnmatch
import os
import re
from typing import Any

from ..base.base_tool import BaseTool


class SearchTool(BaseTool):
    _name = "search"
    _description = "Search files and directories for patterns"
    _permissions = ["read"]

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "pattern" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        pattern = params.get("pattern", "")
        path = params.get("path", ".")
        search_type = params.get("type", "file")

        if not pattern:
            return {"success": False, "error": "No search pattern provided"}

        try:
            results = []

            if search_type == "file":
                for root, _dirs, files in os.walk(path):
                    for fname in files:
                        if fnmatch.fnmatch(fname, pattern):
                            results.append(os.path.join(root, fname))

            elif search_type == "grep":
                for root, _dirs, files in os.walk(path):
                    for fname in files:
                        try:
                            fpath = os.path.join(root, fname)
                            with open(fpath, encoding="utf-8", errors="ignore") as f:
                                for lineno, line in enumerate(f, 1):
                                    if re.search(pattern, line, re.IGNORECASE):
                                        results.append({
                                            "file": fpath,
                                            "line": lineno,
                                            "content": line.strip(),
                                        })
                        except Exception:
                            pass

            elif search_type == "code":
                code_extensions = {".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".cs", ".go", ".rs", ".rb", ".php"}
                for root, _dirs, files in os.walk(path):
                    for fname in files:
                        ext = os.path.splitext(fname)[1]
                        if ext in code_extensions:
                            try:
                                fpath = os.path.join(root, fname)
                                with open(fpath, encoding="utf-8", errors="ignore") as f:
                                    for lineno, line in enumerate(f, 1):
                                        if re.search(pattern, line, re.IGNORECASE):
                                            results.append({
                                                "file": fpath,
                                                "line": lineno,
                                                "content": line.strip(),
                                            })
                            except Exception:
                                pass

            return {"success": True, "results": results, "count": len(results)}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        pass
