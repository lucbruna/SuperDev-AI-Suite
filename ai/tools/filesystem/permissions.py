from __future__ import annotations

import os
import stat
from typing import Any

from ...base.base_tool import BaseTool


class FilePermissions(BaseTool):
    _name = "file_permissions"
    _description = "Manage file and directory permissions"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._changes: list[dict[str, Any]] = []

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "path" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        path = params["path"]
        action = params.get("action", "get")
        try:
            if action == "get":
                mode = os.stat(path).st_mode
                return {
                    "success": True,
                    "path": path,
                    "readable": bool(mode & stat.S_IRUSR),
                    "writable": bool(mode & stat.S_IWUSR),
                    "executable": bool(mode & stat.S_IXUSR),
                    "mode": oct(mode),
                }
            elif action == "set":
                new_mode = int(params.get("mode", "644"), 8)
                old_mode = os.stat(path).st_mode
                os.chmod(path, new_mode)
                self._changes.append({"path": path, "old_mode": old_mode, "new_mode": new_mode})
                return {"success": True, "path": path, "mode": oct(new_mode)}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        if not self._changes:
            return
        last = self._changes.pop()
        os.chmod(last["path"], last["old_mode"])

    async def cleanup(self) -> None:
        self._changes.clear()
