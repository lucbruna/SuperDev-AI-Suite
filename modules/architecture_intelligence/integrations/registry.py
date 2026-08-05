"""Integrations registry: external tool adapters (VCS, CI, telemetry).

Adapters are optional; the registry reports availability and exposes a common
run/check interface so integrations never break core intelligence.
"""
from __future__ import annotations

import threading
from typing import Any, Callable

Integration = Callable[[], dict[str, Any]]


class IntegrationRegistry:
    def __init__(self) -> None:
        self._integrations: dict[str, Integration] = {}
        self._lock = threading.Lock()

    def register(self, name: str, integration: Integration) -> None:
        with self._lock:
            self._integrations[name] = integration

    def names(self) -> list[str]:
        with self._lock:
            return sorted(self._integrations)

    def status(self) -> list[dict[str, Any]]:
        results = []
        for name in self.names():
            try:
                result = self._integrations[name]()
                results.append({"name": name, "ok": True, "detail": result})
            except Exception as exc:  # pragma: no cover - defensive
                results.append({"name": name, "ok": False, "detail": str(exc)})
        return results


_registry: IntegrationRegistry | None = None
_registry_lock = threading.Lock()


def get_integration_registry() -> IntegrationRegistry:
    global _registry
    if _registry is None:
        with _registry_lock:
            if _registry is None:
                _registry = IntegrationRegistry()
    return _registry
