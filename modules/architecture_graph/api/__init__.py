"""FastAPI layer for the Architecture Graph module.

Exposes the graph lifecycle (build/refresh/load), queries (nodes, edges,
search, impact), analysis (score, insights, plan) and exports/reports through
a REST API plus a WebSocket for real-time graph events. Auth degrades
gracefully when the platform auth module is unavailable.
"""
from __future__ import annotations

from modules.architecture_graph.api.router import api_router

__all__ = ["api_router"]
