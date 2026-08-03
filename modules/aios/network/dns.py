"""Network DNS — host resolution via stdlib socket (Vol 12, Fase 27)."""
from __future__ import annotations

import socket
from time import monotonic
from typing import Any

from modules.aios.network.acl import require_network_action
from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_metrics import get_kernel_metrics


class Dns:
    """Resolves hostnames to addresses using the system resolver."""

    def __init__(self) -> None:
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    def resolve(self, host: str) -> dict[str, Any]:
        require_network_action("dns")
        started = monotonic()
        try:
            infos = socket.getaddrinfo(host, None)
        except socket.gaierror as exc:
            return {"ok": False, "host": host, "reason": str(exc)}
        addresses = sorted({info[4][0] for info in infos})
        self._metrics.record_timing("network.dns", monotonic() - started)
        self._logger.log("network", f"dns: resolved {host}")
        return {"ok": True, "host": host, "addresses": addresses}

    def lookup(self, host: str) -> dict[str, Any]:
        require_network_action("dns")
        try:
            return {"ok": True, "host": host, "ip": socket.gethostbyname(host)}
        except socket.gaierror as exc:
            return {"ok": False, "host": host, "reason": str(exc)}


__all__ = ["Dns"]
