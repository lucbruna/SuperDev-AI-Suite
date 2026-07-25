from __future__ import annotations

from backend.events.event_bus import EventBus, event_bus


class EventDispatcher:
    """Dispatches events through the event bus."""

    def __init__(self, bus: EventBus | None = None):
        self._bus = bus or event_bus

    async def dispatch(self, event_type: str, data: dict = None, source: str = ""):
        return await self._bus.publish(event_type, data, source)


dispatcher = EventDispatcher()
