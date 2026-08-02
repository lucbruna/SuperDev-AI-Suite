"""Health monitor — snapshots health of registered services and the integration core."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from modules.ai_video_studio.integration.dependency_manager import get_dependency_manager
from modules.ai_video_studio.integration.module_registry import get_registry


@dataclass
class ServiceHealth:
    name: str
    healthy: bool
    registered: bool
    deps_satisfied: bool
    ping_ok: bool | None = None
    last_check: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    error: str | None = None


class HealthMonitor:
    """Per-service liveness/readiness based on registration + dependency graph.

    ``ping`` is called when the service instance exposes a zero-arg ``ping``
    method; otherwise presence + satisfied dependencies determine health.
    """

    def __init__(self, registry=None) -> None:  # type: ignore[no-untyped-def]
        self._registry = registry or get_registry()
        self._results: dict[str, ServiceHealth] = {}

    def check(self, name: str) -> dict[str, Any]:
        service = self._registry.get(name)
        registered = service is not None
        deps_ok = self._dependency_manager().is_satisfied(name) if registered else False
        ping_ok: bool | None = None
        error: str | None = None
        if registered and hasattr(service, "ping") and callable(service.ping):
            try:
                service.ping()
                ping_ok = True
            except Exception as e:  # noqa: BLE001 — health must not raise
                ping_ok = False
                error = str(e)
        health = ServiceHealth(
            name=name,
            healthy=registered and deps_ok and (ping_ok is not False),
            registered=registered,
            deps_satisfied=deps_ok,
            ping_ok=ping_ok,
            error=error,
        )
        self._results[name] = health
        return self._to_dict(health)

    def check_all(self) -> dict[str, Any]:
        names = [s["name"] for s in self._registry.list_services()]
        services = [self.check(n) for n in names]
        return {
            "healthy": all(s["healthy"] for s in services),
            "checked_at": datetime.now(UTC).isoformat(),
            "service_count": len(services),
            "services": services,
        }

    def _dependency_manager(self):
        return get_dependency_manager()

    @staticmethod
    def _to_dict(h: ServiceHealth) -> dict[str, Any]:
        return {
            "name": h.name,
            "healthy": h.healthy,
            "registered": h.registered,
            "deps_satisfied": h.deps_satisfied,
            "ping_ok": h.ping_ok,
            "last_check": h.last_check,
            "error": h.error,
        }


_health_monitor: HealthMonitor | None = None


def get_health_monitor() -> HealthMonitor:
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    return _health_monitor
