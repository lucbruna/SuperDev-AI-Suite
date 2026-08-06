"""WebSocket bridge: serializable event hub (no live connections)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from modules.super_ai_orchestrator.events.event import Event


@dataclass(slots=True)
class WSEventMessage:
    """A serializable message ready for transport.

    Attributes:
        channel: logical channel the message is published on.
        payload: structured data attached to the message.
    """

    channel: str
    payload: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {"channel": self.channel, "payload": self.payload}


class EventHub:
    """Synchronous fan-out of orchestrator events to registered handlers.

    The hub itself has no clock, no I/O and no live connections: it routes
    ``WSEventMessage`` objects to registered callbacks in subscription
    order. ``wire`` attaches it to the kernel's ``EventBus``, translating
    every bus event into a transport-ready message.
    """

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

    def publish_event(self, event: Event) -> None:
        """Publish any object exposing ``to_dict()`` on the orchestrator channel."""
        self.publish(
            WSEventMessage(
                channel="orchestrator",
                payload={"event": event.to_dict()},
            )
        )

    def wire(self, bus) -> Callable[[], None]:
        """Attach to an ``EventBus``; returns the unsubscribe callable.

        Every event published on the bus is translated into a
        ``WSEventMessage`` on the ``orchestrator`` channel and fanned out
        to this hub's subscribers.
        """

        def _translate(event: Event) -> None:
            self.publish_event(event)

        return bus.subscribe(_translate)

    def channels(self) -> list[str]:
        return sorted(self._subscribers)

    def to_dict(self) -> dict[str, Any]:
        return {"channels": self.channels()}
