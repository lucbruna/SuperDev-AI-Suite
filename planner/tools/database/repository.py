from __future__ import annotations

from typing import Any, Generic, TypeVar

from .database_tool import DatabaseTool

T = TypeVar("T")


class DatabaseRepository(Generic[T]):
    """Generic CRUD repository for database operations."""

    def __init__(self, adapter: DatabaseTool, table: str, model_class: type[T] | None = None):
        self._adapter = adapter
        self._table = table
        self._model = model_class

    def find_by_id(self, id_value: Any, id_column: str = "id") -> dict[str, Any] | None:
        rows = self._adapter.execute(f"SELECT * FROM {self._table} WHERE {id_column} = ?", {id_column: id_value})
        return rows[0] if rows else None

    def find_all(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        return self._adapter.execute(f"SELECT * FROM {self._table} LIMIT ? OFFSET ?", {"limit": limit, "offset": offset})

    def create(self, data: dict[str, Any]) -> Any:
        cols = ", ".join(data.keys())
        placeholders = ", ".join("?" for _ in data)
        self._adapter.execute(f"INSERT INTO {self._table} ({cols}) VALUES ({placeholders})", data)
        return data.get("id")

    def update(self, id_value: Any, data: dict[str, Any], id_column: str = "id") -> int:
        set_clause = ", ".join(f"{k} = ?" for k in data)
        params = {**data, id_column: id_value}
        self._adapter.execute(f"UPDATE {self._table} SET {set_clause} WHERE {id_column} = ?", params)
        return 1

    def delete(self, id_value: Any, id_column: str = "id") -> int:
        self._adapter.execute(f"DELETE FROM {self._table} WHERE {id_column} = ?", {id_column: id_value})
        return 1

    def count(self) -> int:
        rows = self._adapter.execute(f"SELECT COUNT(*) as cnt FROM {self._table}")
        return rows[0]["cnt"] if rows else 0
