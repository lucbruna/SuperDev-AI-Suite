"""Event engine: facade over bus, router, queue, and scheduler."""

from __future__ import annotations

import logging
from typing import Any, Callable

from .event_bus import EventBus
from .routing import EventRouter
from .scheduler import EventScheduler


class EventEngine:
    """Facade for the events subsystem."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.events")
        self.bus = EventBus()
        self.router = self.bus.router
        self.queue = self.bus.queue
        self.scheduler = EventScheduler(self.bus)

    def on(self, event_type: str, handler: Callable[[dict[str, Any]], None]) -> None:
        self.bus.subscribe(event_type, handler)

    def route(self, pattern: str, target: str) -> None:
        self.router.add_rule(pattern, target)

    def emit(self, event_type: str, payload: dict[str, Any]) -> str:
        return self.bus.publish(event_type, payload)

    def drain(self, limit: int = 100) -> int:
        return self.bus.process(limit)

    def stats(self) -> dict[str, Any]:
        return {
            "published": len(self.bus.published()),
            "queued": self.queue.size(),
            "subscribers": self.bus.subscriber_count(),
            "scheduled": len(self.scheduler.jobs()),
        }
