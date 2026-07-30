from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool


class ApiRequest(BaseTool):
    """Execute API requests."""

    _name = "api_request"
    _description = "Execute API requests: get, post, put, patch, delete"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._request_log: list[dict[str, Any]] = []

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
        url = params.get("url", "")
        headers = params.get("headers", {})
        body = params.get("body", {})
        try:
            entry = {"action": action.upper(), "url": url, "headers": headers, "body": body}
            self._request_log.append(entry)
            return {
                "success": True,
                "status_code": 200,
                "data": {"message": f"Mock {action.upper()} response", "url": url},
                "headers": {"content-type": "application/json"},
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def rollback(self) -> None:
        self._request_log.clear()

    async def cleanup(self) -> None:
        self._request_log.clear()
