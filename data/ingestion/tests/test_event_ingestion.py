from __future__ import annotations

import pytest

from SuperDev.data.ingestion.event_ingestion import EventCollector


class TestEventCollector:
    @pytest.mark.asyncio
    async def test_add_and_collect(self) -> None:
        collector = EventCollector("events")
        collector.add_event({"type": "click", "value": 1}, stream="ui")
        collector.add_event({"type": "click", "value": 2}, stream="ui")
        batch = await collector.collect()
        assert len(batch.records) == 2
        assert batch.records[0].data["value"] == 1
        assert batch.records[0].data["stream"] == "ui"

    @pytest.mark.asyncio
    async def test_collect_clears_by_default(self) -> None:
        collector = EventCollector("events")
        collector.add_event({"value": 1})
        await collector.collect()
        batch = await collector.collect()
        assert len(batch.records) == 0

    @pytest.mark.asyncio
    async def test_collect_keep_without_clear(self) -> None:
        collector = EventCollector("events")
        collector.add_event({"value": 1})
        batch = await collector.collect({"clear": False})
        assert len(batch.records) == 1
        batch2 = await collector.collect({"clear": False})
        assert len(batch2.records) == 1

    @pytest.mark.asyncio
    async def test_collect_from_callable_source(self) -> None:
        collector = EventCollector("events", config={"source": lambda: [
            {"a": 1}, {"a": 2},
        ]})
        batch = await collector.collect()
        assert len(batch.records) == 2

    @pytest.mark.asyncio
    async def test_add_many(self) -> None:
        collector = EventCollector("events")
        assert collector.add_many([{"x": 1}, {"x": 2}, {"x": 3}]) == 3
        batch = await collector.collect()
        assert len(batch.records) == 3
