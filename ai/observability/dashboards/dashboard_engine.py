"""Dashboard engine."""
from __future__ import annotations
from typing import Any, Dict, List, Optional
import time

class DashboardEngine:
    def __init__(self) -> None:
        self._dashboards: Dict[str, Dict[str, Any]] = {}
        self._started = False
    def start(self) -> None:
        self._started = True
    def stop(self) -> None:
        self._started = False
    def create_dashboard(self, name: str, layout: str = "grid") -> Dict[str, Any]:
        dashboard = {"name": name, "layout": layout, "panels": [], "created_at": time.time()}
        self._dashboards[name] = dashboard
        return dashboard
    def get_dashboard(self, name: str) -> Optional[Dict[str, Any]]:
        return self._dashboards.get(name)
    def list_dashboards(self) -> List[Dict[str, Any]]:
        return [{"name": d["name"], "panels": len(d["panels"])} for d in self._dashboards.values()]
    def delete_dashboard(self, name: str) -> bool:
        if name in self._dashboards:
            del self._dashboards[name]
            return True
        return False
    def add_panel(self, dashboard_name: str, panel: Dict[str, Any]) -> bool:
        d = self._dashboards.get(dashboard_name)
        if d:
            d["panels"].append(panel)
            return True
        return False
    def get_status(self) -> Dict[str, Any]:
        return {"running": self._started, "dashboards": len(self._dashboards)}
