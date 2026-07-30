from __future__ import annotations

import os
from typing import Any

from ...base.base_tool import BaseTool


class DirectoryScanner(BaseTool):
    _name = "directory_scanner"
    _description = "Scan directory structure and list contents"
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
        return True

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        path = params.get("path", ".")
        recursive = params.get("recursive", False)
        try:
            if not os.path.isdir(path):
                return {"success": False, "error": f"Not a directory: {path}"}
            if recursive:
                entries: list[dict[str, Any]] = []
                for dirpath, dirnames, filenames in os.walk(path):
                    for d in dirnames:
                        entries.append({"name": d, "path": os.path.join(dirpath, d), "type": "directory"})
                    for f in filenames:
                        full = os.path.join(dirpath, f)
                        stat = os.stat(full)
                        entries.append({"name": f, "path": full, "type": "file", "size": stat.st_size})
                result = {"success": True, "path": path, "entries": entries, "total": len(entries)}
            else:
                names = os.listdir(path)
                entries = []
                for name in names:
                    full = os.path.join(path, name)
                    entry_type = "directory" if os.path.isdir(full) else "file"
                    entries.append({"name": name, "type": entry_type})
                result = {"success": True, "path": path, "entries": entries, "total": len(entries)}
            self._operations.append({"action": "scan", "path": path})
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._operations.clear()

    async def cleanup(self) -> None:
        self._operations.clear()
