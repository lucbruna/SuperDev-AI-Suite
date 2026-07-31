from __future__ import annotations

import sqlite3

import pytest

from SuperDev.data.ingestion.database_ingestion import DatabaseCollector, DatabaseConnector


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "test.db"
    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE users (id INTEGER, name TEXT)")
    connection.executemany(
        "INSERT INTO users (id, name) VALUES (?, ?)",
        [(1, "ana"), (2, "bob")],
    )
    connection.commit()
    connection.close()
    return str(path)


class TestDatabaseConnector:
    @pytest.mark.asyncio
    async def test_read_table(self, db_path) -> None:
        connector = DatabaseConnector("db", {"database": db_path})
        assert await connector.connect()
        rows = await connector.read({"table": "users"})
        assert len(rows) == 2
        assert rows[0]["name"] == "ana"
        assert connector.connected is True
        await connector.disconnect()
        assert connector.connected is False

    @pytest.mark.asyncio
    async def test_read_with_query(self, db_path) -> None:
        connector = DatabaseConnector("db", {"database": db_path})
        await connector.connect()
        rows = await connector.read({"query": "SELECT * FROM users WHERE id = 2"})
        assert rows == [{"id": 2, "name": "bob"}]
        await connector.disconnect()

    @pytest.mark.asyncio
    async def test_read_without_query_raises(self) -> None:
        connector = DatabaseConnector("db", {"database": ":memory:"})
        await connector.connect()
        with pytest.raises(ValueError):
            await connector.read({})
        await connector.disconnect()

    @pytest.mark.asyncio
    async def test_read_not_connected_raises(self) -> None:
        connector = DatabaseConnector("db", {"database": ":memory:"})
        with pytest.raises(RuntimeError):
            await connector.read({"table": "users"})


class TestDatabaseCollector:
    @pytest.mark.asyncio
    async def test_collect_builds_batch(self, db_path) -> None:
        connector = DatabaseConnector("db", {"database": db_path})
        collector = DatabaseCollector("db-source", connector=connector)
        batch = await collector.collect({"table": "users"})
        assert len(batch.records) == 2
        assert batch.records[0].data["name"] == "ana"
        assert connector.connected is False
