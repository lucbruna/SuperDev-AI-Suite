"""Network proxy — inspect proxy configuration (Vol 12, Fase 27)."""
from __future__ import annotations

import os
from typing import Any

from modules.aios.network.acl import require_network_action
from modules.aios.kernel.kernel_logger import get_kernel_logger


class Proxy:
    """Reads the current HTTP/HTTPS proxy configuration from the environment."""

    def __init__(self) -> None:
        self._logger = get_kernel_logger()

    def get(self) -> dict[str, Any]:
        require_network_action("proxy")
        config = {
            "http": os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy"),
            "https": os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy"),
            "no_proxy": os.environ.get("NO_PROXY") or os.environ.get("no_proxy"),
        }
        self._logger.log("network", "proxy: read environment configuration")
        return {"ok": True, "config": config}

    def test(self) -> dict[str, Any]:
        require_network_action("proxy")
        config = self.get()["config"]
        active = bool(config["http"] or config["https"])
        return {"ok": True, "active": active, "config": config}


__all__ = ["Proxy"]
