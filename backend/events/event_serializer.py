from __future__ import annotations

import json

from backend.events.event_bus import Event


class EventSerializer:
    """Serializes and deserializes events."""

    @staticmethod
    def serialize(event: Event) -> str:
        return json.dumps(
            {
                "id": event.id,
                "type": event.type,
                "data": event.data,
                "timestamp": event.timestamp.isoformat(),
                "source": event.source,
            },
            default=str,
        )

    @staticmethod
    def deserialize(data: str) -> Event:
        parsed = json.loads(data)
        from datetime import datetime

        return Event(
            id=parsed["id"],
            type=parsed["type"],
            data=parsed.get("data", {}),
            timestamp=datetime.fromisoformat(parsed["timestamp"]),
            source=parsed.get("source", ""),
        )
