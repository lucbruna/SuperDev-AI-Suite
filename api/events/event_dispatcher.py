from __future__ import annotations

import asyncio
import time
from typing import Any, Awaitable, Callable

from ..api_logger import APILogger
from .event_bus import Event, EventBus, EventPriority

EventHandler = Callable[[Event], Awaitable[Any]]


class EventDispatcher:
    """Dispatches events to registered handlers with retry, timeout, and debounce support."""

    def __init__(self, event_bus: EventBus, logger: APILogger | None = None) -> None:
        self._event_bus = event_bus
        self._logger = logger or APILogger(__name__)
        self._debounce_timers: dict[str, asyncio.Task] = {}
        self._retry_counts: dict[str, int] = {}

    async def dispatch_now(self, event: Event) -> list[Any]:
        """Dispatch synchronously and collect results."""
        results: list[Any] = []
        handlers: list[EventHandler] = []
        handlers.extend(self._event_bus._subscribers.get(event.topic, []))  # noqa: SLF001
        handlers.extend(self._event_bus._wildcard_subscribers)  # noqa: SLF001

        for handler in handlers:
            try:
                result = await handler(event)
                results.append(result)
            except Exception as exc:
                self._logger.error(f"Sync dispatch error for {handler.__name__}: {exc}")
                results.append(exc)
        return results

    async def dispatch_with_retry(
        self,
        event: Event,
        max_retries: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
    ) -> None:
        """Dispatch with exponential backoff retry."""
        last_exc: Exception | None = None
        for attempt in range(max_retries):
            try:
                results = await self.dispatch_now(event)
                if any(isinstance(r, Exception) for r in results):
                    raise RuntimeError(f"Handler returned error for {event.topic}")
                return
            except Exception as exc:
                last_exc = exc
                if attempt < max_retries - 1:
                    wait = delay * (backoff**attempt)
                    self._logger.warning(f"Retry {attempt + 1}/{max_retries} for {event.topic} in {wait:.1f}s")
                    await asyncio.sleep(wait)
        self._logger.error(f"All {max_retries} retries exhausted for {event.topic}: {last_exc}")

    async def dispatch_after(self, event: Event, delay: float) -> None:
        """Dispatch after a delay."""
        await asyncio.sleep(delay)
        await self._event_bus.publish(event)

    def debounce(self, key: str, event: Event, wait: float = 0.3) -> None:
        """Debounce event dispatch — only the last call within `wait` seconds fires."""
        if key in self._debounce_timers:
            self._debounce_timers[key].cancel()

        async def _debounced() -> None:
            await asyncio.sleep(wait)
            await self._event_bus.publish(event)
            del self._debounce_timers[key]

        self._debounce_timers[key] = asyncio.create_task(_debounced())

    def throttle(self, key: str, event: Event, interval: float = 1.0) -> None:
        """Throttle event dispatch — at most one per `interval` seconds."""
        now = time.monotonic()
        last = getattr(self, f"_last_throttle_{key}", 0.0)
        if now - last >= interval:
            setattr(self, f"_last_throttle_{key}", now)
            asyncio.create_task(self._event_bus.publish(event))
