from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class BrowserForm(BaseTool):
    """Browser form interactions."""

    _name = "browser_form"
    _description = "Browser form interactions: fill, select, submit, clear, get_value"
    _permissions = ["write"]

    def __init__(self) -> None:
        self._form_data: dict[str, dict[str, str]] = {}

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
            if page_id not in self._form_data:
                self._form_data[page_id] = {}

            if action == "fill":
                selector = params.get("selector", "")
                value = params.get("value", "")
                self._form_data[page_id][selector] = value
                return {"success": True, "message": f"Filled {selector} with '{value}'"}
            elif action == "select":
                selector = params.get("selector", "")
                option = params.get("option", "")
                self._form_data[page_id][selector] = option
                return {"success": True, "message": f"Selected '{option}' in {selector}"}
            elif action == "submit":
                selector = params.get("selector", "form")
                return {"success": True, "message": f"Submitted form: {selector}"}
            elif action == "clear":
                selector = params.get("selector", "")
                self._form_data[page_id].pop(selector, None)
                return {"success": True, "message": f"Cleared {selector}"}
            elif action == "get_value":
                selector = params.get("selector", "")
                value = self._form_data[page_id].get(selector, "")
                return {"success": True, "selector": selector, "value": value}
            return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._form_data.clear()

    async def cleanup(self) -> None:
        self._form_data.clear()
