from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable

from .database_logger import DatabaseLogger
from .database_models import MigrationInfo


class DatabaseEventType(str, Enum):
    CONNECT = "database.connect"
    DISCONNECT = "database.disconnect"
    QUERY_EXECUTED = "database.query.executed"
    QUERY_SLOW = "database.query.slow"
    QUERY_ERROR = "database.query.error"
    TRANSACTION_BEGIN = "database.transaction.begin"
    TRANSACTION_COMMIT = "database.transaction.commit"
    TRANSACTION_ROLLBACK = "database.transaction.rollback"
    POOL_ACQUIRE = "database.pool.acquire"
    POOL_RELEASE = "database.pool.release"
    POOL_EXHAUSTED = "database.pool.exhausted"
    MIGRATION_RUN = "database.migration.run"
    MIGRATION_ROLLBACK = "database.migration.rollback"
    MIGRATION_FAILED = "database.migration.failed"
    CONNECTION_LOST = "database.connection.lost"
    CONNECTION_RESTORED = "database.connection.restored"
    BACKUP_STARTED = "database.backup.started"
    BACKUP_COMPLETED = "database.backup.completed"
    BACKUP_FAILED = "database.backup.failed"


DatabaseEventHandler = Callable[["DatabaseEvent"], Awaitable[Any]]


@dataclass
class DatabaseEvent:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    type: DatabaseEventType = DatabaseEventType.CONNECT
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    source: str = ""


class DatabaseEventBus:
    """Event bus for database lifecycle events."""

    def __init__(self, logger: DatabaseLogger | None = None) -> None:
        self._handlers: dict[DatabaseEventType, list[DatabaseEventHandler]] = {}
        self._wildcard_handlers: list[DatabaseEventHandler] = []
        self._logger = logger or DatabaseLogger("database.events")

    def on(self, event_type: DatabaseEventType, handler: DatabaseEventHandler) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def on_any(self, handler: DatabaseEventHandler) -> None:
        self._wildcard_handlers.append(handler)

    def off(self, event_type: DatabaseEventType, handler: DatabaseEventHandler) -> None:
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    async def emit(self, event_type: DatabaseEventType, data: dict[str, Any] | None = None) -> None:
        event = DatabaseEvent(type=event_type, data=data or {})
        handlers: list[DatabaseEventHandler] = []

        handlers.extend(self._handlers.get(event_type, []))
        handlers.extend(self._wildcard_handlers)

        for handler in handlers:
            try:
                await handler(event)
            except Exception as exc:
                self._logger.error(f"Event handler failed for {event_type.value}: {exc}")

    def clear(self) -> None:
        self._handlers.clear()
        self._wildcard_handlers.clear()

    @property
    def handler_count(self) -> int:
        count = len(self._wildcard_handlers)
        for handlers in self._handlers.values():
            count += len(handlers)
        return count
