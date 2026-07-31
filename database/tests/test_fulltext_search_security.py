"""Regression tests for SQL-injection hardening in ``FullTextSearch``.

Identifiers (table/column names) cannot be bound as SQL parameters, so they
must pass the strict allowlist before being interpolated into any query.
"""

from __future__ import annotations

from typing import Any

import pytest

from database.search.fulltext_search import FullTextSearch


class _FakeDriver:
    """Minimal driver stub that records calls and fails if any query runs."""

    def __init__(self, dialect: str = "sqlite") -> None:
        self.dialect = dialect
        self.queries: list[tuple[str, list[Any]]] = []

    async def execute_query(self, sql: str, params: list[Any]) -> list[dict[str, Any]]:
        self.queries.append((sql, params))
        return []


@pytest.mark.parametrize(
    "table,columns",
    [
        ("users; DROP TABLE users; --", ["name"]),
        ("users", ["name; DROP TABLE users; --"]),
        ("users", ["id", "name OR 1=1 --"]),
        ("x' UNION SELECT * FROM secrets --", ["name"]),
        ("users", ["name--"]),
    ],
)
@pytest.mark.asyncio
async def test_invalid_identifiers_are_rejected(table: str, columns: list[str]) -> None:
    driver = _FakeDriver()
    fts = FullTextSearch(driver)
    with pytest.raises(ValueError):
        await fts.search(table=table, columns=columns, query="hello")
    # No query may ever reach the driver with an unvalidated identifier.
    assert driver.queries == []


@pytest.mark.asyncio
async def test_valid_identifiers_pass_through() -> None:
    driver = _FakeDriver(dialect="sqlite")
    fts = FullTextSearch(driver)
    result = await fts.search(table="users", columns=["name", "email"], query="alice")
    assert result == []
    assert driver.queries, "expected a query to run for valid identifiers"
    sql, _ = driver.queries[0]
    assert "users" in sql
    assert "name" in sql and "email" in sql


@pytest.mark.asyncio
async def test_empty_columns_short_circuit() -> None:
    driver = _FakeDriver()
    fts = FullTextSearch(driver)
    assert await fts.search(table="users", columns=[], query="hello") == []
    assert driver.queries == []


@pytest.mark.asyncio
async def test_limit_is_bounded() -> None:
    driver = _FakeDriver(dialect="sqlite")
    fts = FullTextSearch(driver)
    await fts.search(table="users", columns=["name"], query="alice", limit=999999)
    sql, _ = driver.queries[0]
    assert "LIMIT 1000" in sql
