from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ..data_models import StreamEvent


class EventStream:
    """A single named event stream with ordered buffering and subscriptions.

    Events are appended in order, each carrying a monotonically increasing
    offset. Subscribers may be sync callables or async callables. Buffered
    events can be replayed or read from a given offset.
    """

    def __init__(
        self,
        name: str,
        engine: Any | None = None,
        buffer_size: int = 10000,
    ) -> None:
        self.name = name
        self.engine = engine
        self.buffer_size = buffer_size
        self._events: list[StreamEvent] = []
        self._offsets: list[int] = []
        self._next_offset = 0
        self._subscribers: list[Callable[[StreamEvent], Any]] = []

    async def publish(self, payload: dict[str, Any]) -> StreamEvent:
        """Append an event to the stream and notify subscribers."""
        event = StreamEvent(stream=self.name, payload=dict(payload))
        self._next_offset += 1
        self._events.append(event)
        self._offsets.append(self._next_offset)

        # Bound the in-memory buffer
        if len(self._events) > self.buffer_size:
            overflow = len(self._events) - self.buffer_size
            del self._events[:overflow]
            del self._offsets[:overflow]

        for handler in list(self._subscribers):
            result = handler(event)
            if hasattr(result, "__await__"):
                await result

        if self.engine is not None:
            self.engine.metrics.increment("streaming.published", labels={"stream": self.name})
        return event

    # -- subscriptions -------------------------------------------------------

    def subscribe(self, handler: Callable[[StreamEvent], Any]) -> Callable[[StreamEvent], Any]:
        """Register a subscriber. Returns the handler (for unsubscribe)."""
        if handler not in self._subscribers:
            self._subscribers.append(handler)
        return handler

    def unsubscribe(self, handler: Callable[[StreamEvent], Any]) -> bool:
        try:
            self._subscribers.remove(handler)
            return True
        except ValueError:
            return False

    def subscriber_count(self) -> int:
        return len(self._subscribers)

    # -- reads ---------------------------------------------------------------

    def events(self) -> list[StreamEvent]:
        """All buffered events, oldest first."""
        return list(self._events)

    def read(self, offset: int = 0, limit: int = 100) -> list[StreamEvent]:
        """Read events with offset > ``offset``, up to ``limit`` events."""
        result = [
            event for event, off in zip(self._events, self._offsets, strict=False)
            if off > offset
        ]
        return result[-limit:]

    def replay(self) -> list[StreamEvent]:
        """Replay the full buffer."""
        return self.events()

    def last_offset(self) -> int:
        """The highest offset published so far (0 when empty)."""
        return self._offsets[-1] if self._offsets else 0

    def size(self) -> int:
        return len(self._events)

    def clear(self) -> int:
        """Drop all buffered events, returning the number dropped."""
        count = len(self._events)
        self._events.clear()
        self._offsets.clear()
        return count

    def status(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "events": len(self._events),
            "last_offset": self.last_offset(),
            "subscribers": len(self._subscribers),
            "buffer_size": self.buffer_size,
        }


class StreamManager:
    """Registry and lifecycle manager for event streams."""

    def __init__(
        self,
        engine: Any | None = None,
        default_buffer_size: int = 10000,
    ) -> None:
        self.engine = engine
        self.default_buffer_size = default_buffer_size
        self._streams: dict[str, EventStream] = {}

    def create(self, name: str, buffer_size: int | None = None) -> EventStream:
        stream = EventStream(
            name,
            engine=self.engine,
            buffer_size=buffer_size or self.default_buffer_size,
        )
        self._streams[name] = stream
        return stream

    def get(self, name: str) -> EventStream | None:
        return self._streams.get(name)

    def list(self) -> list[EventStream]:
        return list(self._streams.values())

    def names(self) -> list[str]:
        return list(self._streams.keys())

    def remove(self, name: str) -> bool:
        return self._streams.pop(name, None) is not None

    async def publish(self, name: str, payload: dict[str, Any]) -> StreamEvent:
        stream = self._streams.get(name)
        if stream is None:
            raise ValueError(f"Stream not registered: {name}")
        return await stream.publish(payload)

    def status(self) -> dict[str, Any]:
        return {
            "streams": {name: stream.status() for name, stream in self._streams.items()},
            "count": len(self._streams),
        }


__all__ = ["EventStream", "StreamManager"]
