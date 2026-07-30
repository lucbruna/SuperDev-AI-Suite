from __future__ import annotations

from typing import Any


class QueryBuilder:
    """Fluent SQL query builder."""

    def __init__(self):
        self._columns: list[str] = ["*"]
        self._table: str = ""
        self._wheres: list[str] = []
        self._params: list[Any] = []
        self._joins: list[str] = []
        self._order: str = ""
        self._limit: int = 0
        self._offset: int = 0
        self._type: str = "select"
        self._set: dict[str, Any] = {}
        self._values: dict[str, Any] = {}

    def select(self, *columns: str) -> QueryBuilder:
        self._type = "select"
        if columns:
            self._columns = list(columns)
        return self

    def from_table(self, table: str) -> QueryBuilder:
        self._table = table
        return self

    def insert(self, table: str) -> QueryBuilder:
        self._type = "insert"
        self._table = table
        return self

    def update(self, table: str) -> QueryBuilder:
        self._type = "update"
        self._table = table
        return self

    def delete(self, table: str = "") -> QueryBuilder:
        self._type = "delete"
        if table:
            self._table = table
        return self

    def set(self, **kwargs: Any) -> QueryBuilder:
        self._set = kwargs
        return self

    def values(self, **kwargs: Any) -> QueryBuilder:
        self._values = kwargs
        return self

    def where(self, condition: str, *params: Any) -> QueryBuilder:
        self._wheres.append(condition)
        self._params.extend(params)
        return self

    def join(self, table: str, on: str, join_type: str = "INNER") -> QueryBuilder:
        self._joins.append(f"{join_type} JOIN {table} ON {on}")
        return self

    def order_by(self, column: str, direction: str = "ASC") -> QueryBuilder:
        self._order = f"{column} {direction}"
        return self

    def limit(self, limit: int) -> QueryBuilder:
        self._limit = limit
        return self

    def offset(self, offset: int) -> QueryBuilder:
        self._offset = offset
        return self

    def build(self) -> str:
        if self._type == "select":
            query = f"SELECT {', '.join(self._columns)} FROM {self._table}"
            if self._joins:
                query += " " + " ".join(self._joins)
            if self._wheres:
                query += " WHERE " + " AND ".join(self._wheres)
            if self._order:
                query += f" ORDER BY {self._order}"
            if self._limit:
                query += f" LIMIT {self._limit}"
            if self._offset:
                query += f" OFFSET {self._offset}"
            return query
        elif self._type == "insert":
            cols = ", ".join(self._values.keys())
            placeholders = ", ".join("?" for _ in self._values)
            return f"INSERT INTO {self._table} ({cols}) VALUES ({placeholders})"
        elif self._type == "update":
            set_clause = ", ".join(f"{k} = ?" for k in self._set)
            query = f"UPDATE {self._table} SET {set_clause}"
            if self._wheres:
                query += " WHERE " + " AND ".join(self._wheres)
            return query
        elif self._type == "delete":
            query = f"DELETE FROM {self._table}"
            if self._wheres:
                query += " WHERE " + " AND ".join(self._wheres)
            return query
        return ""
