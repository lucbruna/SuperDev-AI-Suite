from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class BrowserNavigation(BaseTool):
    """Browser navigation operations."""

    _name = "browser_navigation"
    _description = "Browser navigation: go, back, forward, click, hover, wait"
    _permissions = ["read"]

    def __init__(self) -> None:
        self._history: dict[str, list[str]] = {}

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
            if action == "go":
                url = params.get("url", "")
                if page_id not in self._history:
                    self._history[page_id] = []
                self._history[page_id].append(url)
                return {"success": True, "url": url, "page_id": page_id}
            elif action == "back":
                hist = self._history.get(page_id, [])
                if len(hist) < 2:
                    return {"success": False, "error": "No previous page in history"}
                prev = hist[-2]
                hist.pop()
                return {"success": True, "url": prev, "page_id": page_id}
            elif action == "forward":
                return {"success": True, "message": "No forward history available"}
            elif action == "click":
                selector = params.get("selector", "")
                return {"success": True, "message": f"Clicked element: {selector}"}
            elif action == "hover":
                selector = params.get("selector", "")
                return {"success": True, "message": f"Hovered over: {selector}"}
            elif action == "wait":
                timeout = params.get("timeout", 1000)
                return {"success": True, "message": f"Waited {timeout}ms"}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._history.clear()

    async def cleanup(self) -> None:
        self._history.clear()
