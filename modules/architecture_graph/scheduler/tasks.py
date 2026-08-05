"""Background maintenance tasks for the Architecture Graph module.

Each task is a plain callable that can run inside the periodic runner, a
thread, or the FastAPI lifespan. Tasks publish lifecycle events on the module
event bus so WebSocket clients stay in sync.
"""
from __future__ import annotations

import logging
from typing import Any

from modules.architecture_graph.core.architecture_engine import get_engine
from modules.architecture_graph.websocket.events import publish

logger = logging.getLogger(__name__)


def rebuild_graph(*, persist: bool = True) -> dict[str, Any]:
    """Full rebuild. Publishes build.started / build.finished / build.error."""
    publish("graph.build.started", {"scope": "scheduled"})
    engine = get_engine()
    try:
        graph = engine.build(persist=persist)
    except Exception as exc:
        logger.exception("Scheduled build failed")
        publish("graph.build.error", {"error": str(exc)})
        return {"ok": False, "error": str(exc)}
    stats = graph.stats()
    publish("graph.build.finished", {"stats": stats, "last_build": engine.last_build})
    return {"ok": True, "stats": stats, "last_build": engine.last_build}


def refresh_graph() -> dict[str, Any]:
    """Incremental refresh. Publishes refresh events."""
    publish("graph.refresh.started", {"scope": "scheduled"})
    engine = get_engine()
    try:
        result = engine.refresh()
    except Exception as exc:
        logger.exception("Scheduled refresh failed")
        publish("graph.refresh.error", {"error": str(exc)})
        return {"ok": False, "error": str(exc)}
    publish("graph.refresh.finished", result)
    return {"ok": True, **result}


def run_all(*, persist: bool = True) -> dict[str, Any]:
    """Run every maintenance step in order (safe to call from a timer)."""
    result = refresh_graph()
    if not result.get("ok"):
        return result
    return rebuild_graph(persist=persist)


def schedule_refresh(interval_minutes: int = 30, *, persist: bool = True) -> dict[str, Any]:
    """Start (or re-arm) the periodic refresh runner. Idempotent per interval."""
    from modules.architecture_graph.scheduler.periodic import get_runner

    runner = get_runner()

    def job() -> dict[str, Any]:
        return run_all(persist=persist)

    runner.schedule("graph.refresh", job, interval_seconds=interval_minutes * 60)
    if not runner.running:
        runner.start()
    return {
        "ok": True,
        "interval_minutes": interval_minutes,
        "running": runner.running,
    }
