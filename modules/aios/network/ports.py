"""Network ports — TCP connectivity checks (Vol 12, Fase 27)."""
from __future__ import annotations

import socket
from time import monotonic
from typing import Any

from modules.aios.network.acl import require_network_action
from modules.aios.kernel.kernel_logger import get_kernel_logger
from modules.aios.kernel.kernel_metrics import get_kernel_metrics


class Ports:
    """Probes TCP ports for reachability using stdlib sockets."""

    def __init__(self) -> None:
        self._logger = get_kernel_logger()
        self._metrics = get_kernel_metrics()

    def is_open(self, host: str, port: int, *, timeout: float = 2.0) -> dict[str, Any]:
        require_network_action("ports")
        started = monotonic()
        try:
            with socket.create_connection((host, port), timeout=timeout):
                open_ = True
        except OSError:
            open_ = False
        self._metrics.record_timing("network.ports", monotonic() - started)
        self._logger.log("network", f"ports: {host}:{port} open={open_}")
        return {"ok": True, "host": host, "port": port, "open": open_}

    def scan(self, host: str, ports: list[int], *, timeout: float = 1.0) -> dict[str, Any]:
        require_network_action("ports")
        open_ports: list[int] = []
        for port in ports:
            try:
                with socket.create_connection((host, port), timeout=timeout):
                    open_ports.append(port)
            except OSError:
                continue
        return {"ok": True, "host": host, "open_ports": open_ports}


__all__ = ["Ports"]
