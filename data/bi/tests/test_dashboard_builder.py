from __future__ import annotations

import pytest

from SuperDev.data.bi.bi_engine import BIEngine
from SuperDev.data.bi.dashboard_builder import DashboardBuilder
from SuperDev.data.data_engine import DataEngine


class TestWidgets:
    def test_add_kpi(self) -> None:
        builder = DashboardBuilder(name="Exec")
        builder.add_kpi("Revenue", 1000.0, unit="USD", status="on_track")
        widgets = builder.widgets()
        assert len(widgets) == 1
        assert widgets[0]["type"] == "kpi"
        assert widgets[0]["value"] == 1000.0

    def test_chaining(self) -> None:
        builder = DashboardBuilder()
        result = builder.add_kpi("A", 1).add_text("B", "hello")
        assert result is builder
        assert builder.widget_count() == 2

    def test_add_chart_copies_data(self) -> None:
        builder = DashboardBuilder()
        data = {"a": 1}
        builder.add_chart("T", "bar", data)
        data["a"] = 999
        assert builder.widgets()[0]["data"] == {"a": 1}

    def test_clear(self) -> None:
        builder = DashboardBuilder()
        builder.add_kpi("A", 1)
        builder.add_table("T", ["x"], [{"x": 1}])
        assert builder.clear() == 2
        assert builder.widget_count() == 0


class TestBuild:
    def test_build_registers_dashboard(self, engine: DataEngine) -> None:
        builder = DashboardBuilder(bi=engine.bi, name="Ops", owner="analytics")
        builder.add_kpi("Uptime", 99.9, unit="%")
        builder.add_chart("Errors", "bar", {"e1": 2, "e2": 5})
        dashboard_id = builder.build()
        assert dashboard_id is not None
        assert builder.dashboard_id() == dashboard_id
        created = engine.bi.get_dashboard(dashboard_id)
        assert created is not None
        assert created.name == "Ops"
        assert len(created.widgets) == 2

    def test_build_without_engine_raises(self) -> None:
        builder = DashboardBuilder()
        builder.add_kpi("A", 1)
        with pytest.raises(ValueError):
            builder.build()


class TestRendering:
    def test_render_html(self, engine: DataEngine) -> None:
        builder = DashboardBuilder(bi=engine.bi, name="Report", columns=2)
        builder.add_kpi("Revenue", 1000.0, unit="USD", status="on_track")
        builder.add_table("Top", ["sku", "qty"], [{"sku": "A", "qty": 3}])
        builder.add_text("Note", "All good")
        html = builder.render_html()
        assert "<html" in html
        assert "Revenue" in html
        assert "Top" in html
        assert "kpi-card" in html

    def test_render_html_chart_bars(self, engine: DataEngine) -> None:
        builder = DashboardBuilder(bi=engine.bi)
        builder.add_chart("Costs", "bar", {"p1": 10.0, "p2": 20.0})
        html = builder.render_html()
        assert "bar-chart" in html
        assert "p1" in html

    def test_render_json(self, engine: DataEngine) -> None:
        builder = DashboardBuilder(bi=engine.bi, name="J")
        builder.add_kpi("K", 5, unit="x")
        payload = builder.render_json()
        assert '"name": "J"' in payload
        assert '"kpi"' in payload
        assert '"columns"' in payload

    def test_render_html_escapes(self, engine: DataEngine) -> None:
        builder = DashboardBuilder(bi=engine.bi)
        builder.add_text("Note", "<script>alert(1)</script>")
        html = builder.render_html()
        assert "<script>alert(1)</script>" not in html
        assert "&lt;script&gt;" in html


class TestIntegration:
    def test_full_flow(self, engine: DataEngine) -> None:
        builder = DashboardBuilder(bi=engine.bi, name="Full")
        builder.add_kpi("Projetos", 12, status="good")
        builder.add_kpi("Erros", 3, status="warning")
        builder.add_chart("Trend", "bar", {"d1": 1, "d2": 2})
        builder.build()
        assert engine.bi.list_dashboards()
        html = builder.render_html()
        assert "Projetos" in html and "Erros" in html

    def test_bi_engine_type_hint(self, engine: DataEngine) -> None:
        bi: BIEngine = engine.bi
        builder = DashboardBuilder(bi=bi)
        builder.add_kpi("A", 1)
        builder.build()
        assert bi.list_dashboards()
