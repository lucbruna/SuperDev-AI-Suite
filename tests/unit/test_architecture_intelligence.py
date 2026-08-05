"""Unit tests for the architecture_intelligence module (volume 2).

Covers config, history, forecasting, trends, insights, roadmap, optimizer,
graph Q&A assistant, diagnostics, agents, workflows, event bus, scheduler,
reports, API router and CLI. Graph-dependent tests use the same small temp
fixture project as the Architecture Graph tests.
"""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any

import pytest

from modules.architecture_graph.config.graph_config import GraphConfig
from modules.architecture_graph.core.graph_engine import GraphEngine
from modules.architecture_intelligence.core.engine import (
    ArchitectureIntelligenceEngine,
    _nested,
)
from modules.architecture_intelligence.core.history import MetricHistory


# ------------------------------------------------------------------ fixtures
def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.fixture()
def fixture_root(tmp_path: Path) -> Path:
    root = tmp_path / "fixture"
    _write(root, "src/app.py", "from lib import helper\nimport db\n\ndef main():\n    return helper()\n")
    _write(root, "src/lib.py", "import db\n\ndef helper():\n    return 42\n")
    _write(root, "src/db.py", "def connect():\n    return 'conn'\n")
    _write(root, "workflows/release.yaml", "name: release\nformat: yaml\nagents: [builder]\nsteps: []\n")
    return root


@pytest.fixture()
def graph(fixture_root: Path, tmp_path: Path) -> Any:
    config = GraphConfig()
    config.project_root = str(fixture_root)
    config.project_dirs = ("src", "workflows")
    config.scan_frontend = False
    config.storage_backend = "memory"
    config.data_dir = str(tmp_path / "data")
    return GraphEngine(config).build()


@pytest.fixture()
def history(tmp_path: Path) -> MetricHistory:
    return MetricHistory(str(tmp_path / "history.json"), limit=50)


class StubGraphEngine:
    """Minimal stand-in for the Architecture Graph engine."""

    def __init__(self, graph: Any) -> None:
        self._graph = graph

    def ensure_graph(self, *, build_if_missing: bool = True) -> Any:
        return self._graph

    def analyze(self) -> dict[str, Any]:
        return {
            "available": True,
            "stats": self._graph.stats(),
            "score": {"score": 50.0},
            "integrity_summary": {"total": 0},
        }


class StubEngine:
    """Minimal stand-in for the intelligence engine facade."""

    available = True

    def __init__(self, graph: Any, *, broken_graph: bool = False) -> None:
        self._graph = graph
        self.broken = broken_graph

    def graph(self, *, build_if_missing: bool = True) -> Any:
        if self.broken:
            raise RuntimeError("graph unavailable")
        return self._graph

    def history_recent(self, limit: int = 1) -> dict[str, Any]:
        return {"available": True, "count": 0, "snapshots": []}

    def analyze(self) -> dict[str, Any]:
        return {"available": True, "metrics": {}, "trends": {}, "forecast": {}}

    def insights(self) -> dict[str, Any]:
        return {"available": True, "insights": []}

    def agents(self) -> dict[str, Any]:
        return {"agents": {}, "count": 0, "errors": [], "generated_at": ""}

    def snapshot(self) -> dict[str, Any]:
        return {"available": True, "appended": False}


def _engine(graph: Any, history: MetricHistory) -> ArchitectureIntelligenceEngine:
    engine = ArchitectureIntelligenceEngine(history=history)
    engine._graph_engine = StubGraphEngine(graph)  # type: ignore[attr-defined]
    return engine


def _forecast(history: MetricHistory, horizon: int = 5) -> dict[str, Any]:
    from modules.architecture_intelligence.prediction.forecast import ForecastEngine

    return ForecastEngine(history, horizon).run()


def _trends(history: MetricHistory) -> dict[str, Any]:
    from modules.architecture_intelligence.prediction.trends import TrendAnalyzer

    return TrendAnalyzer(history).analyze()


# ------------------------------------------------------------------- history
class TestMetricHistory:
    def test_append_and_recent(self, history: MetricHistory) -> None:
        assert history.append({"ts": 1.0, "nodes": 10})
        assert history.append({"ts": 2.0, "nodes": 20})
        assert history.count() == 2
        assert history.recent(1) == [{"ts": 2.0, "nodes": 20}]

    def test_series_dig_nested_keys(self, history: MetricHistory) -> None:
        history.append({"ts": 1.0, "score": {"score": 50.0}})
        timestamps, values = history.series("score.score")
        assert values == [50.0]
        assert timestamps == [1.0]

    def test_throttle_min_interval(self, history: MetricHistory) -> None:
        history.append({"ts": time.time(), "nodes": 1})
        assert not history.append({"ts": time.time(), "nodes": 2}, min_interval_seconds=60)
        assert history.count() == 1

    def test_roundtrip_persists(self, tmp_path: Path) -> None:
        path = str(tmp_path / "h.json")
        MetricHistory(path).append({"ts": 1.0, "nodes": 5})
        reloaded = MetricHistory(path)
        assert reloaded.count() == 1
        assert reloaded.recent(1)[0]["nodes"] == 5


# ------------------------------------------------------------ prediction
class TestForecast:
    def test_not_enough_history(self, history: MetricHistory) -> None:
        history.append({"ts": 1.0, "nodes": 10})
        result = _forecast(history)
        assert result["forecasts"] == []

    def test_forecast_projects_metrics(self, history: MetricHistory) -> None:
        for i, nodes in enumerate([10, 20, 30, 40, 50]):
            history.append({"ts": float(i), "nodes": nodes, "edges": nodes * 2, "score": nodes / 10})
        result = _forecast(history, horizon=3)
        assert result["available"] is True
        by_metric = {f["metric"]: f for f in result["forecasts"]}
        assert by_metric["nodes"]["direction"] == "up"
        assert len(by_metric["nodes"]["projected"]) == 3


class TestTrends:
    def test_not_enough_history(self, history: MetricHistory) -> None:
        history.append({"ts": 1.0, "nodes": 10})
        result = _trends(history)
        assert result["trends"] == []

    def test_trend_directions(self, history: MetricHistory) -> None:
        history.append({"ts": 1.0, "nodes": 10, "edges": 20, "score": 50})
        history.append({"ts": 2.0, "nodes": 20, "edges": 30, "score": 70})
        result = _trends(history)
        by_metric = {t["metric"]: t for t in result["trends"]}
        assert by_metric["nodes"]["direction"] == "increasing"
        assert by_metric["score"]["direction"] == "improving"
        assert by_metric["nodes"]["delta"] == 10


# ------------------------------------------------------------- reasoning
class TestInsightEngine:
    def test_insights_structure(self, graph: Any) -> None:
        from modules.architecture_intelligence.reasoning.insight_engine import InsightEngine

        findings = InsightEngine().run(graph)
        assert isinstance(findings, list)
        for finding in findings:
            assert {"id", "severity", "category", "title", "detail", "recommendation"} <= set(finding)

    def test_insights_limited(self, graph: Any) -> None:
        from modules.architecture_intelligence.reasoning.insight_engine import InsightEngine

        assert len(InsightEngine().run(graph, limit=1)) <= 1


# -------------------------------------------------------------- planning
class TestRoadmap:
    def test_roadmap_structure(self, graph: Any) -> None:
        from modules.architecture_intelligence.planning.roadmap import RoadmapGenerator

        result = RoadmapGenerator().generate(graph)
        assert set(result) >= {"summary", "effort", "tasks", "total_tasks", "sequence"}
        assert result["total_tasks"] == len(result["tasks"])
        assert all("id" in t and "effort" in t for t in result["tasks"])


# ------------------------------------------------------------ optimization
class TestOptimizer:
    def test_recommendations_structure(self, graph: Any) -> None:
        from modules.architecture_intelligence.optimization.recommendations import Optimizer

        result = Optimizer().recommend(graph)
        assert set(result) >= {"format", "total", "recommendations"}
        assert result["total"] == len(result["recommendations"])
        for rec in result["recommendations"]:
            assert {"priority", "category", "action", "impact"} <= set(rec)


# ------------------------------------------------------------- graph ai
class TestAssistant:
    def test_heuristic_answer(self, graph: Any) -> None:
        from modules.architecture_intelligence.graph_ai.assistant import GraphAssistant

        result = GraphAssistant().ask("how big is this project?", graph)
        assert result["generator"] == "heuristic"
        assert isinstance(result["answer"], str) and result["answer"]
        assert result["stats"]["nodes"] >= 4


class TestRAG:
    def test_index_and_search(self, graph: Any) -> None:
        from modules.architecture_intelligence.rag.intelligence_rag import IntelligenceRAG

        rag = IntelligenceRAG()
        assert rag.index_graph(graph) >= 4
        results = rag.search("app")
        assert results
        assert "score" in results[0]


# ------------------------------------------------------------ diagnostics
class TestHealth:
    def test_healthy_graph(self, graph: Any) -> None:
        from modules.architecture_intelligence.diagnostics.health import HealthChecker

        result = HealthChecker(StubEngine(graph)).run()
        assert result["status"] == "ok"
        assert {c["name"] for c in result["checks"]} == {"graph", "history"}

    def test_degraded_graph(self, graph: Any) -> None:
        from modules.architecture_intelligence.diagnostics.health import HealthChecker

        result = HealthChecker(StubEngine(graph, broken_graph=True)).run()
        assert result["status"] == "degraded"


# ---------------------------------------------------------------- agents
class TestAgents:
    def test_run_all(self, graph: Any) -> None:
        from modules.architecture_intelligence.agents.manager import AgentManager

        result = AgentManager(StubEngine(graph)).run_all()
        assert result["count"] >= 1
        assert result["errors"] == []
        assert "complexity" in result["agents"]


# -------------------------------------------------------------- workflows
class TestWorkflows:
    def test_run_known_workflow(self, graph: Any) -> None:
        from modules.architecture_intelligence.workflows.pipeline import WorkflowRunner

        result = WorkflowRunner(StubEngine(graph)).run("overview")
        assert result["ok"] is True
        assert "build" in result["steps"]
        assert "analyze" in result["steps"]

    def test_run_unknown_workflow(self, graph: Any) -> None:
        from modules.architecture_intelligence.workflows.pipeline import WorkflowRunner

        result = WorkflowRunner(StubEngine(graph)).run("nope")
        assert result["ok"] is False


# ---------------------------------------------------------------- events
class TestEventBus:
    def test_publish_subscribe_recent(self) -> None:
        from modules.architecture_intelligence.websocket.events import EventBus

        bus = EventBus()
        received: list[dict[str, Any]] = []
        bus.subscribe("intelligence.refresh", received.append)
        bus.publish("intelligence.refresh", {"ok": True})
        assert received and received[0]["payload"] == {"ok": True}
        assert bus.recent(1)[0]["event"] == "intelligence.refresh"
        bus.clear()
        assert bus.recent() == []


# -------------------------------------------------------------- scheduler
class TestScheduler:
    def test_periodic_runner(self) -> None:
        from modules.architecture_intelligence.scheduler.periodic import PeriodicRunner

        counter = {"n": 0}

        def tick() -> None:
            counter["n"] += 1

        runner = PeriodicRunner(0.05, tick)
        runner.start()
        time.sleep(0.25)
        runner.stop()
        assert counter["n"] >= 2


# ---------------------------------------------------------------- engine
class TestEngine:
    def test_snapshot_appends_history(self, graph: Any, history: MetricHistory) -> None:
        engine = _engine(graph, history)
        result = engine.snapshot()
        assert result["available"] is True
        assert result["appended"] is True
        assert history.count() == 1

    def test_analyze_returns_metrics_trends_forecast(self, graph: Any, history: MetricHistory) -> None:
        history.append({"ts": 1.0, "nodes": 10, "edges": 5, "score": 50})
        history.append({"ts": 2.0, "nodes": 12, "edges": 6, "score": 55})
        engine = _engine(graph, history)
        result = engine.analyze()
        assert result["available"] is True
        assert set(result) >= {"metrics", "trends", "forecast"}

    def test_insights_and_plan_available(self, graph: Any, history: MetricHistory) -> None:
        engine = _engine(graph, history)
        assert engine.insights()["available"] is True
        plan = engine.plan()
        assert plan["available"] is True and "tasks" in plan

    def test_optimize_and_agents_and_diagnose(self, graph: Any, history: MetricHistory) -> None:
        engine = _engine(graph, history)
        assert "recommendations" in engine.optimize()
        assert "agents" in engine.agents()
        assert engine.diagnose()["status"] in {"ok", "degraded"}

    def test_ask_heuristic(self, graph: Any, history: MetricHistory) -> None:
        engine = _engine(graph, history)
        result = engine.ask("what is here?")
        assert result["available"] is True
        assert result["generator"] == "heuristic"

    def test_report_aggregates(self, graph: Any, history: MetricHistory) -> None:
        engine = _engine(graph, history)
        result = engine.report()
        assert result["available"] is True
        assert set(result) >= {"metrics", "insights", "optimizations", "diagnostics", "history"}

    def test_engine_unavailable_degrades(
        self, history: MetricHistory, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import modules.architecture_graph.core.architecture_engine as ag_engine

        def _boom() -> Any:
            raise RuntimeError("graph module disabled")

        monkeypatch.setattr(ag_engine, "get_engine", _boom)
        engine = ArchitectureIntelligenceEngine(history=history)
        assert engine.available is False
        assert engine.graph() is None
        assert engine.insights()["available"] is False

    def test_nested_helper(self) -> None:
        assert _nested({"a": {"b": {"c": 1}}}, "a.b.c", None) == 1
        assert _nested({"a": 1}, "a.b", "default") == "default"


# ----------------------------------------------------------------- reports
class TestReport:
    def test_build_report(self, graph: Any, history: MetricHistory) -> None:
        from modules.architecture_intelligence.reports.intelligence_report import (
            IntelligenceReport,
        )

        report = IntelligenceReport(_engine(graph, history)).build()
        assert report["format"] == "json"
        assert report["available"] is True
        assert "generated_at" in report


# -------------------------------------------------------------------- api
class TestAPI:
    def test_router_routes(self) -> None:
        from modules.architecture_intelligence.api.router import router

        paths = {getattr(route, "path", "") for route in router.routes}
        for expected in [
            "/",
            "/metrics",
            "/insights",
            "/plan",
            "/forecast",
            "/trends",
            "/optimize",
            "/diagnose",
            "/agents",
            "/history",
            "/snapshot",
            "/ask",
            "/report",
        ]:
            assert expected in paths, f"missing route {expected}"

    def test_ask_requires_question(self) -> None:
        from modules.architecture_intelligence.api.intelligence_api import ask

        response = ask({"payload": 1})
        assert "Missing 'question'" in response["answer"]


# -------------------------------------------------------------------- cli
class TestCLI:
    def test_status_command(
        self, graph: Any, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
    ) -> None:
        import importlib

        cli_main = importlib.import_module("modules.architecture_intelligence.cli.main")
        monkeypatch.setattr(cli_main, "get_intelligence", lambda: StubEngine(graph))
        assert cli_main.main(["status"]) == 0
        payload = json.loads(capsys.readouterr().out)
        assert payload["module"] == "architecture_intelligence"

    def test_ask_requires_question(self, capsys: pytest.CaptureFixture) -> None:
        import importlib

        cli_main = importlib.import_module("modules.architecture_intelligence.cli.main")
        assert cli_main.main(["ask"]) == 1
        assert "error" in capsys.readouterr().out

    def test_no_command_prints_help(self, capsys: pytest.CaptureFixture) -> None:
        import importlib

        cli_main = importlib.import_module("modules.architecture_intelligence.cli.main")
        assert cli_main.main([]) == 0
        assert "usage" in capsys.readouterr().out.lower()
