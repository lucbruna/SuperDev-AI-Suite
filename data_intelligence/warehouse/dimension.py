"""Dimension tables (star schema)."""

from __future__ import annotations

from typing import Any

from data_intelligence.warehouse.base import WarehouseTable


class DimensionTable(WarehouseTable):
    """A slowly-changing dimension table.

    ``track_changes`` stores history: when a record with an existing key is
    upserted, the previous row is archived into ``_history``.
    """

    def __init__(self, name: str, columns: dict[str, str],
                 primary_key: str = "id",
                 track_changes: bool = False) -> None:
        super().__init__(name, columns, primary_key)
        self.track_changes = track_changes
        self._history: list[dict[str, Any]] = []

    def upsert(self, record: dict[str, Any]) -> dict[str, Any]:
        key = record.get(self.primary_key)
        if self.track_changes and key in self.rows:
            self._history.append(dict(self.rows[key]))
        return self.insert(record)

    def history(self, key: Any) -> list[dict[str, Any]]:
        """Returns the archived rows for the given key."""
        return [row for row in self._history
                if row.get(self.primary_key) == key]
