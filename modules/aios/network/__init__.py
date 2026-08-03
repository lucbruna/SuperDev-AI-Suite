"""Network package — proxy, firewall, dns, ports, http, websocket, grpc (Vol 12, Fase 27)."""
from __future__ import annotations

from modules.aios.network.acl import require_network_action
from modules.aios.network.dns import Dns
from modules.aios.network.firewall import Firewall
from modules.aios.network.grpc import Grpc
from modules.aios.network.http import Http
from modules.aios.network.network import NetworkRuntime, get_network_runtime
from modules.aios.network.ports import Ports
from modules.aios.network.proxy import Proxy
from modules.aios.network.websocket import WebSocket

__all__ = [
    "Dns",
    "Firewall",
    "Grpc",
    "Http",
    "NetworkRuntime",
    "Ports",
    "Proxy",
    "WebSocket",
    "get_network_runtime",
    "require_network_action",
]
