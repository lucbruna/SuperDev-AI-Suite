"""Observability adapter — report suite MonitoringEngine health, record locally.

Bridges to ``SuperDev.monitoring``: adapter ``health()`` reflects the suite
engine (metrics/logs/tracing/alerts flags). Studio metric recording always
lands in a local counter so the studio is observable even before the suite
engine is wired.
"""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.suite_integration.adapters.base import (
    SuiteAdapter,
    ensure_suite_importable,
    import_optional,
)


class ObservabilityAdapter(SuiteAdapter):
    """Metrics recording (local) + suite MonitoringEngine health."""

    name = "observability"
    description = "Forward studio metrics to the suite MonitoringEngine (local counters fallback)"
    platform_module = "SuperDev.monitoring"
    actions = ("record", "health")

    def __init__(self) -> None:
        super().__init__()
        self._counters: dict[str, int] = {}

    def record(self, metric: str, value: int = 1, **labels: Any) -> dict[str, Any]:
        """Increment a labeled counter (local, always available)."""
        key = f"{metric}:{tuple(sorted(labels.items()))}" if labels else metric
        self._counters[key] = self._counters.get(key, 0) + int(value)
        return {"recorded": key, "total": self._counters[key], "platform": self.available()}

    def snapshot(self) -> dict[str, Any]:
        """Local counter snapshot (independent of the suite engine)."""
        return {"counters": dict(self._counters), "count": len(self._counters)}

    async def health(self) -> dict[str, Any]:
        """Suite MonitoringEngine health when importable, else local status."""
        ensure_suite_importable()
        mon = import_optional("SuperDev.monitoring")
        if mon is None:
            return {"running": False, "metrics_count": len(self._counters), "platform": False}
        try:
            engine = mon.MonitoringEngine()
            health = await engine.health()
            health["platform"] = True
            health["studio_counters"] = len(self._counters)
            return health
        except Exception as e:  # noqa: BLE001 — health must not raise
            self._error = f"health failed: {e}"
            return {
                "running": False,
                "metrics_count": len(self._counters),
                "error": self._error,
                "platform": True,
            }
