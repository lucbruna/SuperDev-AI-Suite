from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool
from .page import BrowserPage
from .navigation import BrowserNavigation
from .form import BrowserForm
from .screenshot import BrowserScreenshot
from .cookies import BrowserCookies


class BrowserTool(BaseTool):
    """Composite browser tool for web automation."""

    _name = "browser"
    _description = "Browser automation: page, navigation, form, screenshot, cookies"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._page = BrowserPage()
        self._nav = BrowserNavigation()
        self._form = BrowserForm()
        self._screenshot = BrowserScreenshot()
        self._cookies = BrowserCookies()

    def name(self) -> str:
        return self._name

    def description(self) -> str:
        return self._description

    def permissions(self) -> list[str]:
        return self._permissions

    async def validate(self, params: dict[str, Any]) -> bool:
        return "action" in params

    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        sub_tool = params.get("sub_tool", "")
        action = params.get("action", "")

        if sub_tool == "page" or action in ("open", "get_content", "get_title", "close"):
            return await self._page.execute(params)
        elif sub_tool == "navigation":
            return await self._nav.execute(params)
        elif sub_tool == "form":
            return await self._form.execute(params)
        elif sub_tool == "screenshot":
            return await self._screenshot.execute(params)
        elif sub_tool == "cookies":
            return await self._cookies.execute(params)
        return {"success": False, "error": f"Unknown browser action: {action}"}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        for tool in (self._page, self._nav, self._form, self._screenshot, self._cookies):
            await tool.cleanup()
