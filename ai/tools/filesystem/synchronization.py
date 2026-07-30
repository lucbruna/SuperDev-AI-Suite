from __future__ import annotations

import os
import shutil
from typing import Any

from ...base.base_tool import BaseTool


class FileSync(BaseTool):
    _name = "file_sync"
    _description = "Synchronize files and directories between locations"
    _permissions = ["read", "write", "delete"]

    def __init__(self) -> None:
        self._operations: list[dict[str, Any]] = []

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "source" in params and "target" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        source = params["source"]
        target = params["target"]
        action = params.get("action", "copy")
        try:
            if action == "copy":
                if os.path.isdir(source):
                    shutil.copytree(source, target, dirs_exist_ok=True)
                else:
                    shutil.copy2(source, target)
            elif action == "move":
                shutil.move(source, target)
            elif action == "mirror":
                if os.path.isdir(target):
                    shutil.rmtree(target)
                shutil.copytree(source, target)
            self._operations.append({"action": action, "source": source, "target": target})
            return {"success": True, "source": source, "target": target, "action": action}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        if not self._operations:
            return
        last = self._operations.pop()
        if last["action"] == "copy" and os.path.exists(last["target"]):
            if os.path.isdir(last["target"]):
                shutil.rmtree(last["target"])
            else:
                os.remove(last["target"])

    async def cleanup(self) -> None:
        self._operations.clear()
