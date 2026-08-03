"""Network runtime — facade over network inspection tools (Vol 12, Fase 27)."""
from __future__ import annotations

from typing import Any

from modules.aios.network.acl import require_network_action
from modules.aios.network.dns import Dns
from modules.aios.network.firewall import Firewall
from modules.aios.network.grpc import Grpc
from modules.aios.network.http import Http
from modules.aios.network.ports import Ports
from modules.aios.network.proxy import Proxy
from modules.aios.network.websocket import WebSocket


class NetworkRuntime:
    """Facade over the network inspection tools.

    Stateless: every operation is stdlib-based and self-contained. ``close``
    is a no-op. The network stack is always available.
    """

    def __init__(self) -> None:
        self.proxy = Proxy()
        self.firewall = Firewall()
        self.dns = Dns()
        self.ports = Ports()
        self.http = Http()
        self.websocket = WebSocket()
        self.grpc = Grpc()

    async def available(self) -> bool:
        return True

    async def snapshot(self) -> dict[str, Any]:
        """Best-effort inventory; each tool degrades to None on error."""
        inventory: dict[str, Any] = {}
        try:
            inventory["proxy"] = self.proxy.get()
        except Exception:
            inventory["proxy"] = None
        try:
            inventory["firewall"] = self.firewall.status()
        except Exception:
            inventory["firewall"] = None
        try:
            inventory["dns"] = self.dns.resolve("localhost")
        except Exception:
            inventory["dns"] = None
        try:
            inventory["ports"] = self.ports.is_open("127.0.0.1", 1)
        except Exception:
            inventory["ports"] = None
        try:
            inventory["http"] = self.http.head("http://127.0.0.1:1")
        except Exception:
            inventory["http"] = None
        try:
            inventory["websocket"] = self.websocket.check("ws://127.0.0.1:1")
        except Exception:
            inventory["websocket"] = None
        try:
            inventory["grpc"] = self.grpc.available()
        except Exception:
            inventory["grpc"] = None
        return inventory

    async def close(self) -> None:
        """No-op — the network runtime is stateless."""


_network_runtime: NetworkRuntime | None = None


def get_network_runtime() -> NetworkRuntime:
    global _network_runtime
    if _network_runtime is None:
        _network_runtime = NetworkRuntime()
    return _network_runtime


__all__ = ["NetworkRuntime", "get_network_runtime", "require_network_action"]
