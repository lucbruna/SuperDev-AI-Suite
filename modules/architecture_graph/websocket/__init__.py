"""WebSocket and event infrastructure for the Architecture Graph module.

Provides a dependency-free in-process event bus (used by the scheduler and the
REST API to publish graph lifecycle events) and a connection manager for
pushing those events to live WebSocket clients.
"""
from __future__ import annotations

from modules.architecture_graph.websocket.events import EventBus, get_bus, publish
from modules.architecture_graph.websocket.manager import ConnectionManager, manager

__all__ = ["EventBus", "get_bus", "publish", "ConnectionManager", "manager"]
