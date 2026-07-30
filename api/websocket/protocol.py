from __future__ import annotations

import json
from typing import Any

CLOSE_CODES: dict[int, str] = {
    1000: "Normal Closure",
    1001: "Going Away",
    1002: "Protocol Error",
    1003: "Unsupported Data",
    1004: "Reserved",
    1005: "No Status Received",
    1006: "Abnormal Closure",
    1007: "Invalid Frame Payload Data",
    1008: "Policy Violation",
    1009: "Message Too Big",
    1010: "Mandatory Extension",
    1011: "Internal Server Error",
    1012: "Service Restart",
    1013: "Try Again Later",
    1014: "Bad Gateway",
    1015: "TLS Handshake",
}


def close_code_reason(code: int) -> str:
    """Get the reason phrase for a WebSocket close code."""
    return CLOSE_CODES.get(code, "Unknown")


def serialize_message(message: Any) -> str:
    """Serialize a message to JSON string for WebSocket transport."""
    if isinstance(message, str):
        return message
    return json.dumps(message, default=str, ensure_ascii=False)


SUPPORTED_SUBPROTOCOLS: list[str] = ["json", "msgpack"]
SUPPORTED_VERSIONS: list[str] = ["13"]
