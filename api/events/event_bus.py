from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable

from ..api_logger import APILogger


class EventPriority(int, Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


EventHandler = Callable[["Event"], Awaitable[Any]]


@dataclass
class Event:
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    topic: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    source: str = ""
    priority: EventPriority = EventPriority.NORMAL
    timestamp: float = field(default_factory=time.monotonic)
    metadata: dict[str, Any] = field(default_factory=dict)

    _counter: int = 0

    @classmethod
    def create(
        cls,
        topic: str,
        data: dict[str, Any] | None = None,
        source: str = "",
        priority: EventPriority = EventPriority.NORMAL,
    ) -> Event:
        cls._counter += 1
        return cls(
            topic=topic,
            data=data or {},
            source=source,
            priority=priority,
            timestamp=time.time() + cls._counter * 1e-3,
        )


class EventBus:
    """Publish/subscribe event bus with priority queuing and async dispatch."""

    def __init__(self, logger: APILogger | None = None) -> None:
        self._subscribers: dict[str, list[EventHandler]] = {}
        self._wildcard_subscribers: list[EventHandler] = []
        self._once_subscribers: dict[str, list[EventHandler]] = {}
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._running = False
        self._workers: list[asyncio.Task] = []
        self._logger = logger or APILogger(__name__)
        self._lock = asyncio.Lock()

    def subscribe(self, topic: str, handler: EventHandler) -> None:
        if topic == "*":
            self._wildcard_subscribers.append(handler)
        else:
            self._subscribers.setdefault(topic, []).append(handler)

    def subscribe_once(self, topic: str, handler: EventHandler) -> None:
        self._once_subscribers.setdefault(topic, []).append(handler)

    def unsubscribe(self, topic: str, handler: EventHandler) -> None:
        if topic == "*":
            if handler in self._wildcard_subscribers:
                self._wildcard_subscribers.remove(handler)
        else:
            handlers = self._subscribers.get(topic, [])
            if handler in handlers:
                handlers.remove(handler)

    async def publish(self, event: Event) -> None:
        await self._queue.put((event.priority.value, event))

    async def publish_sync(self, topic: str, data: dict[str, Any] | None = None, source: str = "") -> None:
        event = Event.create(topic=topic, data=data, source=source)
        await self.publish(event)

    async def start(self, num_workers: int = 4) -> None:
        self._running = True
        self._workers = [
            asyncio.create_task(self._worker_loop(), name=f"event-worker-{i}")
            for i in range(num_workers)
        ]
        self._logger.info(f"Event bus started with {num_workers} workers")

    async def stop(self) -> None:
        self._running = False
        for worker in self._workers:
            worker.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()
        self._logger.info("Event bus stopped")

    async def _worker_loop(self) -> None:
        while self._running:
            try:
                _, event = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                await self._dispatch(event)
            except asyncio.TimeoutError:
                continue
            except Exception as exc:
                self._logger.error(f"Event worker error: {exc}")

    async def _dispatch(self, event: Event) -> None:
        handlers: list[EventHandler] = []

        # Topic-specific subscribers
        handlers.extend(self._subscribers.get(event.topic, []))

        # Wildcard subscribers
        handlers.extend(self._wildcard_subscribers)

        # Once subscribers (consumed after dispatch)
        async with self._lock:
            once_handlers = self._once_subscribers.pop(event.topic, [])
            handlers.extend(once_handlers)

        results = await asyncio.gather(
            *[handler(event) for handler in handlers],
            return_exceptions=True,
        )
        for handler, result in zip(handlers, results):
            if isinstance(result, Exception):
                self._logger.error(f"Handler {handler.__name__} failed for {event.topic}: {result}")

    @property
    def subscriber_count(self) -> int:
        count = len(self._wildcard_subscribers)
        for handlers in self._subscribers.values():
            count += len(handlers)
        return count
