"""Warehouse loader (staging -> tables)."""

from __future__ import annotations

from typing import Any, Iterable

from data_intelligence.data_logger import get_logger
from data_intelligence.warehouse.base import WarehouseError


class StagingArea:
    """Temporary landing zone before data reaches the warehouse tables."""

    def __init__(self, name: str = "staging") -> None:
        self._log = get_logger()
        self.name = name
        self._records: dict[str, list[dict[str, Any]]] = {}

    def stage(self, table: str, records: Iterable[dict[str, Any]]) -> int:
        """Buffers records under the target table name."""
        batch = list(records)
        self._records.setdefault(table, []).extend(batch)
        return len(batch)

    def staged(self, table: str) -> list[dict[str, Any]]:
        return list(self._records.get(table, []))

    def commit(self, table: str, sink: Any) -> dict[str, Any]:
        """Writes staged records to a sink (e.g. a warehouse table)."""
        records = self._records.pop(table, [])
        if not records:
            raise WarehouseError(f"nothing staged for {table!r}")
        return sink.write(records, table)

    def flush(self, table: str) -> int:
        records = self._records.pop(table, [])
        return len(records)

    def pending(self) -> dict[str, int]:
        return {table: len(records)
                for table, records in self._records.items()}
