"""Base classes for ingestion sources."""

from __future__ import annotations

from typing import Any, Iterable

from data_intelligence.data_interfaces import DataConnector
from data_intelligence.data_models import DataRecord, SourceType
from data_intelligence.data_protocols import new_id


class BaseSource(DataConnector):
    """Connects to a source and fetches raw records.

    Subclasses only need to implement :meth:`fetch`; the base class turns
    the raw rows into ``DataRecord`` objects.
    """

    source_type: SourceType = SourceType.FILE

    def __init__(self, source_id: str, name: str, **config: Any) -> None:
        self.source_id = source_id
        self.name = name
        self.config = config

    def fetch(self, source: Any = None) -> Iterable[dict[str, Any]]:  # noqa: ARG002
        """Returns raw records from the source (override in subclasses)."""
        raise NotImplementedError

    def records(self, rows: Iterable[dict[str, Any]],
                tags: Iterable[str] | None = None) -> list[DataRecord]:
        """Wraps raw dict rows into ``DataRecord`` objects."""
        tag_list = list(tags or [])
        return [
            DataRecord(record_id=new_id("rec"), source_id=self.source_id,
                       data=dict(row), tags=tag_list)
            for row in rows
        ]

    def __repr__(self) -> str:
        return f"{type(self).__name__}(source_id={self.source_id!r})"
