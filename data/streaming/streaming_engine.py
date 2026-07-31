from __future__ import annotations

from typing import Any

from ..data_models import StreamEvent, StreamWindow
from .event_stream import StreamManager


class StreamingEngine:
    """Real-time streaming — event streams, message processing, windowing, realtime analysis, aggregation."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine
        self.config = engine.config.streaming
        self._streams: dict[str, list[StreamEvent]] = {}
        self._handlers: dict[str, Any] = {}
        self._window_buffers: dict[str, list[float]] = {}
        self._initialized = False
        # Deep-dive toolkit: engine.streaming.streams
        self.streams = StreamManager(engine=self.engine)

    async def initialize(self) -> None:
        self._initialized = True

    async def shutdown(self) -> None:
        self._initialized = False

    def register_handler(self, stream: str, handler: Any) -> None:
        self._handlers[stream] = handler

    async def publish(self, stream: str, payload: dict[str, Any]) -> StreamEvent:
        event = StreamEvent(stream=stream, payload=payload)
        self._streams.setdefault(stream, []).append(event)
        self.engine.metrics.increment("streaming.events", labels={"stream": stream})

        # Bound buffer to config size
        buffer = self._streams[stream]
        if len(buffer) > self.config.buffer_size:
            del buffer[: len(buffer) - self.config.buffer_size]

        handler = self._handlers.get(stream)
        if handler is not None:
            if hasattr(handler, "process"):
                await handler.process(event)
            elif callable(handler):
                result = handler(event)
                if hasattr(result, "__await__"):
                    await result

        await self.engine.event_bus.emit("data.stream_event", {
            "event_id": event.event_id,
            "stream": stream,
        })
        return event

    def get_events(self, stream: str, limit: int = 100) -> list[StreamEvent]:
        return self._streams.get(stream, [])[-limit:]

    def list_streams(self) -> list[str]:
        return list(self._streams.keys())

    # -- windowing -----------------------------------------------------------

    def window(
        self,
        stream: str,
        window: StreamWindow | str = StreamWindow.TUMBLING,
        size: int = 10,
    ) -> list[list[StreamEvent]]:
        events = self._streams.get(stream, [])
        if window == StreamWindow.SLIDING or window == "sliding":
            if not events:
                return []
            return [events[max(0, len(events) - size):]]
        return [events[i:i + size] for i in range(0, len(events), size)]

    # -- aggregation ---------------------------------------------------------

    def aggregate(self, stream: str, field: str, window_size: int = 10) -> dict[str, float]:
        events = self._streams.get(stream, [])[-window_size:]
        values = [
            e.payload[field] for e in events
            if isinstance(e.payload.get(field), (int, float))
        ]
        if not values:
            return {"count": 0, "sum": 0.0}
        return {
            "count": len(values),
            "sum": sum(values),
            "avg": round(sum(values) / len(values), 2),
            "min": min(values),
            "max": max(values),
        }

    # -- realtime analysis ---------------------------------------------------

    def realtime_rate(self, stream: str) -> float:
        events = self._streams.get(stream, [])
        if len(events) < 2:
            return 0.0
        span = events[-1].timestamp - events[0].timestamp
        if span <= 0:
            return 0.0
        return round(len(events) / span, 2)

    def status(self) -> dict[str, Any]:
        return {
            "initialized": self._initialized,
            "streams": len(self._streams),
            "events": sum(len(v) for v in self._streams.values()),
        }


__all__ = ["StreamingEngine"]
