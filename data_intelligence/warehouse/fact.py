"""Fact tables (measures linked to dimensions)."""

from __future__ import annotations

from typing import Any

from data_intelligence.warehouse.base import WarehouseTable


class FactTable(WarehouseTable):
    """A fact table holding measures plus dimension foreign keys."""

    def __init__(self, name: str, columns: dict[str, str],
                 primary_key: str = "id",
                 measures: list[str] | None = None,
                 dimensions: list[str] | None = None) -> None:
        super().__init__(name, columns, primary_key)
        self.measures = measures or []
        self.dimensions = dimensions or []

    def insert(self, record: dict[str, Any]) -> dict[str, Any]:
        inserted = super().insert(record)
        return inserted

    def rollup(self, dimension_key: str,
               measure: str) -> dict[Any, float]:
        """Aggregates a measure grouped by a dimension key."""
        totals: dict[Any, float] = {}
        for row in self.all():
            key = row.get(dimension_key)
            totals[key] = totals.get(key, 0.0) + float(row.get(measure, 0.0))
        return totals
