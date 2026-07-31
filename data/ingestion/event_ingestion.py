from __future__ import annotations

import time
from typing import Any

from ..data_models import DataSourceType, StreamEvent
from .collector import BaseCollector


class EventCollector(BaseCollector):
    """Collector for event streams.

    Collects events pushed via :meth:`add_event` or pulled from an external
    callable (``source`` in config) that returns an iterable of dicts.
    """

    def __init__(
        self,
        name: str,
        engine: Any | None = None,
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(name, engine, config)
        self._events: list[StreamEvent] = []

    def get_source_type(self) -> DataSourceType:
        return DataSourceType.EVENT

    def add_event(
        self,
        payload: dict[str, Any],
        stream: str = "",
        partition: int = 0,
    ) -> StreamEvent:
        event = StreamEvent(
            stream=stream or self.name,
            payload=payload,
            partition=partition,
        )
        self._events.append(event)
        return event

    def add_many(self, events: list[dict[str, Any]]) -> int:
        count = 0
        for event in events:
            self.add_event(dict(event))
            count += 1
        return count

    async def collect(self, config: dict[str, Any] | None = None) -> Any:
        config = config or {}
        source = config.get("source") or self.config.get("source")
        rows: list[dict[str, Any]] = []

        if callable(source):
            for item in source():
                if isinstance(item, dict):
                    rows.append(item)
        else:
            events = list(self._events)
            if config.get("clear", True):
                self._events.clear()
            rows = [dict(event.payload, stream=event.stream, event_id=event.event_id)
                    for event in events]

        return self._build_batch(rows, metadata={"collector": "event"})


__all__ = ["EventCollector"]
