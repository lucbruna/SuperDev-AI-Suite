from __future__ import annotations

import time

import pytest

from SuperDev.data.ingestion.connector import BaseConnector, ConnectorManager


class _MemoryConnector(BaseConnector):
    def __init__(self, name: str, rows: list[dict]) -> None:
        super().__init__(name)
        self.rows = rows
        self.read_count = 0

    async def connect(self) -> bool:
        self.connected = True
        return True

    async def read(self, query: dict | None = None) -> list[dict]:
        self.read_count += 1
        self._last_read_at = time.time()
        return self.rows

    async def disconnect(self) -> None:
        self.connected = False


class TestBaseConnector:
    @pytest.mark.asyncio
    async def test_lifecycle(self) -> None:
        connector = _MemoryConnector("mem", [{"a": 1}])
        assert await connector.connect()
        assert connector.connected is True
        rows = await connector.read()
        assert rows == [{"a": 1}]
        assert connector.get_status()["last_read_at"] is not None
        await connector.disconnect()
        assert connector.connected is False

    def test_status(self) -> None:
        connector = _MemoryConnector("mem", [])
        status = connector.get_status()
        assert status["name"] == "mem"
        assert status["type"] == "_MemoryConnector"
        assert status["connected"] is False


class TestConnectorManager:
    def test_register_get_list(self) -> None:
        manager = ConnectorManager()
        connector = _MemoryConnector("mem", [])
        manager.register(connector)
        assert manager.get("mem") is connector
        assert manager.names() == ["mem"]
        assert manager.unregister("mem") is True
        assert manager.get("mem") is None

    @pytest.mark.asyncio
    async def test_connect_all_and_disconnect_all(self) -> None:
        manager = ConnectorManager()
        a = _MemoryConnector("a", [])
        b = _MemoryConnector("b", [])
        manager.register(a)
        manager.register(b)
        results = await manager.connect_all()
        assert results == {"a": True, "b": True}
        assert a.connected and b.connected
        await manager.disconnect_all()
        assert not a.connected and not b.connected

    @pytest.mark.asyncio
    async def test_connect_all_isolates_failures(self) -> None:
        manager = ConnectorManager()

        class _Broken(_MemoryConnector):
            async def connect(self) -> bool:
                raise RuntimeError("boom")

        manager.register(_MemoryConnector("ok", []))
        manager.register(_Broken("bad", []))
        results = await manager.connect_all()
        assert results["ok"] is True
        assert results["bad"] is False
