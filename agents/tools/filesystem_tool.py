from __future__ import annotations

import os
import shutil
from typing import Any

from ..base.base_tool import BaseTool


class FilesystemTool(BaseTool):
    _name = "filesystem"
    _description = "Read, write, delete, and list files on the filesystem"
    _permissions = ["read", "write", "delete"]

    def __init__(self) -> None:
        self._operations_log: list[dict[str, Any]] = []

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        action = params.get("action")
        if action not in ("read", "write", "delete", "list"):
            return False
        if action in ("read", "write", "delete") and "path" not in params:
            return False
        return not (action == "write" and "content" not in params)

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action")
        path = params.get("path", "")

        try:
            if action == "read":
                if not os.path.exists(path):
                    raise FileNotFoundError(f"File not found: {path}")
                with open(path, encoding="utf-8") as f:
                    content = f.read()
                self._log_operation("read", path)
                return {"success": True, "content": content, "path": path}

            elif action == "write":
                content = params.get("content", "")

                # Backup existing file for rollback
                backup = None
                if os.path.exists(path):
                    with open(path, encoding="utf-8") as f:
                        backup = f.read()

                os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)

                self._log_operation("write", path, backup=backup)
                return {"success": True, "path": path, "bytes_written": len(content)}

            elif action == "delete":
                if not os.path.exists(path):
                    raise FileNotFoundError(f"File not found: {path}")

                # Backup file content for rollback
                backup = None
                if os.path.isfile(path):
                    with open(path, encoding="utf-8") as f:
                        backup = f.read()
                elif os.path.isdir(path):
                    backup_dir = path + ".backup"
                    shutil.copytree(path, backup_dir)
                    backup = backup_dir

                os.remove(path)
                self._log_operation("delete", path, backup=backup)
                return {"success": True, "path": path, "deleted": True}

            elif action == "list":
                directory = path or "."
                if not os.path.isdir(directory):
                    raise NotADirectoryError(f"Not a directory: {directory}")
                entries = os.listdir(directory)
                self._log_operation("list", directory)
                return {"success": True, "path": directory, "entries": entries}

            else:
                return {"success": False, "error": f"Unknown action: {action}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        """Rollback the last filesystem operation."""
        if not self._operations_log:
            return

        last = self._operations_log.pop()
        op = last.get("operation")
        path = last.get("path")
        backup = last.get("backup")

        try:
            if op == "write" and backup is not None:
                # Restore original content
                with open(path, "w", encoding="utf-8") as f:
                    f.write(backup)

            elif op == "delete" and backup is not None:
                if isinstance(backup, str) and backup.endswith(".backup"):
                    # Restore directory from backup
                    shutil.move(backup, path)
                elif os.path.exists(path):
                    # File was deleted, can't restore without backup content
                    pass

        except Exception:
            pass  # Best-effort rollback

    async def cleanup(self) -> None:
        self._operations_log.clear()

    def _log_operation(self, operation: str, path: str, **kwargs: Any) -> None:
        self._operations_log.append({
            "operation": operation,
            "path": path,
            **kwargs,
        })
