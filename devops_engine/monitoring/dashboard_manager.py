"""Dashboard management for monitoring (Volume 37, Fase 4)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from devops_engine.devops_protocols import new_id, now


@dataclass
class Dashboard:
    """A dashboard grouping metric series."""
    dashboard_id: str
    name: str
    metrics: list[str] = field(default_factory=list)
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class DashboardManager:
    """Creates and lists dashboards."""

    def __init__(self) -> None:
        self._dashboards: dict[str, Dashboard] = {}

    def create(self, name: str,
               metrics: list[str] | None = None) -> Dashboard:
        dashboard = Dashboard(
            dashboard_id=new_id("dashboard"),
            name=name,
            metrics=list(metrics or []),
            created_at=now(),
        )
        self._dashboards[dashboard.dashboard_id] = dashboard
        return dashboard

    def get(self, dashboard_id: str) -> Dashboard | None:
        return self._dashboards.get(dashboard_id)

    def list(self) -> list[Dashboard]:
        return list(self._dashboards.values())

    def count(self) -> int:
        return len(self._dashboards)
