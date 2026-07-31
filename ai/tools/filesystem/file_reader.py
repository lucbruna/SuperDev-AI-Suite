from __future__ import annotations

import os
from typing import Any

from ...base.base_tool import BaseTool


class FileReader(BaseTool):
    _name = "file_reader"
    _description = "Read file contents from the filesystem"
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
        return "path" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        path = params["path"]
        encoding = params.get("encoding", "utf-8")
        offset = params.get("offset")
        limit = params.get("limit")
        try:
            if not os.path.exists(path):
                return {"success": False, "error": f"File not found: {path}"}
            with open(path, encoding=encoding) as f:
                content = f.read()
            if offset is not None and limit is not None:
                lines = content.splitlines()
                content = "\n".join(lines[offset : offset + limit])
            self._operations.append({"action": "read", "path": path})
            return {"success": True, "content": content, "path": path, "size": len(content)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._operations.clear()

    async def cleanup(self) -> None:
        self._operations.clear()
