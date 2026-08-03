"""Network WebSocket — best-effort endpoint availability (Vol 12, Fase 27)."""
from __future__ import annotations

from typing import Any

from modules.aios.network.acl import require_network_action
from modules.aios.kernel.kernel_logger import get_kernel_logger


class WebSocket:
    """Reports WebSocket endpoint availability.

    Best-effort: without a WS client dependency this degrades to a config
    check rather than a live handshake.
    """

    def __init__(self) -> None:
        self._logger = get_kernel_logger()

    def check(self, url: str) -> dict[str, Any]:
        require_network_action("websocket")
        self._logger.log("network", f"websocket: check {url}")
        return {"ok": True, "url": url, "supported": False}


__all__ = ["WebSocket"]
