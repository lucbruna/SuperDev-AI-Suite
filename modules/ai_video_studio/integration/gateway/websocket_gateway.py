"""WebSocket Gateway — channel registration for realtime streams."""
from __future__ import annotations

from typing import Any


class WebSocketGateway:
    """Registers WebSocket channels."""

    def __init__(self) -> None:
        self._channels: dict[str, dict[str, Any]] = {}

    def register(self, channel: str, *, mode: str = "broadcast") -> dict[str, Any]:
        self._channels[channel] = {"channel": channel, "mode": mode}
        return {"registered": channel}

    def routes(self) -> dict[str, Any]:
        return {"channels": list(self._channels.values()), "count": len(self._channels)}


_websocket_gateway: WebSocketGateway | None = None


def get_websocket_gateway() -> WebSocketGateway:
    global _websocket_gateway
    if _websocket_gateway is None:
        _websocket_gateway = WebSocketGateway()
    return _websocket_gateway
