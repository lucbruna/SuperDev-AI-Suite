"""Event Gateway — bridges external callers to the studio event bus."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration.event_bus import get_event_bus


class EventGateway:
    """Publishes and introspects studio events."""

    def publish(self, event: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        self.publish_sync(event, **(payload or {}))
        return {"published": event}

    def history(self, limit: int = 50) -> dict[str, Any]:
        return {"events": get_event_bus().history(limit=limit)}


_event_gateway: EventGateway | None = None


def get_event_gateway() -> EventGateway:
    global _event_gateway
    if _event_gateway is None:
        _event_gateway = EventGateway()
    return _event_gateway
