from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class BrowserCookies(BaseTool):
    """Manage browser cookies."""

    _name = "browser_cookies"
    _description = "Manage browser cookies: list, get, set, delete, clear"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._cookies: dict[str, dict[str, str]] = {}

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
        page_id = params.get("page_id", "default")
        try:
            if page_id not in self._cookies:
                self._cookies[page_id] = {}

            if action == "list":
                return {"success": True, "cookies": self._cookies[page_id], "count": len(self._cookies[page_id])}
            elif action == "get":
                name = params.get("name", "")
                value = self._cookies[page_id].get(name)
                if value is None:
                    return {"success": False, "error": f"Cookie not found: {name}"}
                return {"success": True, "cookie": {"name": name, "value": value}}
            elif action == "set":
                name = params.get("name", "")
                value = params.get("value", "")
                self._cookies[page_id][name] = value
                return {"success": True, "message": f"Set cookie {name}={value}"}
            elif action == "delete":
                name = params.get("name", "")
                self._cookies[page_id].pop(name, None)
                return {"success": True, "message": f"Deleted cookie {name}"}
            elif action == "clear":
                self._cookies[page_id].clear()
                return {"success": True, "message": "Cleared all cookies"}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._cookies.clear()

    async def cleanup(self) -> None:
        self._cookies.clear()
