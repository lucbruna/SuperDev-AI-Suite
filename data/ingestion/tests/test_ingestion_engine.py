from __future__ import annotations

import pytest

from SuperDev.data.data_engine import DataEngine
from SuperDev.data.data_models import DataSourceType
from SuperDev.data.ingestion.agent_ingestion import AgentCollector
from SuperDev.data.ingestion.connector import BaseConnector
from SuperDev.data.ingestion.event_ingestion import EventCollector
from SuperDev.data.ingestion.file_ingestion import FileConnector


class _FakeConnector(BaseConnector):
    """New-style connector returning canned rows — no network or filesystem needed."""

    def __init__(self, name: str, rows: list[dict]) -> None:
        super().__init__(name)
        self.rows = rows

    async def connect(self) -> bool:
        self.connected = True
        return True

    async def read(self, query: dict | None = None) -> list[dict]:
        return self.rows

    async def disconnect(self) -> None:
        self.connected = False


class TestIngestionEngine:
    @pytest.mark.asyncio
    async def test_register_connector_and_ingest(self, engine: DataEngine, tmp_path) -> None:
        path = tmp_path / "users.csv"
        path.write_text("id,name\n1,ana\n2,bob\n", encoding="utf-8")
        connector = FileConnector("users", {"path": str(path)})
        engine.ingestion.register_connector(connector)

        source = engine.ingestion.get_source("users")
        assert source is not None
        assert source.source_type == DataSourceType.FILE

        batch = await engine.ingestion.ingest("users")
        assert len(batch.records) == 2
        assert batch.records[0].data["name"] == "ana"

    @pytest.mark.asyncio
    async def test_register_collector_and_ingest(self, engine: DataEngine) -> None:
        collector = AgentCollector("agent-activity")
        collector.record_activity("planner", "plan")
        engine.ingestion.register_collector(collector)

        source = engine.ingestion.get_source("agent-activity")
        assert source is not None
        assert source.source_type == DataSourceType.AGENT

        batch = await engine.ingestion.ingest("agent-activity")
        assert len(batch.records) == 1
        assert batch.records[0].data["agent"] == "planner"

    @pytest.mark.asyncio
    async def test_connector_preferred_over_legacy(self, engine: DataEngine) -> None:
        # Legacy registry connector
        class _Legacy:
            async def read(self, query=None):
                return [{"origin": "legacy"}]

        engine.registry.register_connector("dupe", _Legacy())

        # New-style connector registered later takes precedence
        engine.ingestion.register_connector(_FakeConnector("dupe", [{"origin": "new-style"}]))

        batch = await engine.ingestion.ingest("dupe")
        assert len(batch.records) == 1
        assert batch.records[0].data["origin"] == "new-style"

    @pytest.mark.asyncio
    async def test_legacy_connector_fallback(self, engine: DataEngine) -> None:
        class _Legacy:
            async def read(self, query=None):
                return [{"origin": "legacy"}]

        engine.registry.register_connector("legacy-source", _Legacy())
        batch = await engine.ingestion.ingest("legacy-source")
        assert len(batch.records) == 1
        assert batch.records[0].data["origin"] == "legacy"

    @pytest.mark.asyncio
    async def test_synthesized_fallback(self, engine: DataEngine) -> None:
        batch = await engine.ingestion.ingest("unknown", {"count": 3, "field": "x"})
        assert len(batch.records) == 3
        assert batch.records[0].data["x"] == 0

    @pytest.mark.asyncio
    async def test_collect_via_manager(self, engine: DataEngine) -> None:
        collector = EventCollector("ui-events")
        collector.add_event({"action": "login"})
        engine.ingestion.register_collector(collector)
        batch = await engine.ingestion.collectors.collect("ui-events")
        assert len(batch.records) == 1

    @pytest.mark.asyncio
    async def test_status_includes_managers(self, engine: DataEngine) -> None:
        engine.ingestion.register_collector(AgentCollector("a1"))
        status = engine.ingestion.status()
        assert status["connectors"]["count"] == 0
        assert status["collectors"]["count"] == 1
