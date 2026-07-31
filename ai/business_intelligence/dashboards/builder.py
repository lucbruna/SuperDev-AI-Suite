"""Dashboard builder."""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from .models import Dashboard, DashboardFilter, RefreshMode, Widget
from .interfaces import DashboardBuilderInterface


class DashboardBuilder(DashboardBuilderInterface):
    def __init__(self):
        self._dashboards: Dict[str, Dashboard] = {}
        self._filters: Dict[str, List[DashboardFilter]] = {}

    async def create_dashboard(self, dashboard: Dashboard) -> Dashboard:
        self._dashboards[dashboard.dashboard_id] = dashboard
        return dashboard

    async def update_dashboard(self, dashboard_id: str, updates: Dict) -> Dashboard:
        d = self._dashboards.get(dashboard_id)
        if not d:
            raise KeyError(f"Dashboard {dashboard_id} not found")
        for k, v in updates.items():
            if hasattr(d, k):
                setattr(d, k, v)
        d.updated_at = datetime.now()
        return d

    async def delete_dashboard(self, dashboard_id: str) -> bool:
        return self._dashboards.pop(dashboard_id, None) is not None

    async def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        return self._dashboards.get(dashboard_id)

    async def list_dashboards(self, tags: Optional[List[str]] = None) -> List[Dashboard]:
        dashboards = list(self._dashboards.values())
        if tags:
            dashboards = [d for d in dashboards if any(t in d.tags for t in tags)]
        return dashboards

    async def add_widget(self, dashboard_id: str, widget: Widget) -> bool:
        d = self._dashboards.get(dashboard_id)
        if not d:
            return False
        d.widgets.append(widget)
        d.updated_at = datetime.now()
        return True

    async def remove_widget(self, dashboard_id: str, widget_id: str) -> bool:
        d = self._dashboards.get(dashboard_id)
        if not d:
            return False
        before = len(d.widgets)
        d.widgets = [w for w in d.widgets if w.widget_id != widget_id]
        return len(d.widgets) < before
