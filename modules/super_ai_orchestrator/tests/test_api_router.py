"""Integration tests for the FastAPI router (backend exposure).

Uses ``pytest.importorskip`` so the module test suite stays runnable in
environments without FastAPI installed (the core suite is stdlib-only).
"""
from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from modules.super_ai_orchestrator.api.router import router  # noqa: E402

# TestClient must wrap a full FastAPI app (not the bare router): modern
# FastAPI requires the middleware stack to be present in the request scope.
app = FastAPI()
app.include_router(router)

client = TestClient(app)


def test_status_ok() -> None:
    response = client.get("/status")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "health" in body["data"]
    assert "stats" in body["data"]


def test_config_and_governance() -> None:
    config = client.get("/config")
    assert config.status_code == 200
    assert "kernel" in config.json()["data"]

    governance = client.get("/governance")
    assert governance.status_code == 200
    assert "approval_kinds" in governance.json()["data"]


def test_submit_and_list_tasks() -> None:
    submitted = client.post(
        "/tasks",
        json={
            "kind": "monitor",
            "title": "route watch",
            "payload": {"scope": "api"},
            "require_approval": False,
        },
    )
    assert submitted.status_code == 200
    body = submitted.json()
    assert body["success"] is True
    seq = body["data"]["seq"]

    listed = client.get("/tasks")
    assert listed.status_code == 200
    assert any(t["seq"] == seq for t in listed.json()["data"])

    single = client.get(f"/tasks/{seq}")
    assert single.status_code == 200
    assert single.json()["data"]["title"] == "route watch"


def test_tick_and_completion() -> None:
    submitted = client.post(
        "/tasks",
        json={"kind": "monitor", "title": "tick me", "require_approval": False},
    )
    seq = submitted.json()["data"]["seq"]
    # The router uses a shared in-process instance, so earlier tasks may be
    # queued ahead of this one; tick enough slices to drain them all.
    tick = client.post("/tick", json={"slices": 20})
    assert tick.status_code == 200
    assert tick.json()["data"]["processed"] >= 1

    done = client.get(f"/tasks/{seq}")
    assert done.json()["data"]["status"] == "completed"


def test_approval_gate_flow() -> None:
    submitted = client.post(
        "/tasks",
        json={"kind": "develop", "title": "gated", "require_approval": True},
    )
    seq = submitted.json()["data"]["seq"]
    assert submitted.json()["data"]["status"] == "waiting_approval"

    approved = client.post(f"/tasks/{seq}/approve")
    assert approved.status_code == 200
    assert approved.json()["data"]["status"] == "queued"


def test_reject_and_unknown_task_404() -> None:
    submitted = client.post(
        "/tasks",
        json={"kind": "develop", "title": "reject me", "require_approval": True},
    )
    seq = submitted.json()["data"]["seq"]
    rejected = client.post(f"/tasks/{seq}/reject", json={"reason": "no"})
    assert rejected.status_code == 200
    assert rejected.json()["data"]["status"] == "rejected"

    missing = client.post("/tasks/999999/approve")
    assert missing.status_code == 404


def test_memory_endpoints() -> None:
    created = client.post("/memory", json={"namespace": "api", "key": "k", "value": 7})
    assert created.status_code == 200

    recalled = client.get("/memory/api/k")
    assert recalled.status_code == 200
    assert recalled.json()["data"]["value"] == 7

    namespaces = client.get("/memory")
    assert "api" in namespaces.json()["data"]["namespaces"]

    keys = client.get("/memory/api")
    assert keys.json()["data"]["keys"] == ["k"]

    deleted = client.delete("/memory/api/k")
    assert deleted.json()["data"]["removed"] is True


def test_integrations_endpoints() -> None:
    integrations = client.get("/integrations")
    assert integrations.status_code == 200
    body = integrations.json()["data"]
    assert "connectors" in body
    assert "available" in body

    invoke = client.post("/integrations/nope/invoke", json={})
    assert invoke.status_code == 200
    assert invoke.json()["data"]["status"] == "unknown"


def test_dashboard_and_analytics() -> None:
    dashboard = client.get("/dashboard")
    assert dashboard.status_code == 200
    assert "analytics" in dashboard.json()["data"]
    assert "connectors" in dashboard.json()["data"]

    analytics = client.get("/analytics")
    assert analytics.status_code == 200
    assert "totals" in analytics.json()["data"]

    audit = client.get("/audit")
    assert audit.status_code == 200
    assert isinstance(audit.json()["data"], list)

    events = client.get("/events")
    assert events.status_code == 200
    assert isinstance(events.json()["data"], list)


def test_unknown_route_returns_404() -> None:
    assert client.get("/nope").status_code == 404
