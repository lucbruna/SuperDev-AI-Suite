from __future__ import annotations

import pytest

from SuperDev.data.ingestion.agent_ingestion import AgentCollector


class TestAgentCollector:
    @pytest.mark.asyncio
    async def test_record_and_collect(self) -> None:
        collector = AgentCollector("agents")
        collector.record_activity("planner", "plan", duration_ms=120.5, tokens_used=500)
        collector.record_activity("coder", "write_code", duration_ms=800.0)
        batch = await collector.collect()
        assert len(batch.records) == 2
        assert batch.records[0].data["agent"] == "planner"
        assert batch.records[0].data["tokens_used"] == 500

    @pytest.mark.asyncio
    async def test_agent_filter(self) -> None:
        collector = AgentCollector("agents")
        collector.record_activity("planner", "plan")
        collector.record_activity("coder", "code")
        batch = await collector.collect({"agent": "coder"})
        assert len(batch.records) == 1
        assert batch.records[0].data["agent"] == "coder"

    @pytest.mark.asyncio
    async def test_collect_clears_by_default(self) -> None:
        collector = AgentCollector("agents")
        collector.record_activity("planner", "plan")
        await collector.collect()
        batch = await collector.collect()
        assert len(batch.records) == 0

    @pytest.mark.asyncio
    async def test_callable_source(self) -> None:
        collector = AgentCollector("agents", config={"source": lambda: [
            {"agent": "reviewer", "action": "review"},
        ]})
        batch = await collector.collect()
        assert len(batch.records) == 1
        assert batch.records[0].data["agent"] == "reviewer"
