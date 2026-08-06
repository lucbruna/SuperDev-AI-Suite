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

from modules.ai_evolution_engine.api.router import router  # noqa: E402

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
    assert "state" in body["data"]
    assert body["data"]["state"]["running"] is False


def test_analyze_and_recommend_cycle() -> None:
    analyze = client.post("/analyze")
    assert analyze.status_code == 200
    assert analyze.json()["success"] is True

    recommend = client.post(
        "/recommend",
        json={
            "kind": "performance",
            "title": "warm the cache",
            "impact_score": 0.8,
            "effort_score": 0.3,
            "risk_score": 0.2,
        },
    )
    assert recommend.status_code == 200
    body = recommend.json()
    assert body["success"] is True
    assert body["data"]["recommendation"]["title"] == "warm the cache"
    assert body["data"]["recommendation"]["status"] == "draft"


def test_recommend_requires_payload() -> None:
    response = client.post("/recommend", json={})
    assert response.status_code == 400


def test_approve_unknown_id_returns_404() -> None:
    response = client.post("/approve", json={"recommendation_id": "nope"})
    assert response.status_code == 404


def test_unknown_route_returns_404() -> None:
    assert client.get("/nope").status_code == 404


def test_integrations_summary() -> None:
    response = client.get("/integrations")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], dict)
    # Every sibling module connector is present in the default registry.
    assert "self_healing" in body["data"]
    assert "architecture_graph" in body["data"]


def test_dashboard_payload() -> None:
    response = client.get("/dashboard")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "engine" in body["data"]
    assert "integrations" in body["data"]
