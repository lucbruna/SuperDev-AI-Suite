"""Dashboard payload builder: serializes orchestrator state for the frontend."""
from __future__ import annotations

from typing import Any

from modules.super_ai_orchestrator.api import OrchestratorAPI


class DashboardPayload:
    """Builds a JSON-serializable dashboard payload.

    The facade's ``dashboard()`` already aggregates health, metrics,
    stats, analytics, governance, connectors, telemetry, memory,
    recent tasks and recent events; this builder only guarantees the
    result is safe to serialize (set/tuple/frozenset → sorted list).
    """

    def __init__(self, api: OrchestratorAPI) -> None:
        self._api = api

    def build(self) -> dict[str, Any]:
        return self._json_safe(self._api.dashboard())

    @staticmethod
    def _json_safe(value: Any) -> Any:
        if isinstance(value, dict):
            return {str(k): DashboardPayload._json_safe(v) for k, v in value.items()}
        if isinstance(value, (set, frozenset, tuple)):
            try:
                return [DashboardPayload._json_safe(v) for v in sorted(value)]
            except TypeError:  # mixed-type collection: keep insertion order
                return [DashboardPayload._json_safe(v) for v in value]
        if isinstance(value, list):
            return [DashboardPayload._json_safe(v) for v in value]
        return value
