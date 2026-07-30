from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any, Callable

from .ai_types import EventType

EventListener = Callable[..., Any]


class AIEvents:
    """Event system for the AI engine."""

    def __init__(self):
        self._listeners: dict[str, list[EventListener]] = {}
        self._once_listeners: dict[str, list[EventListener]] = {}
        self._history: list[dict[str, Any]] = []
        self._max_history: int = 1000

    def on(self, event_type: str | EventType, listener: EventListener) -> None:
        """Register a listener for an event type."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)

    def off(self, event_type: str | EventType, listener: EventListener) -> None:
        """Remove a listener for an event type."""
        if event_type in self._listeners:
            self._listeners[event_type] = [
                l for l in self._listeners[event_type] if l is not listener
            ]

    def once(self, event_type: str | EventType, listener: EventListener) -> None:
        """Register a one-time listener."""
        if event_type not in self._once_listeners:
            self._once_listeners[event_type] = []
        self._once_listeners[event_type].append(listener)

    def emit(self, event_type: str | EventType, data: dict[str, Any] | None = None) -> None:
        """Emit an event synchronously."""
        event_data = {
            "type": event_type,
            "data": data or {},
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # Call regular listeners
        listeners = self._listeners.get(event_type, [])
        for listener in listeners:
            try:
                listener(event_data)
            except Exception:
                pass

        # Call once listeners
        once_listeners = self._once_listeners.pop(event_type, [])
        for listener in once_listeners:
            try:
                listener(event_data)
            except Exception:
                pass

        # Record history
        self._history.append(event_data)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

    async def emit_async(self, event_type: str | EventType, data: dict[str, Any] | None = None) -> None:
        """Emit an event asynchronously."""
        event_data = {
            "type": event_type,
            "data": data or {},
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # Call regular listeners
        listeners = self._listeners.get(event_type, [])
        if listeners:
            await asyncio.gather(
                *[self._safe_call_async(listener, event_data) for listener in listeners],
                return_exceptions=True,
            )

        # Call once listeners
        once_listeners = self._once_listeners.pop(event_type, [])
        if once_listeners:
            await asyncio.gather(
                *[self._safe_call_async(listener, event_data) for listener in once_listeners],
                return_exceptions=True,
            )

        # Record history
        self._history.append(event_data)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

    async def _safe_call_async(self, listener: EventListener, event_data: dict[str, Any]) -> None:
        """Safely call an async listener."""
        try:
            if asyncio.iscoroutinefunction(listener):
                await listener(event_data)
            else:
                listener(event_data)
        except Exception:
            pass

    def get_history(
        self,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get event history, optionally filtered by type."""
        events = self._history
        if event_type:
            events = [e for e in events if e["type"] == event_type]
        return events[-limit:]

    def clear_history(self) -> None:
        """Clear event history."""
        self._history.clear()

    def listener_count(self, event_type: str | None = None) -> int:
        """Count registered listeners."""
        if event_type:
            return len(self._listeners.get(event_type, []))
        return sum(len(v) for v in self._listeners.values())

    def health(self) -> dict[str, Any]:
        """Get events subsystem health."""
        return {
            "status": "healthy",
            "listeners": self.listener_count(),
            "event_types": list(self._listeners.keys()),
            "history_size": len(self._history),
            "timestamp": datetime.now(UTC).isoformat(),
        }
