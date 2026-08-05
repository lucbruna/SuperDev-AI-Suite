"""Agent manager: runs the built-in intelligence agents over the engine."""
from __future__ import annotations

from typing import Any

from modules.architecture_intelligence.agents.agents import AGENTS


class AgentManager:
    """Runs all registered agents and aggregates their reports."""

    def __init__(self, engine: Any) -> None:
        self.engine = engine

    def run_all(self) -> dict[str, Any]:
        graph = self.engine.graph(build_if_missing=True)
        results = {}
        errors: list[str] = []
        for name, fn in AGENTS.items():
            try:
                results[name] = fn(graph)
            except Exception as exc:  # pragma: no cover - defensive
                errors.append(f"{name}: {exc}")
        return {
            "agents": results,
            "count": len(results),
            "errors": errors,
            "generated_at": _now_iso(),
        }


def _now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()
