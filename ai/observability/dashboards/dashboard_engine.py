"""Dashboard engine."""
from __future__ import annotations

import time
from typing import Any


class DashboardEngine:
    def __init__(self) -> None:
        self._dashboards: dict[str, dict[str, Any]] = {}
        self._started = False
    def start(self) -> None:
        self._started = True
    def stop(self) -> None:
        self._started = False
    def create_dashboard(self, name: str, layout: str = "grid") -> dict[str, Any]:
        dashboard = {"name": name, "layout": layout, "panels": [], "created_at": time.time()}
        self._dashboards[name] = dashboard
        return dashboard
    def get_dashboard(self, name: str) -> dict[str, Any] | None:
        return self._dashboards.get(name)
    def list_dashboards(self) -> list[dict[str, Any]]:
        return [{"name": d["name"], "panels": len(d["panels"])} for d in self._dashboards.values()]
    def delete_dashboard(self, name: str) -> bool:
        if name in self._dashboards:
            del self._dashboards[name]
            return True
        return False
    def add_panel(self, dashboard_name: str, panel: dict[str, Any]) -> bool:
        d = self._dashboards.get(dashboard_name)
        if d:
            d["panels"].append(panel)
            return True
        return False
    def get_status(self) -> dict[str, Any]:
        return {"running": self._started, "dashboards": len(self._dashboards)}
