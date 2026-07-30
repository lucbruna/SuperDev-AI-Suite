from __future__ import annotations

import json
from typing import Any


class MCPProtocol:
    """Model Context Protocol message formatting and parsing."""

    JSON_RPC_VERSION = "2.0"

    @staticmethod
    def create_request(method: str, params: dict[str, Any] | None = None, request_id: str = "1") -> str:
        msg: dict[str, Any] = {
            "jsonrpc": MCPProtocol.JSON_RPC_VERSION,
            "id": request_id,
            "method": method,
        }
        if params:
            msg["params"] = params
        return json.dumps(msg, default=str, ensure_ascii=False)

    @staticmethod
    def create_response(result: Any, request_id: str = "1") -> str:
        msg = {
            "jsonrpc": MCPProtocol.JSON_RPC_VERSION,
            "id": request_id,
            "result": result,
        }
        return json.dumps(msg, default=str, ensure_ascii=False)

    @staticmethod
    def create_error(code: int, message: str, data: Any = None, request_id: str = "1") -> str:
        error: dict[str, Any] = {"code": code, "message": message}
        if data is not None:
            error["data"] = data
        msg = {
            "jsonrpc": MCPProtocol.JSON_RPC_VERSION,
            "id": request_id,
            "error": error,
        }
        return json.dumps(msg, default=str, ensure_ascii=False)

    @staticmethod
    def parse_message(raw: str | bytes) -> dict[str, Any]:
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        return json.loads(raw)

    @staticmethod
    def is_request(msg: dict[str, Any]) -> bool:
        return "method" in msg and "id" in msg

    @staticmethod
    def is_response(msg: dict[str, Any]) -> bool:
        return "result" in msg or "error" in msg

    @staticmethod
    def is_notification(msg: dict[str, Any]) -> bool:
        return "method" in msg and "id" not in msg

    ERROR_CODES: dict[int, str] = {
        -32700: "Parse Error",
        -32600: "Invalid Request",
        -32601: "Method not found",
        -32602: "Invalid params",
        -32603: "Internal error",
        -32000: "Server error",
    }
