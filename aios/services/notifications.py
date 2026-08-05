"""AIOS Notification Service — channel-based in-memory delivery.

Supports direct send to a recipient and broadcast to a channel.
A real deployment may route to email/SMS/push behind the same API.
"""

from __future__ import annotations

import time
import uuid
from typing import Any


class NotificationService:
    """In-memory notification delivery with channels."""

    def __init__(self, max_delivered: int = 5_000) -> None:
        self._channels: dict[str, list[str]] = {}
        self._delivered: list[dict[str, Any]] = []
        self._max = max_delivered

    def subscribe(self, channel: str, recipient: str) -> "NotificationService":
        self._channels.setdefault(channel, []).append(recipient)
        return self

    def send(self, title: str, body: str, recipient: str, channel: str = "direct") -> dict[str, Any]:
        notification = {
            "notification_id": f"ntf-{uuid.uuid4().hex[:10]}",
            "title": title,
            "body": body,
            "recipient": recipient,
            "channel": channel,
            "timestamp": time.time(),
        }
        self._delivered.append(notification)
        if len(self._delivered) > self._max:
            self._delivered = self._delivered[-self._max:]
        return notification

    def broadcast(self, channel: str, title: str, body: str) -> dict[str, Any]:
        recipients = self._channels.get(channel, [])
        sent = [self.send(title, body, recipient, channel=channel) for recipient in recipients]
        return {"ok": True, "channel": channel, "recipients": len(sent)}

    def received_by(self, recipient: str, limit: int = 50) -> list[dict[str, Any]]:
        return [n for n in reversed(self._delivered) if n["recipient"] == recipient][:limit]

    def snapshot(self) -> dict[str, Any]:
        return {
            "channels": {c: len(r) for c, r in sorted(self._channels.items())},
            "delivered": len(self._delivered),
        }
