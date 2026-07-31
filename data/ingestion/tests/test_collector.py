from __future__ import annotations

import pytest

from SuperDev.data.data_models import DataSourceType
from SuperDev.data.ingestion.collector import BaseCollector, CollectorManager


class _FakeCollector(BaseCollector):
    def get_source_type(self) -> DataSourceType:
        return DataSourceType.API

    async def collect(self, config: dict | None = None) -> object:
        return self._build_batch([{"id": 1}, {"id": 2}], metadata={"fake": True})


class TestBaseCollector:
    @pytest.mark.asyncio
    async def test_build_batch(self) -> None:
        collector = _FakeCollector("fake")
        batch = await collector.collect()
        assert batch.source == "fake"
        assert len(batch.records) == 2
        assert batch.records[0].data == {"id": 1}
        assert collector._collected_count == 2  # noqa: SLF001

    def test_status(self) -> None:
        collector = _FakeCollector("fake")
        status = collector.get_status()
        assert status["source_type"] == "api"


class TestCollectorManager:
    def test_register_get_list(self) -> None:
        manager = CollectorManager()
        collector = _FakeCollector("fake")
        manager.register(collector)
        assert manager.get("fake") is collector
        assert manager.names() == ["fake"]
        assert manager.unregister("fake") is True

    @pytest.mark.asyncio
    async def test_collect(self) -> None:
        manager = CollectorManager()
        manager.register(_FakeCollector("fake"))
        batch = await manager.collect("fake")
        assert len(batch.records) == 2

    @pytest.mark.asyncio
    async def test_collect_missing_raises(self) -> None:
        manager = CollectorManager()
        with pytest.raises(ValueError):
            await manager.collect("nope")
