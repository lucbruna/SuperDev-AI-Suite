from __future__ import annotations

import pytest

from SuperDev.data.ingestion.project_ingestion import ProjectCollector


class TestProjectCollector:
    @pytest.mark.asyncio
    async def test_add_and_collect(self) -> None:
        collector = ProjectCollector("projects")
        collector.add_project("app-a", status="completed", tasks_completed=10, tasks_total=10)
        collector.add_project("app-b", status="active", tasks_completed=3, tasks_total=8)
        batch = await collector.collect()
        assert len(batch.records) == 2
        assert batch.records[0].data["project"] == "app-a"

    @pytest.mark.asyncio
    async def test_status_filter(self) -> None:
        collector = ProjectCollector("projects")
        collector.add_project("app-a", status="completed")
        collector.add_project("app-b", status="active")
        batch = await collector.collect({"status": "active"})
        assert len(batch.records) == 1
        assert batch.records[0].data["project"] == "app-b"

    @pytest.mark.asyncio
    async def test_callable_source(self) -> None:
        collector = ProjectCollector("projects", config={"source": lambda: [
            {"project": "app-c", "status": "active"},
        ]})
        batch = await collector.collect()
        assert len(batch.records) == 1
        assert batch.records[0].data["project"] == "app-c"
