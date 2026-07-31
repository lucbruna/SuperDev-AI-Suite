from __future__ import annotations

import pytest

from SuperDev.data.data_engine import DataEngine
from SuperDev.data.data_factory import DataFactory
from SuperDev.data.data_manager import DataManager


class TestDataEngine:
    @pytest.mark.asyncio
    async def test_start_and_status(self, engine: DataEngine) -> None:
        status = engine.status()
        assert status["running"] is True
        assert len(status["subsystems"]) == 16

    @pytest.mark.asyncio
    async def test_health(self, engine: DataEngine) -> None:
        health = await engine.health()
        assert health["running"] is True
        assert health["subsystems_initialized"] == 16

    @pytest.mark.asyncio
    async def test_collect_and_process(self, engine: DataEngine) -> None:
        result = await engine.collect_and_process("demo", {"count": 50, "field": "value"})
        assert result["records"] == 50
        assert result["source"] == "demo"

    @pytest.mark.asyncio
    async def test_forecast_flow(self, engine: DataEngine) -> None:
        result = await engine.forecast([1, 2, 3, 4, 5], horizon=3)
        assert result["horizon"] == 3
        assert len(result["values"]) == 3

    @pytest.mark.asyncio
    async def test_report_flow(self, engine: DataEngine) -> None:
        result = await engine.generate_report("Exec Summary")
        assert result["title"] == "Exec Summary"

    @pytest.mark.asyncio
    async def test_emit_event(self, engine: DataEngine) -> None:
        result = await engine.emit_event("telemetry", {"cpu": 42})
        assert result["stream"] == "telemetry"


class TestDataFactory:
    def test_create_engine(self) -> None:
        engine = DataFactory.create_engine()
        assert isinstance(engine, DataEngine)


class TestDataManager:
    @pytest.mark.asyncio
    async def test_initialize(self) -> None:
        manager = DataManager()
        engine = await manager.initialize()
        assert engine.is_running is True
        assert manager.status()["initialized"] is True
        await manager.shutdown()
        assert manager.status()["initialized"] is False
