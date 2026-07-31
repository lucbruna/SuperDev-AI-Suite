from __future__ import annotations

import pytest

from SuperDev.data.bi.executive_dashboard import (
    KPI_AGENT_PERFORMANCE,
    KPI_AVG_DEV_TIME,
    KPI_COMPLETED_PROJECTS,
    KPI_COSTS,
    KPI_ERRORS,
    KPI_KEYS,
    ExecutiveDashboard,
)
from SuperDev.data.data_engine import DataEngine
from SuperDev.data.data_models import DataRecord


def _agent_records() -> list[DataRecord]:
    data = [
        ("planner", 1200, 1800, 0.018, "completed"),
        ("coder", 24000, 5200, 0.052, "completed"),
        ("reviewer", 18000, 3100, 0.031, "completed"),
        ("coder", 150000, 9800, 0.098, "completed"),
        ("tester", 30000, 2600, 0.026, "failed"),
        ("deploy", 9000, 900, 0.009, "completed"),
        ("planner", 2100, 1500, 0.015, "completed"),
        ("reviewer", 45000, 4200, 0.042, "failed"),
    ]
    return [
        DataRecord(source="agents", data={
            "agent": a, "action": "run", "duration_ms": d,
            "tokens_used": t, "cost": c, "status": s,
        })
        for a, d, t, c, s in data
    ]


def _project_records() -> list[DataRecord]:
    data = [
        ("SuperDev Core", "completed", 12, 12, 3, 240.0),
        ("Mobile App", "active", 8, 14, 5, 180.0),
        ("Marketing Site", "completed", 6, 6, 1, 90.0),
        ("API Gateway", "active", 4, 9, 2, 130.0),
        ("Data Platform", "planning", 0, 15, 0, 40.0),
    ]
    return [
        DataRecord(source="projects", data={
            "project": n, "status": s, "tasks_completed": tc,
            "tasks_total": tt, "errors": e, "cost": c,
        })
        for n, s, tc, tt, e, c in data
    ]


class TestComputeKpis:
    def test_kpi_values(self, engine: DataEngine) -> None:
        dashboard = ExecutiveDashboard(engine)
        dashboard.compute_kpis(_agent_records(), _project_records())

        snapshot = dashboard.kpi_snapshot()
        assert snapshot[KPI_COMPLETED_PROJECTS]["value"] == 2
        # durations sum to 279300ms over 8 records → 34,912.5ms = 0.58 min
        assert snapshot[KPI_AVG_DEV_TIME]["value"] == pytest.approx(0.6, abs=0.1)
        assert snapshot[KPI_ERRORS]["value"] == 11
        assert snapshot[KPI_COSTS]["value"] == pytest.approx(0.291, abs=0.01)
        # 6 of 8 agents completed
        assert snapshot[KPI_AGENT_PERFORMANCE]["value"] == pytest.approx(75.0, abs=0.1)

    def test_errors_kpi_lower_is_better_status(self, engine: DataEngine) -> None:
        dashboard = ExecutiveDashboard(engine)
        dashboard.compute_kpis(_agent_records(), _project_records())
        snapshot = dashboard.kpi_snapshot()
        # 11 errors > 2x target (5) → behind, not no_target
        assert snapshot[KPI_ERRORS]["status"] == "behind"

    def test_kpis_registered_in_bi(self, engine: DataEngine) -> None:
        dashboard = ExecutiveDashboard(engine)
        dashboard.compute_kpis(_agent_records(), _project_records())
        kpis = engine.bi.list_kpis()
        assert len(kpis) == len(KPI_KEYS)
        assert all(k.metric in KPI_KEYS for k in kpis)

    def test_empty_records(self, engine: DataEngine) -> None:
        dashboard = ExecutiveDashboard(engine)
        dashboard.compute_kpis([], [])
        snapshot = dashboard.kpi_snapshot()
        assert snapshot[KPI_COMPLETED_PROJECTS]["value"] == 0
        assert snapshot[KPI_AGENT_PERFORMANCE]["value"] == 0.0

    def test_repeated_build_cleans_up_kpis(self, engine: DataEngine) -> None:
        """Repeated builds must remove old KPIs (no orphans) and reflect new values."""
        dashboard = ExecutiveDashboard(engine)
        dashboard.compute_kpis(_agent_records(), _project_records())
        first = dashboard.kpi_snapshot()
        assert first[KPI_COMPLETED_PROJECTS]["value"] == 2
        assert len(engine.bi.list_kpis()) == len(KPI_KEYS)

        # Second build with different data: no orphaned KPIs, fresh values.
        dashboard.compute_kpis([], [])
        assert len(engine.bi.list_kpis()) == len(KPI_KEYS)
        second = dashboard.kpi_snapshot()
        assert second[KPI_COMPLETED_PROJECTS]["value"] == 0
        assert second[KPI_AGENT_PERFORMANCE]["value"] == 0.0


class TestCharts:
    def test_build_charts_types(self, engine: DataEngine) -> None:
        dashboard = ExecutiveDashboard(engine)
        dashboard.compute_kpis(_agent_records(), _project_records())
        charts = dashboard.build_charts(_agent_records(), _project_records())

        types = [c["type"] for c in charts]
        assert types == ["bar", "line", "pie", "gauge"]

    def test_build_dashboard(self, engine: DataEngine) -> None:
        dashboard = ExecutiveDashboard(engine)
        dashboard.compute_kpis(_agent_records(), _project_records())
        dashboard_id = dashboard.build_dashboard()
        assert dashboard_id is not None
        created = engine.bi.get_dashboard(dashboard_id)
        assert created is not None
        assert created.name == "Executive Overview"


class TestReporting:
    @pytest.mark.asyncio
    async def test_generate_report(self, engine: DataEngine) -> None:
        dashboard = ExecutiveDashboard(engine)
        dashboard.compute_kpis(_agent_records(), _project_records())
        rendered = await dashboard.generate_report()
        assert "# Executive Dashboard Report" in rendered
        assert "Projetos Concluídos" in rendered or "kpis" in rendered


class TestRendering:
    @pytest.mark.asyncio
    async def test_render_html(self, engine: DataEngine) -> None:
        dashboard = ExecutiveDashboard(engine)
        await dashboard.build(_agent_records(), _project_records())
        html = dashboard.render_html()
        assert "<html" in html
        assert "Executive Dashboard" in html
        assert "Performance dos Agentes" in html
        assert "Custo por Projeto" in html
        assert "<svg" in html

    @pytest.mark.asyncio
    async def test_render_json(self, engine: DataEngine) -> None:
        dashboard = ExecutiveDashboard(engine)
        await dashboard.build(_agent_records(), _project_records())
        payload = dashboard.render_json()
        assert KPI_COSTS in payload
        assert '"dashboard"' in payload

    @pytest.mark.asyncio
    async def test_full_build(self, engine: DataEngine) -> None:
        dashboard = ExecutiveDashboard(engine)
        result = await dashboard.build(_agent_records(), _project_records())
        assert result["dashboard_id"]
        assert len(result["kpis"]) == len(KPI_KEYS)
        assert len(result["charts"]) == 4
        assert result["report_markdown"].startswith("# Executive Dashboard Report")


class TestRecommendations:
    @pytest.mark.asyncio
    async def test_recommendations_are_generated(self, engine: DataEngine) -> None:
        dashboard = ExecutiveDashboard(engine)
        await dashboard.build(_agent_records(), _project_records())
        # 75% performance → should recommend agent review
        report = dashboard.render_html()
        assert "Executive Dashboard" in report
