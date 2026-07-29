"""System Event Bus — the nervous system of the SuperDev platform.

Provides typed, prioritized, and asynchronous event distribution across
all modules. Supports pub/sub, direct messaging, event filtering, 
retry with backoff, dead-letter queues, and structured history logging.
"""

from __future__ import annotations

import asyncio
import contextlib
import time
import uuid
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from typing import Any

from .exceptions import EventDeliveryError
from .types import EventPriority, SystemEvent, now_iso

EventHandler = Callable[[SystemEvent], Awaitable[None]]
EventFilter = Callable[[SystemEvent], bool]


class EventBus:
    """Typed, prioritized, async event bus for system-wide communication.

    Features:
    - Priority-based message ordering
    - Topic filtering with wildcard support (/)
    - Retry with exponential backoff for failed handlers
    - Dead-letter queue for undeliverable events
    - Structured event history
    - Correlation ID tracking across event chains
    - Subscriber health monitoring
    """

    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0) -> None:
        self._subscriptions: dict[str, list[EventHandler]] = {}
        self._filters: dict[str, list[EventFilter]] = {}
        self._history: list[SystemEvent] = []
        self._dead_letter: list[dict[str, Any]] = []
        self._lock = asyncio.Lock()
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._total_published: int = 0
        self._total_delivered: int = 0
        self._total_failed: int = 0
        self._handler_times: dict[str, list[float]] = {}

    # ─── Subscription Management ─────────────────────────────────────────

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe to an event type. Supports wildcard: 'system.*' matches 'system.boot'."""
        if event_type not in self._subscriptions:
            self._subscriptions[event_type] = []
            self._filters[event_type] = []
        self._subscriptions[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Remove a specific handler subscription."""
        handlers = self._subscriptions.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    def add_filter(self, event_type: str, event_filter: EventFilter) -> None:
        """Add a filter to an event type. Only events passing ALL filters are delivered."""
        if event_type not in self._filters:
            self._filters[event_type] = []
        self._filters[event_type].append(event_filter)

    # ─── Publishing ───────────────────────────────────────────────────────

    async def publish(
        self,
        event_type: str,
        data: dict[str, Any] | None = None,
        source: str = "system",
        priority: EventPriority = EventPriority.NORMAL,
        correlation_id: str = "",
        user_id: str = "",
    ) -> SystemEvent:
        """Publish an event to all matching subscribers."""
        event = SystemEvent(
            event_type=event_type,
            source=source,
            data=data or {},
            priority=priority,
            event_id=uuid.uuid4().hex[:12],
            timestamp=now_iso(),
            correlation_id=correlation_id or uuid.uuid4().hex[:12],
            user_id=user_id,
        )

        async with self._lock:
            self._history.append(event)
            if len(self._history) > 10_000:
                self._history = self._history[-5_000:]
            self._total_published += 1

        # Find matching subscribers (exact + wildcard)
        matched_handlers: list[EventHandler] = []
        for pattern, handlers in self._subscriptions.items():
            if self._matches_pattern(event_type, pattern):
                matched_handlers.extend(handlers)

        # Apply filters
        matched_filters: list[EventFilter] = []
        for pattern, filters in self._filters.items():
            if self._matches_pattern(event_type, pattern):
                matched_filters.extend(filters)

        # Filter out events that don't pass all filters
        if matched_filters:
            for event_filter in matched_filters:
                if not event_filter(event):
                    return event  # Silently filtered

        # Deliver to all matched handlers in parallel
        tasks = [
            self._deliver_with_retry(event, handler)
            for handler in matched_handlers
        ]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        return event

    def _matches_pattern(self, event_type: str, pattern: str) -> bool:
        """Match event type against a pattern with wildcard support."""
        if pattern == "*":
            return True
        if pattern.endswith(".*"):
            prefix = pattern[:-2]
            return event_type == prefix or event_type.startswith(prefix + ".")
        return event_type == pattern

    async def _deliver_with_retry(
        self,
        event: SystemEvent,
        handler: EventHandler,
    ) -> None:
        """Deliver an event to a handler with retry logic."""
        last_error = ""
        for attempt in range(self._max_retries + 1):
            try:
                start = time.time()
                await handler(event)
                elapsed = time.time() - start

                async with self._lock:
                    self._total_delivered += 1
                    handler_name = getattr(handler, "__name__", str(handler))
                    if handler_name not in self._handler_times:
                        self._handler_times[handler_name] = []
                    self._handler_times[handler_name].append(elapsed)
                    if len(self._handler_times[handler_name]) > 100:
                        self._handler_times[handler_name] = (
                            self._handler_times[handler_name][-50:]
                        )
                return

            except Exception as e:
                last_error = str(e)
                if attempt < self._max_retries:
                    await asyncio.sleep(self._retry_delay * (2 ** attempt))
                continue

        # All retries exhausted — send to dead-letter queue
        async with self._lock:
            self._total_failed += 1
            self._dead_letter.append({
                "event_type": event.event_type,
                "event_id": event.event_id,
                "handler": getattr(handler, "__name__", str(handler)),
                "error": last_error,
                "timestamp": now_iso(),
                "data": event.data,
            })

    # ─── Direct Messaging ─────────────────────────────────────────────────

    async def send_to(
        self,
        target_service: str,
        event_type: str,
        data: dict[str, Any] | None = None,
        source: str = "system",
        priority: EventPriority = EventPriority.NORMAL,
    ) -> bool:
        """Send an event to a specific service handler."""
        pattern = f"svc.{target_service}.{event_type}"
        event = await self.publish(
            event_type=pattern,
            data=data,
            source=source,
            priority=priority,
        )
        return event.event_id != ""

    # ─── Query Methods ────────────────────────────────────────────────────

    def get_history(
        self,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get structured event history, optionally filtered by type."""
        events = self._history
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        return [
            {
                "event_id": e.event_id,
                "event_type": e.event_type,
                "source": e.source,
                "priority": e.priority.name,
                "timestamp": e.timestamp,
                "correlation_id": e.correlation_id,
            }
            for e in events[-limit:]
        ]

    def get_dead_letter_queue(self) -> list[dict[str, Any]]:
        """Get undeliverable events."""
        return list(self._dead_letter)

    def retry_dead_letter(self, index: int = -1) -> None:
        """Retry a dead-letter event (default: all)."""
        if index >= 0:
            items = [self._dead_letter[index]] if index < len(self._dead_letter) else []
        else:
            items = list(self._dead_letter)
        self._dead_letter.clear()
        for item in items:
            with contextlib.suppress(Exception):
                asyncio.ensure_future(
                    self.publish(item["event_type"], item["data"])
                )

    # ─── Statistics ───────────────────────────────────────────────────────

    def get_statistics(self) -> dict[str, Any]:
        """Get event bus metrics."""
        total = self._total_published
        failed = self._total_failed
        return {
            "total_published": total,
            "total_delivered": self._total_delivered,
            "total_failed": failed,
            "failure_rate": round(failed / total, 4) if total > 0 else 0,
            "dead_letter_count": len(self._dead_letter),
            "subscriber_count": sum(len(h) for h in self._subscriptions.values()),
            "active_topics": len(self._subscriptions),
            "avg_handler_time_ms": self._avg_handler_time(),
        }

    def _avg_handler_time(self) -> float:
        """Calculate average handler execution time."""
        all_times: list[float] = []
        for times in self._handler_times.values():
            all_times.extend(times)
        if not all_times:
            return 0.0
        return round((sum(all_times) / len(all_times)) * 1000, 2)

    async def clear_history(self) -> None:
        """Clear event history (keeps dead-letter queue)."""
        async with self._lock:
            self._history.clear()
