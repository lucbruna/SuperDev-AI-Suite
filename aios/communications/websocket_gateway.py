"""AIOS WebSocket Gateway — connection registry and fan-out.

Tracks connected clients and supports unicast send and broadcast.
In-memory; a real deployment plugs this into a WebSocket server while
keeping the client registry contract.
"""

from __future__ import annotations

import time
import uuid
from typing import Any

Outbox = list[dict[str, Any]]


class WebSocketGateway:
    """Client registry with send/broadcast semantics."""

    def __init__(self) -> None:
        self._clients: dict[str, Outbox] = {}
        self._connected_at: dict[str, float] = {}

    def connect(self, client_id: str | None = None, metadata: dict[str, Any] | None = None) -> str:
        cid = client_id or f"ws-{uuid.uuid4().hex[:10]}"
        self._clients[cid] = []
        self._connected_at[cid] = time.time()
        if metadata:
            self._clients[cid].append({"event": "meta", "metadata": metadata})
        return cid

    def disconnect(self, client_id: str) -> bool:
        if client_id in self._clients:
            del self._clients[client_id]
            self._connected_at.pop(client_id, None)
            return True
        return False

    def clients(self) -> list[str]:
        return sorted(self._clients)

    def send(self, client_id: str, payload: Any) -> dict[str, Any]:
        if client_id not in self._clients:
            return {"ok": False, "error": f"unknown client: {client_id}"}
        self._clients[client_id].append({"payload": payload, "timestamp": time.time()})
        return {"ok": True, "client_id": client_id}

    def broadcast(self, payload: Any) -> dict[str, Any]:
        sent = 0
        for client_id in self._clients:
            self._clients[client_id].append({"payload": payload, "timestamp": time.time()})
            sent += 1
        return {"ok": True, "clients": sent}

    def drain(self, client_id: str) -> list[dict[str, Any]]:
        outbox = self._clients.get(client_id, [])
        if client_id in self._clients:
            self._clients[client_id] = []
        return outbox

    def snapshot(self) -> dict[str, Any]:
        return {
            "clients": self.clients(),
            "client_count": len(self._clients),
            "connected_at": dict(self._connected_at),
        }
