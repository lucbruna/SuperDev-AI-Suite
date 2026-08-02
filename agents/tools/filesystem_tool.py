"""FilesystemTool with write/read/delete/list actions and rollback support."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


class FilesystemTool:
    """Provides filesystem operations to agents with undo (rollback) support."""

    def __init__(self) -> None:
        # Each entry: {"type": "write"|"delete", "path": ..., "backup": str|None}
        self._history: list[dict[str, Any]] = []

    async def execute(self, params: dict) -> dict:
        action = params.get("action")
        if not await self.validate(params):
            return {"success": False, "error": "Invalid parameters"}

        path = Path(params["path"])

        if action == "write":
            return self._write(path, params.get("content", ""))
        if action == "read":
            return self._read(path)
        if action == "delete":
            return self._delete(path)
        if action == "list":
            return self._list(path)
        return {"success": False, "error": f"Unknown action: {action}"}

    def _write(self, path: Path, content: str) -> dict:
        backup: str | None = None
        if path.exists():
            backup = path.read_text(encoding="utf-8")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        self._history.append({"type": "write", "path": str(path), "backup": backup})
        return {"success": True}

    def _read(self, path: Path) -> dict:
        if not path.exists():
            return {"success": False, "error": "File not found"}
        return {"success": True, "content": path.read_text(encoding="utf-8")}

    def _delete(self, path: Path) -> dict:
        backup: str | None = None
        if path.exists():
            backup = path.read_text(encoding="utf-8")
        path.unlink(missing_ok=True)
        self._history.append({"type": "delete", "path": str(path), "backup": backup})
        return {"success": True}

    def _list(self, path: Path) -> dict:
        if not path.exists() or not path.is_dir():
            return {"success": False, "error": "Directory not found"}
        entries = sorted(e.name for e in path.iterdir())
        return {"success": True, "entries": entries}

    async def rollback(self) -> None:
        for entry in reversed(self._history):
            path = Path(entry["path"])
            if entry["type"] == "write":
                if entry["backup"] is None:
                    path.unlink(missing_ok=True)
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(entry["backup"], encoding="utf-8")
            elif entry["type"] == "delete":
                if entry["backup"] is not None:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(entry["backup"], encoding="utf-8")
        self._history.clear()

    async def validate(self, params: dict) -> bool:
        action = params.get("action")
        if action not in {"read", "write", "delete", "list"}:
            return False
        if "path" not in params:
            return False
        if action == "write" and "content" not in params:
            return False
        return True
