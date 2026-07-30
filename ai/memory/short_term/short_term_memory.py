from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from .active_agents import ActiveAgents
from .active_tasks import ActiveTasks
from .cleanup import Cleanup
from .expiration import Expiration
from .interaction_history import InteractionHistory
from .recent_events import RecentEvents
from .request_context import RequestContext
from .session_memory import SessionMemory
from .temporary_storage import TemporaryStorage
from .working_buffer import WorkingBuffer


class ShortTermMemory:
    """High-level facade for short-term memory operations."""

    def __init__(self, default_ttl: float = 300.0):
        self._default_ttl = default_ttl
        self._session = SessionMemory()
        self._buffer = WorkingBuffer()
        self._temporary = TemporaryStorage(default_ttl=default_ttl)
        self._request = RequestContext()
        self._history = InteractionHistory()
        self._tasks = ActiveTasks()
        self._agents = ActiveAgents()
        self._events = RecentEvents()
        self._cleanup = Cleanup()
        self._expiration = Expiration()

    @property
    def session(self) -> SessionMemory:
        return self._session

    @property
    def working_buffer(self) -> WorkingBuffer:
        return self._buffer

    @property
    def temporary(self) -> TemporaryStorage:
        return self._temporary

    @property
    def request(self) -> RequestContext:
        return self._request

    @property
    def history(self) -> InteractionHistory:
        return self._history

    @property
    def tasks(self) -> ActiveTasks:
        return self._tasks

    @property
    def agents(self) -> ActiveAgents:
        return self._agents

    @property
    def events(self) -> RecentEvents:
        return self._events

    @property
    def cleanup(self) -> Cleanup:
        return self._cleanup

    @property
    def expiration(self) -> Expiration:
        return self._expiration

    def store(self, key: str, data: Any, ttl: float | None = None) -> None:
        self._temporary.set(key, data, ttl or self._default_ttl)

    def retrieve(self, key: str) -> Any | None:
        return self._temporary.get(key)

    def delete(self, key: str) -> bool:
        return self._temporary.delete(key)

    def clear_session(self) -> None:
        self._session.clear()
        self._buffer.clear()
        self._temporary.clear()
        self._history.clear()
        self._tasks.clear()
        self._agents.clear()
        self._events.clear()

    def run_housekeeping(self) -> Dict[str, int]:
        expired = self._expiration.purge_expired(self._temporary)
        cleaned = self._cleanup.clean(self._temporary, self._buffer, self._history)
        self._events.record("housekeeping", {"expired": expired, "cleaned": cleaned})
        return {"expired": expired, "cleaned": cleaned}

    def snapshot(self) -> Dict[str, Any]:
        return {
            "session_size": len(self._session.data),
            "buffer_size": self._buffer.size,
            "temporary_count": self._temporary.count,
            "history_length": self._history.length,
            "active_tasks": self._tasks.count,
            "active_agents": self._agents.count,
            "events_count": self._events.count,
        }
