"""Tests for the visualization and reporting subsystems (Fase 6)."""

from __future__ import annotations

from datetime import datetime
from typing import cast

import pytest

from data_intelligence.data_context import DataIntelligenceContext
from data_intelligence.data_events import DataIntelligenceEvents
from data_intelligence.data_metrics import DataIntelligenceMetrics
from data_intelligence.data_models import ReportFormat, DashboardSpec
from data_intelligence.visualization.base import (VisualizationError, Widget)
from data_intelligence.visualization.charts import CHART_BUILDERS
from data_intelligence.visualization.dashboard import DashboardBuilder
from data_intelligence.visualization.dashboard_specs import (
    PREBUILT_DASHBOARDS, default_dashboard, get_dashboard)
from data_intelligence.visualization.engine import VisualizationEngine
from data_intelligence.reporting.base import ReportingError
from data_intelligence.reporting.engine import ReportingEngine
from data_intelligence.reporting.formats import (CsvRenderer, HtmlRenderer,
                                                 JsonRenderer,
                                                 MarkdownRenderer,
                                                 RENDERERS, render_report)
from data_intelligence.reporting.scheduler import ReportScheduler
from data_intelligence.reporting.templates import get_template


def make_visualization_engine() -> VisualizationEngine:
    return VisualizationEngine(events=DataIntelligenceEvents(),
                               metrics=DataIntelligenceMetrics(),
                               config=None, context=DataIntelligenceContext())


def make_reporting_engine() -> ReportingEngine:
    return ReportingEngine(events=DataIntelligenceEvents(),
                           metrics=DataIntelligenceMetrics(),
                           config=None, context=DataIntelligenceContext())


# ---------------------------------------------------------------------------
# visualization: widgets and chart builders
# ---------------------------------------------------------------------------

def test_widget_to_dict():
    widget = Widget("rev", "kpi", "Receita", suffix=" R$")
    assert widget.to_dict() == {
        "widget_id": "rev", "type": "kpi", "title": "Receita",
        "config": {"suffix": " R$"}}


def test_chart_builders_registry():
    for kind in ("bar", "line", "pie", "kpi", "table"):
        assert kind in CHART_BUILDERS


def test_bar_chart_from_dict():
    chart = CHART_BUILDERS["bar"].build(
        Widget("p", "bar", "Por região", label="regiao", value="valor"),
        {"SP": 120, "RJ": 80})
    assert chart["type"] == "bar"
    assert chart["labels"] == ["SP", "RJ"]
    assert chart["values"] == [120.0, 80.0]


def test_line_chart_keeps_category_order():
    chart = CHART_BUILDERS["line"].build(
        Widget("t", "line", "Tendência"), {"Jan": 10, "Fev": 20, "Mar": 15})
    assert chart["categories"] == ["Jan", "Fev", "Mar"]
    assert chart["values"] == [10.0, 20.0, 15.0]


def test_pie_chart_slices_with_percent():
    chart = CHART_BUILDERS["pie"].build(
        Widget("s", "pie", "Share"), {"SP": 75, "RJ": 25})
    assert chart["slices"] == [
        {"label": "SP", "value": 75, "percent": 75.0},
        {"label": "RJ", "value": 25, "percent": 25.0}]


def test_kpi_chart_number_and_dict():
    assert CHART_BUILDERS["kpi"].build(Widget("k", "kpi", "V"),
                                       42)["value"] == 42.0
    assert CHART_BUILDERS["kpi"].build(
        Widget("k", "kpi", "V"), {"total": 7})["value"] == 7.0


def test_table_chart_uses_config_columns():
    chart = CHART_BUILDERS["table"].build(
        Widget("tb", "table", "Pedidos", columns=["id", "status"]),
        [{"id": 1, "status": "novo", "extra": "x"},
         {"id": 2, "status": "finalizado"}])
    assert chart["columns"] == ["id", "status"]
    assert chart["rows"] == [[1, "novo"], [2, "finalizado"]]


def test_unsupported_widget_type_not_registered():
    assert CHART_BUILDERS.get("gauge") is None


# ---------------------------------------------------------------------------
# visualization: dashboards
# ---------------------------------------------------------------------------

def test_dashboard_builder_create_and_render():
    builder = DashboardBuilder()
    spec = builder.create("d1", "Diretoria", "executive")
    builder.add_widget(spec, "revenue", "kpi", "Receita")
    builder.add_widget(spec, "trend", "line", "Vendas")
    rendered = builder.render(spec, {"revenue": {"total": 1000},
                                     "trend": {"Jan": 1, "Fev": 2}})
    assert rendered["dashboard_id"] == "d1"
    assert rendered["audience"] == "executive"
    assert [w["type"] for w in rendered["widgets"]] == ["kpi", "line"]


def test_dashboard_builder_unknown_audience():
    builder = DashboardBuilder()
    with pytest.raises(VisualizationError):
        builder.create("x", "X", "marketing")


def test_dashboard_builder_unknown_widget_type():
    builder = DashboardBuilder()
    spec = builder.create("d2", "D2", "executive")
    builder.add_widget(spec, "w", "gauge", "Gauge")
    with pytest.raises(VisualizationError):
        builder.render(spec, {"w": 1})


def test_prebuilt_dashboards_for_all_audiences():
    assert sorted(PREBUILT_DASHBOARDS) == [
        "executive_overview", "it_health", "operations_floor"]
    for audience in ("executive", "operations", "it"):
        spec = default_dashboard(audience)
        assert spec.audience == audience
        assert spec.widgets


def test_get_dashboard_by_id_and_unknown():
    assert get_dashboard("it_health").name == "Saúde de TI"
    with pytest.raises(VisualizationError):
        get_dashboard("nope")
    with pytest.raises(VisualizationError):
        default_dashboard("marketing")


def test_prebuilt_dashboards_render_with_sample_data():
    builder = DashboardBuilder()
    for spec in PREBUILT_DASHBOARDS.values():
        data = {}
        for w in spec.widgets:
            if w["type"] == "line":
                data[w["widget_id"]] = {"a": 1, "b": 2}
            elif w["type"] == "table":
                data[w["widget_id"]] = [{"id": 1, "status": "ok"}]
            else:
                data[w["widget_id"]] = {"a": 10, "b": 20}
        rendered = builder.render(spec, data)
        assert len(rendered["widgets"]) == len(spec.widgets)


# ---------------------------------------------------------------------------
# visualization: engine
# ---------------------------------------------------------------------------

def test_visualization_engine_flow():
    viz = make_visualization_engine()
    spec = viz.create_dashboard("exec", "Diretoria", "executive")
    viz.add_widget(spec, "revenue", "kpi", "Receita")
    rendered = viz.render("exec", {"revenue": {"total": 500}})
    assert rendered["widgets"][0]["type"] == "kpi"
    assert rendered["widgets"][0]["value"] == 500.0
    assert viz.metrics.snapshot()["counters"]["visualization.renders"] == 1


def test_visualization_engine_unknown_dashboard():
    viz = make_visualization_engine()
    with pytest.raises(VisualizationError):
        viz.render("missing", {})


def test_visualization_engine_build_chart():
    viz = make_visualization_engine()
    chart = viz.build_chart("pie", "Share", {"SP": 3, "RJ": 1})
    assert chart["type"] == "pie"
    assert chart["slices"][0]["label"] == "SP"
    with pytest.raises(VisualizationError):
        viz.build_chart("gauge", "G", 1)


def test_default_dashboard_via_engine():
    viz = make_visualization_engine()
    spec = default_dashboard("operations")
    rendered = viz.render(spec.dashboard_id, {
        "orders_today": {"value": 88}, "top_products": {"A": 5, "B": 3},
        "order_queue": [{"id": 1, "status": "novo"}]})
    assert rendered["audience"] == "operations"
    assert {w["type"] for w in rendered["widgets"]} == {"kpi", "bar", "table"}


# ---------------------------------------------------------------------------
# reporting: renderers
# ---------------------------------------------------------------------------

REPORT_PAYLOAD = {
    "name": "Relatório Executivo", "summary": {"receita": 1000},
    "tables": [{"title": "Vendas", "columns": ["regiao", "valor"],
                "rows": [{"regiao": "SP", "valor": 600},
                         {"regiao": "RJ", "valor": 400}]}]}


def test_json_renderer():
    content = render_report(ReportFormat.JSON, REPORT_PAYLOAD)
    assert '"name": "Relatório Executivo"' in content
    assert '"regiao": "SP"' in content


def test_markdown_renderer():
    content = render_report(ReportFormat.MARKDOWN, REPORT_PAYLOAD)
    assert "# Relatório Executivo" in content
    assert "| regiao | valor |" in content
    assert "| SP | 600 |" in content


def test_html_renderer():
    content = render_report(ReportFormat.HTML, REPORT_PAYLOAD)
    assert "<h1>Relatório Executivo</h1>" in content
    assert "<th>regiao</th>" in content
    assert "<td>SP</td>" in content


def test_csv_renderer():
    content = render_report(ReportFormat.CSV, REPORT_PAYLOAD)
    assert content.splitlines()[0] == "regiao,valor"
    assert "SP,600" in content


def test_unsupported_format_raises():
    with pytest.raises(ReportingError):
        render_report(cast(ReportFormat, "pdf"), REPORT_PAYLOAD)


def test_renderer_registry_types():
    assert isinstance(RENDERERS[ReportFormat.JSON], JsonRenderer)
    assert isinstance(RENDERERS[ReportFormat.MARKDOWN], MarkdownRenderer)
    assert isinstance(RENDERERS[ReportFormat.HTML], HtmlRenderer)
    assert isinstance(RENDERERS[ReportFormat.CSV], CsvRenderer)


# ---------------------------------------------------------------------------
# reporting: templates
# ---------------------------------------------------------------------------

def test_template_instantiate_fills_sections():
    template = get_template("executive")
    assert template is not None
    filled = template.instantiate({"summary": {"receita": 10},
                                   "recommendations": ["reduzir preço"]})
    assert filled["name"] == "executive"
    assert filled["sections"][0]["data"] == {"receita": 10}
    assert filled["sections"][2]["data"] == ["reduzir preço"]


def test_unknown_template_returns_none():
    assert get_template("space") is None


# ---------------------------------------------------------------------------
# reporting: scheduler
# ---------------------------------------------------------------------------

def test_scheduler_cron_matches_and_due():
    scheduler = ReportScheduler()
    scheduler.schedule("weekly", "0 9 * * 1")  # segunda às 09:00
    monday = datetime(2026, 7, 27, 9, 0)  # segunda-feira
    assert scheduler.due("weekly", monday)
    assert not scheduler.due("weekly",
                             datetime(2026, 7, 28, 9, 0))  # terça


def test_scheduler_star_and_ranges():
    scheduler = ReportScheduler()
    scheduler.schedule("daily", "*/5 8-18 * * *")
    assert scheduler.due("daily", datetime(2026, 7, 27, 8, 5))
    assert scheduler.due("daily", datetime(2026, 7, 27, 18, 0))
    assert not scheduler.due("daily", datetime(2026, 7, 27, 7, 55))


def test_scheduler_invalid_cron_and_mark_run():
    scheduler = ReportScheduler()
    with pytest.raises(ReportingError):
        scheduler.schedule("bad", "not-a-cron")
    scheduler.schedule("r", "0 0 * * *")
    scheduler.mark_run("r", "2026-07-27T00:00:00")
    assert scheduler.list_jobs()["r"]["last_run"] == "2026-07-27T00:00:00"
    with pytest.raises(ReportingError):
        scheduler.due("missing", datetime.now())


# ---------------------------------------------------------------------------
# reporting: engine
# ---------------------------------------------------------------------------

def test_reporting_engine_generate_json():
    engine = make_reporting_engine()
    engine.register("exec1", "Executivo", "executive", ReportFormat.JSON)
    result = engine.generate("exec1", {
        "summary": {"receita": 1000},
        "indicators": [{"nome": "receita", "valor": 1000}],
        "recommendations": ["reduzir preço"]})
    assert result["format"] == "json"
    assert "Executivo" in result["content"]
    assert result["payload"]["tables"]
    assert engine.metrics.snapshot()["counters"]["reporting.generated"] == 1
    latest = engine.latest("exec1")
    assert latest is not None
    assert latest["report_id"] == "exec1"


def test_reporting_engine_generate_markdown():
    engine = make_reporting_engine()
    engine.register("exec2", "Executivo", "executive",
                    ReportFormat.MARKDOWN)
    result = engine.generate("exec2", {"summary": {"receita": 1000}})
    assert result["content"].startswith("# Executivo")


def test_reporting_engine_unknown_report():
    engine = make_reporting_engine()
    with pytest.raises(ReportingError):
        engine.generate("ghost", {})


def test_reporting_engine_scheduled_run_due():
    engine = make_reporting_engine()
    engine.register("daily1", "Diário", "operational",
                    ReportFormat.JSON, schedule_cron="0 9 * * *")
    generated = engine.run_due(datetime(2026, 7, 27, 9, 0))
    assert len(generated) == 1
    assert engine.scheduler.list_jobs()["daily1"]["last_run"] is not None
    # sem match fora do horário
    assert engine.run_due(datetime(2026, 7, 27, 10, 0)) == []


def test_reporting_engine_remove():
    engine = make_reporting_engine()
    engine.register("tmp", "Temp", "financial", ReportFormat.JSON)
    assert engine.remove("tmp")
    assert not engine.remove("tmp")
    with pytest.raises(ReportingError):
        engine.generate("tmp", {})


def test_reporting_engine_stats():
    engine = make_reporting_engine()
    engine.register("a", "A", "financial")
    engine.generate("a", {"summary": {"margem": 0.2}})
    stats = engine.stats()
    assert stats["reports"] == ["a"]
    assert stats["generated"] == 1
