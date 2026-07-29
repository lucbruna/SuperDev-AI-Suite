"""
Event Bus - Internal communication system for agent coordination
"""

import asyncio
from collections import defaultdict
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID

from enterprise_ai_core.models import Event, EventType


class EventBus:
    """Event-driven communication between agents and services"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.config = orchestrator.config
        self._subscribers: Dict[EventType, List[Callable]] = defaultdict(list)
        self._wildcard_subscribers: List[Callable] = []
        self._event_history: List[Event] = []
        self._max_history = 10000
        self._running = False
        self._queue: asyncio.Queue = asyncio.Queue()
        self._processor_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        self._running = True
        self._processor_task = asyncio.create_task(self._process_events())

    async def stop(self) -> None:
        self._running = False
        if self._processor_task:
            self._processor_task.cancel()
            try:
                await self._processor_task
            except asyncio.CancelledError:
                pass

    async def publish(self, event: Event) -> None:
        await self._queue.put(event)

    async def subscribe(self, event_type: EventType, handler: Callable) -> None:
        self._subscribers[event_type].append(handler)

    async def unsubscribe(self, event_type: EventType, handler: Callable) -> bool:
        if handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)
            return True
        return False

    async def subscribe_all(self, handler: Callable) -> None:
        self._wildcard_subscribers.append(handler)

    async def _process_events(self) -> None:
        while self._running:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                await self._dispatch(event)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                await self.orchestrator.audit_manager.log(
                    event_type="event_bus.error",
                    action="process_event",
                    outcome="failure",
                    details={"error": str(e)},
                    severity="error",
                )

    async def _dispatch(self, event: Event) -> None:
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]

        handlers = self._subscribers.get(event.type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                await self.orchestrator.audit_manager.log(
                    event_type="event_bus.handler_error",
                    action="dispatch_event",
                    outcome="failure",
                    details={"event_type": event.type.value, "error": str(e)},
                    severity="error",
                )

        for handler in self._wildcard_subscribers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception:
                pass

    def get_history(
        self,
        event_type: Optional[EventType] = None,
        limit: int = 100,
        since: Optional[datetime] = None,
    ) -> List[Event]:
        events = self._event_history

        if event_type:
            events = [e for e in events if e.type == event_type]

        if since:
            events = [e for e in events if e.timestamp >= since]

        return events[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        return {
            "queue_size": self._queue.qsize(),
            "history_size": len(self._event_history),
            "subscribers": {et.value: len(h) for et, h in self._subscribers.items()},
            "wildcard_subscribers": len(self._wildcard_subscribers),
            "running": self._running,
        }

    async def replay_events(
        self,
        event_type: EventType,
        handler: Callable,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> int:
        events = self.get_history(event_type, limit, since)
        count = 0
        for event in events:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
                count += 1
            except Exception:
                pass
        return count