"""AIOS Conversation Memory — per-session message history.

Stores (role, content) exchanges per session; recall returns the most
recent N messages, optionally filtered by role.
"""

from __future__ import annotations

import time
import uuid
from typing import Any


class ConversationMemory:
    """Per-session conversation history."""

    def __init__(self, max_messages_per_session: int = 500) -> None:
        self._history: dict[str, list[dict[str, Any]]] = {}
        self._max = max_messages_per_session

    def store(self, content: Any, **meta: Any) -> dict[str, Any]:
        session_id = meta.get("session_id", "default")
        role = meta.get("role", "assistant")
        message = {
            "record_id": f"con-{uuid.uuid4().hex[:10]}",
            "role": role,
            "content": content,
            "timestamp": time.time(),
        }
        history = self._history.setdefault(session_id, [])
        history.append(message)
        if len(history) > self._max:
            self._history[session_id] = history[-self._max:]
        return message

    def recall(self, query: Any = None, limit: int = 5, **filters: Any) -> list[dict[str, Any]]:
        session_id = filters.get("session_id", "default")
        role = filters.get("role")
        history = self._history.get(session_id, [])
        matches = []
        for message in reversed(history):
            if role is not None and message["role"] != role:
                continue
            if query is not None and str(query).lower() not in str(message["content"]).lower():
                continue
            matches.append(message)
            if len(matches) >= limit:
                break
        return list(reversed(matches))

    def forget(self, record_id: str) -> bool:
        for history in self._history.values():
            before = len(history)
            history[:] = [m for m in history if m["record_id"] != record_id]
            if len(history) < before:
                return True
        return False

    def clear(self) -> None:
        self._history.clear()

    def stats(self) -> dict[str, Any]:
        return {
            "sessions": len(self._history),
            "messages": sum(len(h) for h in self._history.values()),
            "max_per_session": self._max,
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "sessions": sorted(self._history.keys()),
            "messages": sum(len(h) for h in self._history.values()),
        }
