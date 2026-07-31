"""Query builder for constructing SQL queries."""
from typing import List, Dict, Any, Optional


class QueryBuilder:
    """Builds SQL queries programmatically."""

    def __init__(self):
        self._query = ""
        self._params: List[Any] = []

    def select(self, columns: List[str], table: str) -> "QueryBuilder":
        cols = ", ".join(columns) if columns else "*"
        self._query = f"SELECT {cols} FROM {table}"
        return self

    def where(self, condition: str, value: Any = None) -> "QueryBuilder":
        self._query += f" WHERE {condition}"
        if value is not None:
            self._params.append(value)
        return self

    def and_where(self, condition: str, value: Any = None) -> "QueryBuilder":
        self._query += f" AND {condition}"
        if value is not None:
            self._params.append(value)
        return self

    def order_by(self, column: str, direction: str = "ASC") -> "QueryBuilder":
        self._query += f" ORDER BY {column} {direction}"
        return self

    def limit(self, count: int) -> "QueryBuilder":
        self._query += f" LIMIT {count}"
        return self

    def offset(self, count: int) -> "QueryBuilder":
        self._query += f" OFFSET {count}"
        return self

    def insert(self, table: str, columns: List[str], values: List[Any]) -> "QueryBuilder":
        cols = ", ".join(columns)
        placeholders = ", ".join(["?" for _ in values])
        self._query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        self._params = list(values)
        return self

    def update(self, table: str, sets: Dict[str, Any]) -> "QueryBuilder":
        set_str = ", ".join(f"{k} = ?" for k in sets)
        self._query = f"UPDATE {table} SET {set_str}"
        self._params = list(sets.values())
        return self

    def delete(self, table: str) -> "QueryBuilder":
        self._query = f"DELETE FROM {table}"
        return self

    def build(self) -> str:
        return self._query

    def get_params(self) -> List[Any]:
        return list(self._params)

    def reset(self) -> None:
        self._query = ""
        self._params.clear()
