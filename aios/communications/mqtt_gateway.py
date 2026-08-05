"""AIOS MQTT Gateway — topic pub/sub emulation.

In-memory MQTT-style topic messaging: subscribers register per topic,
published payloads fan out to matching subscribers. A real deployment
plugs into an MQTT broker while keeping this contract.
"""

from __future__ import annotations

import fnmatch
import time
import uuid
from typing import Any


class MQTTGateway:
    """In-memory topic-based pub/sub (MQTT semantics)."""

    def __init__(self) -> None:
        self._subscriptions: dict[str, list[tuple[str, str]]] = {}  # topic -> [(sub_id, client)]
        self._outbox: dict[str, list[dict[str, Any]]] = {}
        self._messages: list[dict[str, Any]] = []

    def subscribe(self, topic: str, client_id: str, sub_id: str | None = None) -> str:
        sid = sub_id or f"sub-{uuid.uuid4().hex[:10]}"
        self._subscriptions.setdefault(topic, []).append((sid, client_id))
        self._outbox.setdefault(client_id, [])
        return sid

    def unsubscribe(self, sub_id: str) -> bool:
        for topic, subs in self._subscriptions.items():
            before = len(subs)
            subs[:] = [s for s in subs if s[0] != sub_id]
            if len(subs) < before:
                return True
        return False

    def publish(self, topic: str, payload: Any, *, retain: bool = False) -> dict[str, Any]:
        message = {
            "message_id": f"mqtt-{uuid.uuid4().hex[:10]}",
            "topic": topic,
            "payload": payload,
            "timestamp": time.time(),
        }
        delivered = 0
        for pattern, subs in self._subscriptions.items():
            if not fnmatch.fnmatch(topic, pattern):
                continue
            for _sid, client_id in subs:
                self._outbox.setdefault(client_id, []).append(message)
                delivered += 1
        self._messages.append(message)
        return {"ok": True, "message_id": message["message_id"], "delivered": delivered}

    def drain(self, client_id: str) -> list[dict[str, Any]]:
        outbox = self._outbox.get(client_id, [])
        self._outbox[client_id] = []
        return outbox

    def snapshot(self) -> dict[str, Any]:
        return {
            "topics": sorted(self._subscriptions),
            "subscription_count": sum(len(s) for s in self._subscriptions.values()),
            "messages": len(self._messages),
            "clients": sorted(self._outbox),
        }
