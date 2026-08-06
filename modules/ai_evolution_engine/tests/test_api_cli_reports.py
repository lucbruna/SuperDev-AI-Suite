"""Unit tests: api, cli, reports, frontend packages."""
from __future__ import annotations

from modules.ai_evolution_engine.api.evolution_api import EvolutionAPI
from modules.ai_evolution_engine.core.evolution_manager import EvolutionManager
from modules.ai_evolution_engine.frontend.dashboard_payload import DashboardPayload
from modules.ai_evolution_engine.reports.report_generator import (
    ReportGenerator,
    ReportSection,
)
from modules.ai_evolution_engine.tests.helpers import make_recommendation


def _make_api() -> EvolutionAPI:
    manager = EvolutionManager()
    return EvolutionAPI(manager)


def test_api_status_action():
    api = _make_api()
    result = api.handle("status")
    assert result["ok"] is True
    assert result["state"]["running"] is False


def test_api_analyze_action():
    api = _make_api()
    result = api.handle("analyze")
    assert result["ok"] is True
    assert "analysis" in result


def test_api_unknown_action_returns_error():
    api = _make_api()
    result = api.handle("nope")
    assert result["ok"] is False


def test_api_approve_reject_cycle():
    api = _make_api()
    manager = api._manager
    item = make_recommendation()
    manager.recommend(item)
    manager.submit_for_approval(item)

    approved = api.handle("approve", {"recommendation_id": item.title})
    assert approved["ok"] is True
    assert item.status == "approved"

    other = make_recommendation(title="other")
    manager.recommend(other)
    manager.submit_for_approval(other)
    rejected = api.handle("reject", {"recommendation_id": other.title})
    assert rejected["ok"] is True
    assert other.status == "rejected"


def test_cli_main_commands():
    from modules.ai_evolution_engine.cli.cli import main

    assert main(["status"]) == 0
    assert main(["analyze"]) == 0
    assert main(["integrations"]) == 0


def test_report_generator_markdown():
    generator = ReportGenerator()
    text = generator.render(
        "Report",
        [ReportSection(title="Section", lines=["one", "two"])],
    )
    assert "# Report" in text
    assert "## Section" in text
    assert "- one" in text
    assert "- two" in text


def test_report_payload_render():
    generator = ReportGenerator()
    text = generator.render_payload("Summary", {"health": {"score": 0.9}})
    assert "## health" in text


def test_dashboard_payload_build():
    manager = EvolutionManager()
    payload = DashboardPayload(manager).build()
    assert "engine" in payload
    assert "integrations" in payload
    assert payload["integrations"]["self_healing"] is True
