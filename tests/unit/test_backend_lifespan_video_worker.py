"""Lifecycle integration tests for the main backend application."""

import pytest
from contextlib import asynccontextmanager


@pytest.mark.asyncio(loop_scope="function")
async def test_main_backend_lifespan_starts_and_stops_darkstudio_worker(monkeypatch):
    import backend.lifespan as backend_lifespan
    from modules.ai_video_studio.api.routes import video

    calls = []
    async def startup():
        calls.append("backend_startup")

    async def shutdown():
        calls.append("backend_shutdown")

    monkeypatch.setattr(backend_lifespan, "startup_handler", startup)
    monkeypatch.setattr(backend_lifespan, "shutdown_handler", shutdown)
    monkeypatch.setattr(backend_lifespan, "setup_logging", lambda _config: __import__("logging").getLogger("test"))
    monkeypatch.setattr(backend_lifespan, "get_environment", lambda: __import__("backend.environment", fromlist=["Environment"]).Environment.DEV)
    monkeypatch.setattr(backend_lifespan, "register_signal_handlers", lambda **_kwargs: None)
    monkeypatch.setattr(video, "start_dependency_rebuild_worker", lambda: calls.append("worker_start"))

    async def stop_worker():
        calls.append("worker_stop")

    monkeypatch.setattr(video, "stop_dependency_rebuild_worker", stop_worker)

    async with asynccontextmanager(backend_lifespan.lifespan)(None):
        assert calls == ["backend_startup", "worker_start"]

    assert calls == ["backend_startup", "worker_start", "worker_stop", "backend_shutdown"]
