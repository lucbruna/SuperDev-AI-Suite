from __future__ import annotations

from typing import Any

from ..database_interfaces import IQueryBuilder


class QueryBuilder(IQueryBuilder):
    """SQL query builder with dialect-aware quoting and parameterisation.

    Dialects supported: ``postgresql``, ``sqlite``, ``mysql``, ``mariadb``,
    ``sqlserver`` (``mssql``).
    """

    PLACEHOLDER: dict[str, str] = {
        "postgresql": "%s",
        "sqlite": "?",
        "mysql": "?",
        "mariadb": "?",
        "mssql": "?",
        "sqlserver": "?",
    }

    def __init__(self, dialect: str = "postgresql") -> None:
        self._dialect = dialect
        self.reset()

    def copy(self) -> QueryBuilder:
        """Return a fresh builder with the same dialect."""
        return QueryBuilder(dialect=self._dialect)

    # -- operation entry-points -----------------------------------------------

    def select(self, *fields: str) -> IQueryBuilder:
        self._operation = "SELECT"
        self._select_fields = list(fields) if fields else ["*"]
        return self

    def insert(self, table: str) -> IQueryBuilder:
        self._operation = "INSERT"
        self._table = self._quote(table)
        return self

    def update(self, table: str) -> IQueryBuilder:
        self._operation = "UPDATE"
        self._table = self._quote(table)
        return self

    def delete(self, table: str) -> IQueryBuilder:
        self._operation = "DELETE"
        self._table = self._quote(table)
        return self

    def from_table(self, table: str) -> IQueryBuilder:
        self._table = self._quote(table)
        return self

    # -- clause methods -------------------------------------------------------

    def where(self, condition: str, *params: Any) -> IQueryBuilder:
        self._conditions.append(condition)
        self._params.extend(params)
        return self

    def order_by(self, field: str, direction: str = "ASC") -> IQueryBuilder:
        self._order.append(f"{self._quote(field)} {direction}")
        return self

    def limit(self, count: int) -> IQueryBuilder:
        self._limit_count = count
        return self

    def offset(self, count: int) -> IQueryBuilder:
        self._offset_count = count
        return self

    def join(self, table: str, on: str) -> IQueryBuilder:
        self._joins.append(f"JOIN {self._quote(table)} ON {on}")
        return self

    # -- value setters --------------------------------------------------------

    def set_values(self, values: dict[str, Any]) -> IQueryBuilder:
        self._values = values
        return self

    def returning(self, *fields: str) -> IQueryBuilder:
        self._returning = list(fields) if fields else ["*"]
        return self

    # -- build ----------------------------------------------------------------

    def build(self) -> tuple[str, list[Any]]:
        if self._operation == "SELECT":
            return self._build_select()
        if self._operation == "INSERT":
            return self._build_insert()
        if self._operation == "UPDATE":
            return self._build_update()
        if self._operation == "DELETE":
            return self._build_delete()
        raise ValueError(f"Unknown operation: {self._operation!r}")

    def reset(self) -> None:
        self._operation: str = ""
        self._select_fields: list[str] = []
        self._table: str = ""
        self._conditions: list[str] = []
        self._order: list[str] = []
        self._limit_count: int | None = None
        self._offset_count: int | None = None
        self._joins: list[str] = []
        self._params: list[Any] = []
        self._values: dict[str, Any] = {}
        self._returning: list[str] | None = None

    # -- internal builders ----------------------------------------------------

    def _build_select(self) -> tuple[str, list[Any]]:
        clauses = [
            f"SELECT {', '.join(self._select_fields)}",
            f"FROM {self._table}",
        ]
        clauses.extend(self._joins)
        if self._conditions:
            clauses.append(f"WHERE {' AND '.join(self._conditions)}")
        if self._order:
            clauses.append(f"ORDER BY {', '.join(self._order)}")
        if self._limit_count is not None:
            clauses.append(f"LIMIT {self._limit_count}")
        if self._offset_count is not None:
            clauses.append(f"OFFSET {self._offset_count}")
        return (" ".join(clauses), list(self._params))

    def _build_insert(self) -> tuple[str, list[Any]]:
        columns = [self._quote(c) for c in self._values]
        placeholders = ", ".join(self._ph() for _ in self._values)
        sql = f"INSERT INTO {self._table} ({', '.join(columns)}) VALUES ({placeholders})"
        if self._returning is not None:
            sql += f" RETURNING {', '.join(self._returning)}"
        return (sql, list(self._values.values()))

    def _build_update(self) -> tuple[str, list[Any]]:
        assignments = [f"{self._quote(k)} = {self._ph()}" for k in self._values]
        params: list[Any] = list(self._values.values())
        clauses: list[str] = [
            f"UPDATE {self._table}",
            f"SET {', '.join(assignments)}",
        ]
        if self._conditions:
            clauses.append(f"WHERE {' AND '.join(self._conditions)}")
            params.extend(self._params)
        return (" ".join(clauses), params)

    def _build_delete(self) -> tuple[str, list[Any]]:
        clauses: list[str] = [f"DELETE FROM {self._table}"]
        if self._conditions:
            clauses.append(f"WHERE {' AND '.join(self._conditions)}")
        return (" ".join(clauses), list(self._params))

    # -- helpers --------------------------------------------------------------

    def _quote(self, name: str) -> str:
        if self._dialect in ("mysql", "mariadb"):
            return f"`{name}`"
        if self._dialect in ("sqlserver", "mssql"):
            return f"[{name}]"
        return f'"{name}"'

    def _ph(self) -> str:
        return self.PLACEHOLDER.get(self._dialect, "?")


__all__ = [
    "QueryBuilder",
]
