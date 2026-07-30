from __future__ import annotations

import json
from typing import Any, Callable

from ..api_logger import APILogger
from .mcp_protocol import MCPProtocol


class MCPHandler:
    """Handles MCP method calls by dispatching to registered handlers."""

    def __init__(self, logger: APILogger | None = None) -> None:
        self._handlers: dict[str, Callable] = {}
        self._logger = logger or APILogger("mcp.handler")

    def register(self, method: str, handler: Callable) -> None:
        self._handlers[method] = handler

    def unregister(self, method: str) -> None:
        self._handlers.pop(method, None)

    async def handle(self, raw: str | bytes) -> str:
        try:
            msg = MCPProtocol.parse_message(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            return MCPProtocol.create_error(-32700, f"Parse error: {e}")

        request_id = msg.get("id", "unknown")
        method = msg.get("method", "")
        params = msg.get("params", {})

        handler = self._handlers.get(method)
        if handler is None:
            self._logger.warning("MCP method not found", method=method)
            return MCPProtocol.create_error(-32601, f"Method not found: {method}", request_id=request_id)

        try:
            result = handler(params)
            if hasattr(result, "__await__"):
                result = await result
            return MCPProtocol.create_response(result, request_id=request_id)
        except Exception as e:
            self._logger.error("MCP handler error", method=method, error=str(e))
            return MCPProtocol.create_error(-32603, str(e), request_id=request_id)

    def list_methods(self) -> list[str]:
        return list(self._handlers.keys())

    def to_dict(self) -> dict[str, Any]:
        return {
            "handler": "MCPHandler",
            "methods": self.list_methods(),
            "count": len(self._handlers),
        }
