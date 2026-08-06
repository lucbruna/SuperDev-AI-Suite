"""WebSocket bridge: serializable event hub (no live connections)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from modules.ai_evolution_engine.core.evolution_events import EvolutionEvent


@dataclass(slots=True)
class WSEventMessage:
    """A serializable message ready for transport."""

    channel: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"channel": self.channel, "payload": self.payload}


class EventHub:
    """Synchronous fan-out of evolution events to registered handlers."""

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Callable[[WSEventMessage], None]]] = {}

    def subscribe(self, channel: str, handler: Callable[[WSEventMessage], None]) -> None:
        self._subscribers.setdefault(channel, []).append(handler)

    def unsubscribe(self, channel: str, handler: Callable[[WSEventMessage], None]) -> None:
        handlers = self._subscribers.get(channel, [])
        if handler in handlers:
            handlers.remove(handler)

    def publish(self, message: WSEventMessage) -> None:
        for handler in list(self._subscribers.get(message.channel, [])):
            handler(message)

    def publish_event(self, event: EvolutionEvent) -> None:
        self.publish(
            WSEventMessage(channel="evolution", payload={"event": event.to_dict()})
        )

    def channels(self) -> list[str]:
        return sorted(self._subscribers)
