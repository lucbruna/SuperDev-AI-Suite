from __future__ import annotations

import os
from typing import Any

from ...base.base_tool import BaseTool


class FileWriter(BaseTool):
    _name = "file_writer"
    _description = "Write content to files on the filesystem"
    _permissions = ["write"]

    def __init__(self) -> None:
        self._backups: list[dict[str, Any]] = []

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "path" in params and "content" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        path = params["path"]
        content = params["content"]
        mode = params.get("mode", "w")
        try:
            backup = None
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    backup = f.read()
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, mode, encoding="utf-8") as f:
                f.write(content)
            self._backups.append({"path": path, "backup": backup})
            return {"success": True, "path": path, "bytes_written": len(content)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        if not self._backups:
            return
        last = self._backups.pop()
        if last["backup"] is not None:
            with open(last["path"], "w", encoding="utf-8") as f:
                f.write(last["backup"])

    async def cleanup(self) -> None:
        self._backups.clear()
