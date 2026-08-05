"""Health diagnostics for the architecture and the intelligence pipeline."""
from __future__ import annotations

from typing import Any


class HealthChecker:
    """Runs a set of checks and returns a health report dict."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine

    def run(self) -> dict[str, Any]:
        checks: list[dict[str, Any]] = [self._graph_check()]
        try:
            checks.append(self._history_check())
        except Exception as exc:  # pragma: no cover - defensive
            checks.append({"name": "history", "ok": False, "detail": str(exc)})
        ok = all(c.get("ok") for c in checks)
        return {
            "status": "ok" if ok else "degraded",
            "checks": checks,
            "checked_at": _now_iso(),
        }

    def _graph_check(self) -> dict[str, Any]:
        try:
            graph = self.engine.graph(build_if_missing=True)
            stats = graph.stats()
            ok = stats.get("nodes", 0) > 0
            return {
                "name": "graph",
                "ok": ok,
                "detail": {
                    "nodes": stats.get("nodes", 0),
                    "edges": stats.get("edges", 0),
                    "packages": stats.get("packages", 0),
                },
            }
        except Exception as exc:
            return {"name": "graph", "ok": False, "detail": str(exc)}

    def _history_check(self) -> dict[str, Any]:
        history = self.engine.history_recent(limit=1)
        return {"name": "history", "ok": True, "detail": {"samples": len(history)}}


def _now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()
