from __future__ import annotations

import asyncio
from typing import Any

import pytest  # type: ignore[import-untyped]

from SuperDev.database.database_models import MigrationInfo
from SuperDev.database.events import DatabaseEventBus, DatabaseEventType
from SuperDev.database.database_interfaces import IDatabaseEventListener


class _TestListener(IDatabaseEventListener):
    def __init__(self) -> None:
        self.events: list[str] = []

    async def on_connect(self, driver_name: str) -> None:
        self.events.append(f"connect:{driver_name}")

    async def on_disconnect(self, driver_name: str) -> None:
        self.events.append(f"disconnect:{driver_name}")

    async def on_query(self, query: str, duration_ms: float) -> None:
        self.events.append(f"query:{query}:{duration_ms}")

    async def on_error(self, error: Exception, query: str | None = None) -> None:
        self.events.append(f"error:{error}")

    async def on_migration(self, migration: MigrationInfo) -> None:
        self.events.append(f"migration:{migration.id}")


class TestDatabaseEventBus:
    @pytest.fixture()
    def bus(self) -> DatabaseEventBus:
        return DatabaseEventBus()

    @pytest.fixture()
    def listener(self) -> _TestListener:
        return _TestListener()

    def test_register(self, bus: DatabaseEventBus, listener: _TestListener) -> None:
        bus.register(DatabaseEventType.CONNECT, listener)
        assert len(bus.listeners(DatabaseEventType.CONNECT)) == 1

    def test_unregister(self, bus: DatabaseEventBus, listener: _TestListener) -> None:
        bus.register(DatabaseEventType.CONNECT, listener)
        bus.unregister(DatabaseEventType.CONNECT, listener)
        assert len(bus.listeners(DatabaseEventType.CONNECT)) == 0

    def test_initial_no_listeners(self, bus: DatabaseEventBus) -> None:
        assert len(bus.listeners(DatabaseEventType.QUERY)) == 0

    def test_emit_connect(self, bus: DatabaseEventBus, listener: _TestListener) -> None:
        bus.register(DatabaseEventType.CONNECT, listener)
        asyncio.run(bus.emit(DatabaseEventType.CONNECT, driver_name="pg"))
        assert "connect:pg" in listener.events

    def test_emit_query(self, bus: DatabaseEventBus, listener: _TestListener) -> None:
        bus.register(DatabaseEventType.QUERY, listener)
        asyncio.run(bus.emit(DatabaseEventType.QUERY, query="SELECT 1", duration_ms=5.0))
        assert "query:SELECT 1:5.0" in listener.events

    def test_emit_error(self, bus: DatabaseEventBus, listener: _TestListener) -> None:
        bus.register(DatabaseEventType.ERROR, listener)
        asyncio.run(bus.emit(DatabaseEventType.ERROR, error=RuntimeError("boom")))
        assert any("error" in e for e in listener.events)

    def test_emit_migration(self, bus: DatabaseEventBus, listener: _TestListener) -> None:
        bus.register(DatabaseEventType.MIGRATION, listener)
        mig = MigrationInfo(id="mig_001")
        asyncio.run(bus.emit(DatabaseEventType.MIGRATION, migration=mig))
        assert "migration:mig_001" in listener.events

    def test_listener_isolation(self, bus: DatabaseEventBus, listener: _TestListener) -> None:
        """A failing listener should not crash the bus."""
        class FailingListener(IDatabaseEventListener):
            async def on_connect(self, driver_name: str) -> None:
                raise RuntimeError("fail")
            async def on_disconnect(self, driver_name: str) -> None:
                pass
            async def on_query(self, query: str, duration_ms: float) -> None:
                pass
            async def on_error(self, error: Exception, query: str | None = None) -> None:
                pass
            async def on_migration(self, migration: MigrationInfo) -> None:
                pass

        bus.register(DatabaseEventType.CONNECT, FailingListener())
        bus.register(DatabaseEventType.CONNECT, listener)
        asyncio.run(bus.emit(DatabaseEventType.CONNECT, driver_name="test"))
        # listener still receives event despite failing listener
        assert "connect:test" in listener.events

    def test_multiple_listeners(self, bus: DatabaseEventBus) -> None:
        l1 = _TestListener()
        l2 = _TestListener()
        bus.register(DatabaseEventType.CONNECT, l1)
        bus.register(DatabaseEventType.CONNECT, l2)
        asyncio.run(bus.emit(DatabaseEventType.CONNECT, driver_name="multi"))
        assert "connect:multi" in l1.events
        assert "connect:multi" in l2.events
