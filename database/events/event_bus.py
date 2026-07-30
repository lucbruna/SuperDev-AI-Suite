from __future__ import annotations

from enum import Enum
from typing import Any

from ..database_models import MigrationInfo
from ..database_interfaces import IDatabaseEventListener


class DatabaseEventType(str, Enum):
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    QUERY = "query"
    ERROR = "error"
    MIGRATION = "migration"
    POOL_STATS = "pool_stats"


class DatabaseEventBus:
    """Simple pub-sub event bus for database events.

    Listeners registered here receive events asynchronously.
    """

    def __init__(self) -> None:
        self._listeners: dict[DatabaseEventType, list[IDatabaseEventListener]] = {
            event_type: [] for event_type in DatabaseEventType
        }

    def register(self, event_type: DatabaseEventType, listener: IDatabaseEventListener) -> None:
        self._listeners.setdefault(event_type, []).append(listener)

    def unregister(self, event_type: DatabaseEventType, listener: IDatabaseEventListener) -> None:
        self._listeners[event_type] = [
            l for l in self._listeners.get(event_type, []) if l is not listener
        ]

    async def emit(self, event_type: DatabaseEventType, **kwargs: Any) -> None:
        for listener in self._listeners.get(event_type, []):
            try:
                if event_type == DatabaseEventType.CONNECT:
                    await listener.on_connect(kwargs.get("driver_name", ""))
                elif event_type == DatabaseEventType.DISCONNECT:
                    await listener.on_disconnect(kwargs.get("driver_name", ""))
                elif event_type == DatabaseEventType.QUERY:
                    await listener.on_query(
                        kwargs.get("query", ""),
                        kwargs.get("duration_ms", 0.0),
                    )
                elif event_type == DatabaseEventType.ERROR:
                    await listener.on_error(
                        kwargs.get("error", Exception("unknown")),
                        kwargs.get("query"),
                    )
                elif event_type == DatabaseEventType.MIGRATION:
                    mig = kwargs.get("migration")
                    if isinstance(mig, MigrationInfo):
                        await listener.on_migration(mig)
            except Exception:
                pass  # listener isolation

    def listeners(self, event_type: DatabaseEventType) -> list[IDatabaseEventListener]:
        return list(self._listeners.get(event_type, []))


__all__ = [
    "DatabaseEventType",
    "DatabaseEventBus",
]
