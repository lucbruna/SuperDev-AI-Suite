from __future__ import annotations

import json
from typing import Any

from ..api_logger import APILogger
from ..api_metrics import APIMetrics
from ..api_models import APIRequest, APIResponse
from .mcp_handler import MCPHandler
from .mcp_protocol import MCPProtocol


class MCPServer:
    """Model Context Protocol server — accepts MCP JSON-RPC messages."""

    def __init__(
        self,
        logger: APILogger | None = None,
        metrics: APIMetrics | None = None,
    ) -> None:
        self.handler = MCPHandler(logger=logger)
        self._logger = logger or APILogger("mcp.server")
        self._metrics = metrics
        self._register_default_handlers()

    def _register_default_handlers(self) -> None:
        self.handler.register("ping", lambda params: "pong")
        self.handler.register("initialize", self._handle_initialize)
        self.handler.register("shutdown", self._handle_shutdown)

    async def _handle_initialize(self, params: dict[str, Any]) -> dict[str, Any]:
        return {
            "protocolVersion": MCPProtocol.JSON_RPC_VERSION,
            "capabilities": {
                "tools": {},
                "resources": {},
                "prompts": {},
            },
            "serverInfo": {
                "name": "SuperDev API Engine MCP",
                "version": "1.0.0",
            },
        }

    async def _handle_shutdown(self, params: dict[str, Any]) -> str:
        return "shutting_down"

    async def handle_request(self, request: APIRequest) -> APIResponse:
        body = request.body if isinstance(request.body, (str, bytes)) else b""
        if isinstance(body, str):
            body = body.encode("utf-8")

        try:
            result = await self.handler.handle(body)
            return APIResponse(
                status_code=200,
                body=result,
                headers={"content-type": "application/json"},
                request_id=request.request_id,
            )
        except Exception as e:
            self._logger.error("MCP server error", error=str(e))
            error_response = MCPProtocol.create_error(-32603, "Internal server error", request_id="unknown")
            return APIResponse(
                status_code=500,
                body=error_response,
                headers={"content-type": "application/json"},
                request_id=request.request_id,
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "mcp_server": "MCPServer",
            "handler": self.handler.to_dict(),
        }
