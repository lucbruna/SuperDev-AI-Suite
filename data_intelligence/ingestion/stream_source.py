"""Streaming datasource ingestion (IoT, logs)."""

from __future__ import annotations

from typing import Any, Iterable

from data_intelligence.data_models import SourceType
from data_intelligence.ingestion.base import BaseSource


class StreamSource(BaseSource):
    """Buffers streaming records (IoT telemetry, application logs).

    ``emit`` appends a raw record to the internal buffer; ``fetch`` drains
    the buffer (optionally keeping the last ``keep`` records).
    """

    source_type = SourceType.STREAM

    def __init__(self, source_id: str, name: str, keep: int = 0,
                 **config: Any) -> None:
        super().__init__(source_id, name, keep=keep, **config)
        self.keep = keep
        self._buffer: list[dict[str, Any]] = []

    def emit(self, record: dict[str, Any]) -> None:
        """Appends a raw record to the buffer."""
        self._buffer.append(dict(record))

    def emit_many(self, records: Iterable[dict[str, Any]]) -> int:
        """Appends many records, returning how many were added."""
        added = 0
        for record in records:
            self.emit(record)
            added += 1
        return added

    def fetch(self, source: Any = None) -> Iterable[dict[str, Any]]:  # noqa: ARG002
        records = list(self._buffer)
        if self.keep:
            self._buffer = records[-self.keep:]
        else:
            self._buffer = []
        return records

    def buffer_size(self) -> int:
        return len(self._buffer)
