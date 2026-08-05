"""Notification channel base — every sender writes to a local outbox."""
from __future__ import annotations

import time
from typing import Any


class ChannelSender:
    """Base sender: validates recipients and records to a local outbox."""

    channel = "channel"

    def __init__(self, limit: int = 100) -> None:
        self._outbox: list[dict[str, Any]] = []
        self._limit = limit

    def send(self, *, recipient: str = "", subject: str = "", body: str = "",
             **meta: Any) -> dict[str, Any]:
        missing = [k for k, v in (("recipient", recipient), ("body", body)) if not v]
        if missing:
            return {"ok": False, "error": f"missing field(s): {', '.join(missing)}"}
        entry = {
            "channel": self.channel,
            "recipient": recipient,
            "subject": subject,
            "body": body,
            "ts": round(time.time(), 3),
            **meta,
        }
        self._outbox.append(entry)
        if len(self._outbox) > self._limit:
            self._outbox = self._outbox[-self._limit:]
        return {"ok": True, "channel": self.channel, "queued": len(self._outbox)}

    def outbox(self) -> dict[str, Any]:
        return {"channel": self.channel, "queued": len(self._outbox)}
