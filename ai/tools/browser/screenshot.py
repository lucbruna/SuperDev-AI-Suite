from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class BrowserScreenshot(BaseTool):
    """Take browser screenshots."""

    _name = "browser_screenshot"
    _description = "Take browser screenshots: capture, capture_full_page, capture_element"
    _permissions = ["read"]

    def __init__(self) -> None:
        self._screenshots: list[dict[str, Any]] = []

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
            if action == "capture":
                screenshot = {
                    "page_id": page_id,
                    "format": params.get("format", "png"),
                    "data": "[base64-encoded-image]",
                }
                self._screenshots.append(screenshot)
                return {"success": True, "screenshot": screenshot}
            elif action == "capture_full_page":
                screenshot = {
                    "page_id": page_id,
                    "format": params.get("format", "png"),
                    "full_page": True,
                    "data": "[base64-encoded-full-page-image]",
                }
                self._screenshots.append(screenshot)
                return {"success": True, "screenshot": screenshot}
            elif action == "capture_element":
                selector = params.get("selector", "")
                screenshot = {
                    "page_id": page_id,
                    "selector": selector,
                    "format": params.get("format", "png"),
                    "data": "[base64-encoded-element-image]",
                }
                self._screenshots.append(screenshot)
                return {"success": True, "screenshot": screenshot}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._screenshots.clear()

    async def cleanup(self) -> None:
        self._screenshots.clear()
