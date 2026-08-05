"""Main API router aggregating all Architecture Graph endpoint modules."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from modules.architecture_graph.api.deps import get_optional_user
from modules.architecture_graph.api.graph_api import router as graph_router
from modules.architecture_graph.api.graph_routes import router as analysis_router
from modules.architecture_graph.api.graph_websocket import router as websocket_router
from modules.architecture_graph.core.architecture_engine import get_engine

api_router = APIRouter()

# REST endpoints (no extra prefix: paths are self-descriptive).
api_router.include_router(graph_router)
api_router.include_router(analysis_router)
# Realtime WebSocket endpoint.
api_router.include_router(websocket_router)


@api_router.get("/health", tags=["Architecture Graph"])
async def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "architecture-graph", "version": "2.0.0"}


@api_router.get("/stats", tags=["Architecture Graph"])
async def graph_stats(user: dict[str, Any] = Depends(get_optional_user)) -> dict[str, Any]:
    """Aggregate stats over the current graph (frontend dashboard)."""
    engine = get_engine()
    graph = engine.load()
    if graph is None:
        return {"available": False, "nodes": 0, "edges": 0, "kinds": {}, "layers": {}}
    stats = graph.stats()
    return {
        "available": True,
        "nodes": stats.get("nodes", 0),
        "edges": stats.get("edges", 0),
        "kinds": stats.get("kinds", {}),
        "layers": stats.get("layers", {}),
        "last_build": engine.last_build,
    }
