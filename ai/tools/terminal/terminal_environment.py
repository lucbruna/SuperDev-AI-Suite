from __future__ import annotations

import os
from typing import Any

from ...base.base_tool import BaseTool


class TerminalEnvironment(BaseTool):
    _name = "terminal_environment"
    _description = "Manage terminal environment variables"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._custom_vars: dict[str, str] = {}

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return True

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        action = params.get("action", "get")
        name = params.get("name", "")
        try:
            if action == "get":
                value = os.environ.get(name) or self._custom_vars.get(name)
                return {"success": True, "name": name, "value": value}
            elif action == "set":
                value = params.get("value", "")
                self._custom_vars[name] = value
                return {"success": True, "name": name, "value": value}
            elif action == "list":
                env_vars = {k: v for k, v in os.environ.items()}
                env_vars.update(self._custom_vars)
                return {"success": True, "variables": env_vars, "count": len(env_vars)}
            elif action == "delete":
                self._custom_vars.pop(name, None)
                return {"success": True, "deleted": name}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._custom_vars.clear()

    async def cleanup(self) -> None:
        self._custom_vars.clear()
