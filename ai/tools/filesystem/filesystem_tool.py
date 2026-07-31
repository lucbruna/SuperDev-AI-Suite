from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool
from .directory_scanner import DirectoryScanner
from .file_reader import FileReader
from .file_search import FileSearch
from .file_writer import FileWriter
from .permissions import FilePermissions
from .synchronization import FileSync


class FilesystemTool(BaseTool):
    """Composite filesystem tool delegating to specialized sub-tools."""

    _name = "filesystem"
    _description = "Complete filesystem operations: read, write, search, scan, permissions, sync"
    _permissions = ["read", "write", "delete"]

    def __init__(self) -> None:
        self._reader = FileReader()
        self._writer = FileWriter()
        self._searcher = FileSearch()
        self._scanner = DirectoryScanner()
        self._perms = FilePermissions()
        self._syncer = FileSync()

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "action" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "")
        if action == "read":
            return await self._reader.execute(params)
        elif action == "write":
            return await self._writer.execute(params)
        elif action == "search":
            return await self._searcher.execute(params)
        elif action == "scan":
            return await self._scanner.execute(params)
        elif action in ("get_permissions", "set_permissions"):
            return await self._perms.execute(params)
        elif action in ("copy", "move", "mirror"):
            return await self._syncer.execute(params)
        return {"success": False, "error": f"Unknown filesystem action: {action}"}

    async def rollback(self) -> None:
        await self._writer.rollback()
        await self._perms.rollback()
        await self._syncer.rollback()

    async def cleanup(self) -> None:
        for tool in (self._reader, self._writer, self._searcher, self._scanner, self._perms, self._syncer):
            await tool.cleanup()
