from __future__ import annotations

import re
from typing import Any

from ..database_interfaces import IDatabaseDriver

_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _validate_identifier(name: str) -> str:
    """Validate a table/column identifier to prevent SQL injection.

    Identifiers cannot be bound as parameters, so they are validated against a
    strict allowlist pattern instead of being interpolated verbatim.
    """
    if not _IDENTIFIER_RE.match(name):
        raise ValueError(f"Invalid SQL identifier: {name!r}")
    return name


class FullTextSearch:
    """Cross-database full-text search helper.

    Generates dialect-specific FTS queries.
    """

    def __init__(self, driver: IDatabaseDriver) -> None:
        self._driver = driver

    async def search(
        self,
        table: str,
        columns: list[str],
        query: str,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        dialect = self._driver.dialect
        terms = self._tokenize(query)
        if not terms:
            return []
        if not columns:
            return []
        # Identifiers are interpolated into SQL (they cannot be parameterized),
        # so they must pass the strict allowlist before reaching any query.
        table = _validate_identifier(table)
        columns = [_validate_identifier(c) for c in columns]
        limit = max(1, min(int(limit), 1000))

        if dialect == "postgresql":
            return await self._search_pg(table, columns, terms, limit)
        elif dialect in ("mysql", "mariadb"):
            return await self._search_mysql(table, columns, query, limit)
        elif dialect == "sqlite":
            return await self._search_sqlite(table, columns, terms, limit)
        else:
            return await self._search_like(table, columns, terms, limit)

    async def _search_pg(
        self, table: str, columns: list[str], terms: list[str], limit: int
    ) -> list[dict[str, Any]]:
        tsquery = " & ".join(terms)
        tsvector = " || ' ' || ".join(f"COALESCE({c}::text, '')" for c in columns)
        sql = (
            f"SELECT *, ts_rank(to_tsvector('english', {tsvector}), "
            f"to_tsquery('english', %s)) AS rank "
            f"FROM {table} WHERE to_tsvector('english', {tsvector}) "
            f"@@ to_tsquery('english', %s) ORDER BY rank DESC LIMIT {limit}"
        )
        return await self._driver.execute_query(sql, [tsquery, tsquery])

    async def _search_mysql(
        self, table: str, columns: list[str], query: str, limit: int
    ) -> list[dict[str, Any]]:
        cols = ", ".join(columns)
        sql = (
            f"SELECT *, MATCH({cols}) AGAINST (%s IN BOOLEAN MODE) AS rank "
            f"FROM {table} WHERE MATCH({cols}) AGAINST (%s IN BOOLEAN MODE) "
            f"ORDER BY rank DESC LIMIT {limit}"
        )
        return await self._driver.execute_query(sql, [query, query])

    async def _search_sqlite(
        self, table: str, columns: list[str], terms: list[str], limit: int
    ) -> list[dict[str, Any]]:
        conditions = []
        params: list[str] = []
        for term in terms:
            like = f"%{term}%"
            cond = " OR ".join(f"{c} LIKE ?" for c in columns)
            conditions.append(f"({cond})")
            params.extend([like] * len(columns))
        sql = f"SELECT * FROM {table} WHERE {' AND '.join(conditions)} LIMIT {limit}"
        return await self._driver.execute_query(sql, params)

    async def _search_like(
        self, table: str, columns: list[str], terms: list[str], limit: int
    ) -> list[dict[str, Any]]:
        conditions = []
        params: list[str] = []
        for term in terms:
            like = f"%{term}%"
            cond = " OR ".join(f"{c} LIKE ?" for c in columns)
            conditions.append(f"({cond})")
            params.extend([like] * len(columns))
        sql = f"SELECT * FROM {table} WHERE {' AND '.join(conditions)} LIMIT {limit}"
        return await self._driver.execute_query(sql, params)

    @staticmethod
    def _tokenize(query: str) -> list[str]:
        return [t for t in re.split(r"\W+", query.lower()) if len(t) > 1]


__all__ = [
    "FullTextSearch",
]
