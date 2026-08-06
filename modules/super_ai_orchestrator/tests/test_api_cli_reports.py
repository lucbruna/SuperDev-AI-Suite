"""Unit tests: api facade, cli, reports, frontend, websocket."""
from __future__ import annotations

import json

from modules.super_ai_orchestrator.api import OrchestratorAPI
from modules.super_ai_orchestrator.cli.cli import main
from modules.super_ai_orchestrator.core.status import TaskStatus
from modules.super_ai_orchestrator.events.event import TASK_SUBMITTED
from modules.super_ai_orchestrator.frontend.dashboard_payload import DashboardPayload
from modules.super_ai_orchestrator.reports.report_generator import OrchestratorReport
from modules.super_ai_orchestrator.websocket.event_hub import EventHub, WSEventMessage

from modules.super_ai_orchestrator.tests.helpers import make_api


# ---------------------------------------------------------------------- #
# Facade: end-to-end deterministic pipeline
# ---------------------------------------------------------------------- #
def test_facade_submit_decide_gate_execute_complete():
    api = make_api()
    task = api.submit(kind="develop", title="hello", payload={"scope": "x"})
    assert task["status"] == TaskStatus.QUEUED.value
    assert task["owner"] == "developer"
    assert task["llm"] == "claude"

    api.tick()
    data = api.get(task["seq"])
    assert data["status"] == TaskStatus.COMPLETED.value
    assert data["result"]["status"] == "delegated"
    assert data["result"]["plan"] == ["inspect", "implement", "verify", "scope"]


def test_facade_requires_approval_gate():
    api = make_api(governance=True)
    gated = api.submit(kind="develop", title="gated", require_approval=True)
    assert gated["status"] == TaskStatus.WAITING_APPROVAL.value

    approved = api.approve(gated["seq"])
    assert approved["status"] == TaskStatus.QUEUED.value

    other = api.submit(kind="develop", title="other", require_approval=True)
    rejected = api.reject(other["seq"], reason="not now")
    assert rejected["status"] == TaskStatus.REJECTED.value
    assert rejected["reason"] == "not now"


def test_facade_unknown_task_raises_key_error():
    api = make_api()
    try:
        api.get(999)
        raise AssertionError("expected KeyError")
    except KeyError:
        pass


def test_facade_tasks_filter_by_status():
    api = make_api()
    api.submit(kind="develop", title="a", require_approval=False)
    api.submit(kind="develop", title="b", require_approval=False)
    assert len(api.tasks()) == 2
    assert len(api.tasks(status="queued")) == 2
    try:
        api.tasks(status="bogus")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_facade_stats_health_metrics_analytics_audit_events():
    api = make_api()
    api.submit(kind="monitor", title="m", require_approval=False)
    api.tick()

    assert api.stats()["total"] == 1
    assert "status" in api.health()
    assert "completed" in api.metrics()
    assert "totals" in api.analytics_report()
    assert api.audit()
    assert any(e["type"] == TASK_SUBMITTED for e in api.events())


def test_facade_memory_roundtrip():
    api = make_api()
    api.memory_remember("ops", "last_tick", 12)
    assert api.memory_recall("ops", "last_tick") == 12
    assert api.memory_namespaces() == ["ops"]
    assert api.memory_keys("ops") == ["last_tick"]
    assert api.memory_forget("ops", "last_tick")["removed"] is True


def test_facade_integrations_and_invoke():
    api = make_api()
    data = api.integrations()
    assert "connectors" in data
    assert "available" in data
    unknown = api.invoke("nope")
    assert unknown["status"] == "unknown"


def test_facade_dashboard_is_json_safe():
    api = make_api()
    api.submit(kind="develop", title="dash", require_approval=False)
    payload = api.dashboard()
    # Sets/frozensets/tuples (governance policy, connectors) must serialize.
    assert isinstance(json.dumps(payload), str)
    assert "governance" in payload
    assert "connectors" in payload
    assert "recent_tasks" in payload
    assert "telemetry" in payload


# ---------------------------------------------------------------------- #
# CLI
# ---------------------------------------------------------------------- #
def test_cli_info_commands():
    for command in ("status", "health", "metrics", "analytics", "audit", "governance", "config", "dashboard", "integrations"):
        assert main([command]) == 0


def test_cli_task_lifecycle_commands():
    assert main(["submit", "monitor", "watch", "--require-approval"]) == 0
    assert main(["tasks"]) == 0
    assert main(["tick"]) == 0
    assert main(["memory-set", "ns", "k", "42"]) == 0
    assert main(["memory-get", "ns", "k"]) == 0
    assert main(["memory-namespaces"]) == 0
    assert main(["invoke", "nope"]) == 0


def test_cli_error_returns_nonzero():
    assert main(["task", "999"]) == 1


# ---------------------------------------------------------------------- #
# Reports
# ---------------------------------------------------------------------- #
def test_report_markdown_sections():
    api = make_api()
    api.submit(kind="develop", title="reported", require_approval=False)
    api.tick()
    text = OrchestratorReport(api).markdown()
    assert "# Super AI Orchestrator Report" in text
    assert "## Metrics" in text
    assert "## Analytics" in text
    assert "## Governance" in text
    assert "## Integrations" in text
    assert "## Recent audit" in text


def test_report_to_file_writes_utf8(tmp_path):
    api = make_api()
    path = OrchestratorReport(api).to_file(str(tmp_path / "report.md"))
    assert tmp_path / "report.md" in {tmp_path / "report.md"}
    assert "# Super AI Orchestrator Report" in (tmp_path / "report.md").read_text(encoding="utf-8")


# ---------------------------------------------------------------------- #
# Frontend dashboard payload
# ---------------------------------------------------------------------- #
def test_dashboard_payload_builder():
    api = make_api()
    payload = DashboardPayload(api).build()
    assert isinstance(json.dumps(payload), str)
    assert "health" in payload
    assert "analytics" in payload


# ---------------------------------------------------------------------- #
# WebSocket event hub
# ---------------------------------------------------------------------- #
def test_event_hub_fanout_and_unsubscribe():
    hub = EventHub()
    received: list[WSEventMessage] = []

    def handler(message: WSEventMessage) -> None:
        received.append(message)

    hub.subscribe("orchestrator", handler)
    hub.publish(WSEventMessage(channel="orchestrator", payload={"a": 1}))
    hub.publish(WSEventMessage(channel="other", payload={"b": 2}))
    assert len(received) == 1
    assert received[0].to_dict() == {"channel": "orchestrator", "payload": {"a": 1}}

    hub.unsubscribe("orchestrator", handler)
    hub.publish(WSEventMessage(channel="orchestrator", payload={"a": 3}))
    assert len(received) == 1
    assert hub.channels() == ["orchestrator"]


def test_event_hub_wired_to_event_bus():
    api = make_api()
    hub = EventHub()
    messages: list[dict] = []
    hub.subscribe("orchestrator", lambda message: messages.append(message.to_dict()))
    unsubscribe = hub.wire(api.event_bus)

    api.submit(kind="monitor", title="wired", require_approval=False)
    assert messages, "expected at least one translated event"
    assert messages[0]["channel"] == "orchestrator"
    assert "event" in messages[0]["payload"]
    # The pipeline publishes decision.made before task.submitted; both flow.
    types = [m["payload"]["event"]["type"] for m in messages]
    assert TASK_SUBMITTED in types

    unsubscribe()
    api.submit(kind="monitor", title="wired2", require_approval=False)
    before = len(messages)
    assert len(messages) == before
