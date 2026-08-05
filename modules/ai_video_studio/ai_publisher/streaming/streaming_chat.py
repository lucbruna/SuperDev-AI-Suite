"""Streaming Chat — chat moderation and engagement (Volume 7)."""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_BLOCKED_WORDS = {"spam", "scam", "free-followers"}


class StreamingChat:
    """Moderate chat messages and summarize engagement."""

    def __init__(self) -> None:
        self._messages: list[dict] = []

    def ingest(self, *, user: str = "", text: str = "") -> dict:
        """Record a chat message, flagging blocked words."""
        lowered = text.lower()
        flagged = any(word in lowered for word in _BLOCKED_WORDS)
        message = {"user": user or "viewer", "text": text, "blocked": flagged}
        self._messages.append(message)
        return message

    def flagged(self) -> list[dict]:
        return [m for m in self._messages if m.get("blocked")]

    def sentiment(self) -> dict:
        """Crude sentiment estimate based on keyword presence."""
        positives = sum(1 for m in self._messages if any(w in m["text"].lower() for w in ("love", "great", "awesome", "lol")))
        negatives = sum(1 for m in self._messages if any(w in m["text"].lower() for w in ("bad", "boring", "hate")))
        total = len(self._messages) or 1
        return {"positive": round(positives / total, 2), "negative": round(negatives / total, 2)}

    def stats(self) -> dict[str, int]:
        return {"messages": len(self._messages)}


_CHAT: StreamingChat | None = None


def get_streaming_chat() -> StreamingChat:
    """Get the module-level singleton streaming chat."""
    global _CHAT
    if _CHAT is None:
        _CHAT = StreamingChat()
    return _CHAT
