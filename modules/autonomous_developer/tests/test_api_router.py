"""FastAPI router for the Autonomous Developer module.

Verifies the /api/v1/autonomous-developer endpoints (status, execute, reset,
sessions) against a stubbed runtime so tests never touch the real repo, plus
the concurrency guard on /execute.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from modules.autonomous_developer.api import router as ad_module
from modules.autonomous_developer.api.router import router as ad_router
from modules.autonomous_developer.config.developer_config import DeveloperConfig
from modules.autonomous_developer.core.registry import DeveloperRegistry
from modules.autonomous_developer.core.runtime import DeveloperRuntime
from modules.autonomous_developer.generator.generator import GenerationResult
from modules.autonomous_developer.planner.project_planner import ProjectPlanner


class StubGenerator:
    def run(self, ctx, goal: str, session_id: str | None = None, **kwargs):
        return GenerationResult(written=[])


def _stub_runtime(tmp_path: Path) -> DeveloperRuntime:
    registry = DeveloperRegistry()
    registry.register("planner", "default", ProjectPlanner())
    registry.register("generator", "default", StubGenerator())
    config = DeveloperConfig(
        project_root=str(tmp_path),
        run_tests=False,
        run_review=False,
        create_pr=False,
    )
    return DeveloperRuntime(config=config, registry=registry)


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    ad_router._runtime = _stub_runtime(tmp_path)
    app = FastAPI()
    app.include_router(ad_router)
    return TestClient(app)


class TestRouter:
    def test_status_ok(self, client: TestClient):
        resp = client.get("/status")
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        for key in ("state", "stats", "trace", "cost", "registry"):
            assert key in body["data"]

    def test_execute_requires_goal(self, client: TestClient):
        resp = client.post("/execute", json={})
        assert resp.status_code == 400

    def test_execute_requires_string_goal(self, client: TestClient):
        resp = client.post("/execute", json={"goal": 123})
        assert resp.status_code == 400

    def test_execute_ok(self, client: TestClient):
        resp = client.post(
            "/execute", json={"goal": "smoke", "phases": ["plan", "implement"]}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["session_id"]
        assert body["data"]["state"]["state"] in {"ready", "error"}

    def test_execute_conflict_when_busy(self, client: TestClient):
        acquired = ad_module._exec_lock.acquire(blocking=False)
        assert acquired
        try:
            resp = client.post("/execute", json={"goal": "smoke"})
            assert resp.status_code == 409
        finally:
            ad_module._exec_lock.release()

    def test_reset_ok(self, client: TestClient):
        resp = client.post("/reset")
        assert resp.status_code == 200
        assert resp.json() == {"success": True, "data": {"reset": True}}

    def test_sessions_ok(self, client: TestClient):
        resp = client.get("/sessions")
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert "active" in body["data"]
        assert "recent" in body["data"]
