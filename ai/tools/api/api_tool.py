from __future__ import annotations

from typing import Any

from ...base.base_tool import BaseTool
from .auth import ApiAuth
from .client import ApiClient
from .request import ApiRequest
from .response import ApiResponse
from .webhook import ApiWebhook


class ApiTool(BaseTool):
    """Composite API tool for HTTP operations."""

    _name = "api"
    _description = "API operations: client, request, response, auth, webhook"
    _permissions = ["read", "write"]

    def __init__(self) -> None:
        self._client = ApiClient()
        self._request = ApiRequest()
        self._response = ApiResponse()
        self._auth = ApiAuth()
        self._webhook = ApiWebhook()

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

        if sub_tool == "client":
            return await self._client.execute(params)
        elif sub_tool == "request" or action in ("get", "post", "put", "patch", "delete"):
            return await self._request.execute(params)
        elif sub_tool == "response":
            return await self._response.execute(params)
        elif sub_tool == "auth":
            return await self._auth.execute(params)
        elif sub_tool == "webhook":
            return await self._webhook.execute(params)
        return {"success": False, "error": f"Unknown API action: {action}"}

    async def rollback(self) -> None:
        pass

    async def cleanup(self) -> None:
        for tool in (self._client, self._request, self._response, self._auth, self._webhook):
            await tool.cleanup()
