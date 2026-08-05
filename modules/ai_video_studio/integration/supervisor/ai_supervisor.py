"""AI Supervisor — aggregates subsystem health into a supervision report."""
from __future__ import annotations

from typing import Any


class AISupervisor:
    """Collects health probes from studio subsystems."""

    def __init__(self) -> None:
        self._probes: dict[str, bool] = {}

    def set_probe(self, name: str, healthy: bool) -> None:
        self._probes[name] = bool(healthy)

    def report(self) -> dict[str, Any]:
        healthy = sum(1 for v in self._probes.values() if v)
        total = len(self._probes) or 1
        return {
            "probes": dict(self._probes),
            "healthy": healthy,
            "total": len(self._probes),
            "health_pct": round(healthy / total * 100, 1),
            "status": "ok" if healthy == len(self._probes) else "degraded",
        }


_ai_supervisor: AISupervisor | None = None


def get_ai_supervisor() -> AISupervisor:
    global _ai_supervisor
    if _ai_supervisor is None:
        _ai_supervisor = AISupervisor()
    return _ai_supervisor
