from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .decision_models import Dashboard, DashboardType, Widget, ChartType
from .decision_config import DecisionConfig

logger = logging.getLogger(__name__)


class DashboardManager:
    def __init__(self, config: DecisionConfig):
        self._config = config
        self._dashboards: Dict[str, Dashboard] = {}
        self._widgets: Dict[str, Widget] = {}

    def create_dashboard(self, name: str, dashboard_type: DashboardType = DashboardType.OPERATIONAL, owner: str = "") -> Dashboard:
        dash = Dashboard(
            id=str(uuid.uuid4()),
            name=name,
            dashboard_type=dashboard_type,
            owner=owner,
        )
        self._dashboards[dash.id] = dash
        return dash

    def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        return self._dashboards.get(dashboard_id)

    def update_dashboard(self, dashboard_id: str, updates: Dict[str, Any]) -> Optional[Dashboard]:
        dash = self._dashboards.get(dashboard_id)
        if not dash:
            return None
        for key, value in updates.items():
            if hasattr(dash, key):
                setattr(dash, key, value)
        return dash

    def delete_dashboard(self, dashboard_id: str) -> bool:
        return bool(self._dashboards.pop(dashboard_id, None))

    def list_dashboards(self, dashboard_type: Optional[DashboardType] = None) -> List[Dashboard]:
        if dashboard_type:
            return [d for d in self._dashboards.values() if d.dashboard_type == dashboard_type]
        return list(self._dashboards.values())

    def add_widget(self, dashboard_id: str, title: str, chart_type: ChartType = ChartType.BAR, data_source: str = "") -> Optional[Widget]:
        dash = self._dashboards.get(dashboard_id)
        if not dash:
            return None
        widget = Widget(
            id=str(uuid.uuid4()),
            title=title,
            chart_type=chart_type,
            data_source=data_source,
        )
        self._widgets[widget.id] = widget
        dash.widgets.append({"widget_id": widget.id, "config": {}})
        return widget

    def remove_widget(self, dashboard_id: str, widget_id: str) -> bool:
        dash = self._dashboards.get(dashboard_id)
        if not dash:
            return False
        dash.widgets = [w for w in dash.widgets if w.get("widget_id") != widget_id]
        self._widgets.pop(widget_id, None)
        return True

    def get_widget(self, widget_id: str) -> Optional[Widget]:
        return self._widgets.get(widget_id)

    def get_executive_dashboard(self) -> Optional[Dashboard]:
        for d in self._dashboards.values():
            if d.dashboard_type == DashboardType.EXECUTIVE:
                return d
        return None

    def refresh_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        dash = self._dashboards.get(dashboard_id)
        if dash:
            dash.last_refreshed = datetime.utcnow()
        return dash

    def count_by_type(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for d in self._dashboards.values():
            counts[d.dashboard_type.value] = counts.get(d.dashboard_type.value, 0) + 1
        return counts
