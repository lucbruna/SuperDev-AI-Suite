"""Base classes for the data warehouse."""

from __future__ import annotations

from typing import Any, Iterable


class WarehouseError(Exception):
    """Raised on warehouse operation failures."""


class WarehouseTable:
    """An in-memory table with a fixed schema and primary key."""

    def __init__(self, name: str, columns: dict[str, str],
                 primary_key: str = "id") -> None:
        self.name = name
        self.columns = columns
        self.primary_key = primary_key
        self.rows: dict[Any, dict[str, Any]] = {}

    def insert(self, record: dict[str, Any]) -> dict[str, Any]:
        """Inserts a record, validating its fields against the schema."""
        key = record.get(self.primary_key)
        if key is None:
            raise WarehouseError(
                f"missing primary key {self.primary_key!r}")
        cleaned: dict[str, Any] = {}
        for column, kind in self.columns.items():
            value = record.get(column)
            if kind == "number":
                value = self._to_number(value)
            elif value is None and kind not in ("text",):
                raise WarehouseError(
                    f"missing required column {column!r}")
            cleaned[column] = value
        self.rows[key] = cleaned
        return cleaned

    def insert_many(self, records: Iterable[dict[str, Any]]) -> int:
        count = 0
        for record in records:
            self.insert(record)
            count += 1
        return count

    def upsert(self, record: dict[str, Any]) -> dict[str, Any]:
        """Inserts or replaces the record with the same primary key."""
        return self.insert(record)

    def get(self, key: Any) -> dict[str, Any] | None:
        return self.rows.get(key)

    def all(self) -> list[dict[str, Any]]:
        return list(self.rows.values())

    def count(self) -> int:
        return len(self.rows)

    def truncate(self) -> int:
        n = len(self.rows)
        self.rows.clear()
        return n

    @staticmethod
    def _to_number(value: Any) -> float:
        if value is None:
            raise WarehouseError("column requires a numeric value")
        return float(value)
