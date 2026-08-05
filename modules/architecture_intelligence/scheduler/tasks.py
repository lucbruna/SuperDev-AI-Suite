"""Scheduled intelligence tasks: refresh, analyze, snapshot."""
from __future__ import annotations

from typing import Any

from modules.architecture_intelligence.core.engine import get_intelligence
from modules.architecture_intelligence.websocket.events import get_bus


def refresh_graph() -> dict[str, Any]:
    engine = get_intelligence()
    graph = engine.graph(build_if_missing=True)
    get_bus().publish("intelligence.refresh", {"available": engine.available})
    return {"available": engine.available}


def run_analysis() -> dict[str, Any]:
    engine = get_intelligence()
    result = engine.analyze()
    get_bus().publish("intelligence.analyze", {"available": result.get("available", False)})
    return result


def snapshot() -> dict[str, Any]:
    result = get_intelligence().snapshot()
    get_bus().publish("intelligence.snapshot", {"appended": result.get("appended", False)})
    return result


def run_all() -> dict[str, Any]:
    return {
        "refresh": refresh_graph(),
        "analysis": run_analysis(),
        "snapshot": snapshot(),
    }
