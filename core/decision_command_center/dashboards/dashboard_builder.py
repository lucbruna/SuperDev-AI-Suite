from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..decision_config import DecisionConfig
from ..decision_models import Dashboard, DashboardType, Widget, ChartType

logger = logging.getLogger(__name__)


class DashboardBuilder:
    def __init__(self, config: DecisionConfig):
        self._config = config
        self._dashboards: Dict[str, Dashboard] = {}

    def create(self, name: str, dashboard_type: DashboardType = DashboardType.OPERATIONAL, owner: str = "") -> Dashboard:
        dash = Dashboard(
            id=str(uuid.uuid4()),
            name=name,
            dashboard_type=dashboard_type,
            owner=owner,
        )
        self._dashboards[dash.id] = dash
        return dash

    def get(self, dashboard_id: str) -> Optional[Dashboard]:
        return self._dashboards.get(dashboard_id)

    def update(self, dashboard_id: str, updates: Dict[str, Any]) -> Optional[Dashboard]:
        dash = self._dashboards.get(dashboard_id)
        if not dash:
            return None
        for key, value in updates.items():
            if hasattr(dash, key):
                setattr(dash, key, value)
        return dash

    def delete(self, dashboard_id: str) -> bool:
        return bool(self._dashboards.pop(dashboard_id, None))

    def list_dashboards(self, dashboard_type: Optional[DashboardType] = None) -> List[Dashboard]:
        if dashboard_type:
            return [d for d in self._dashboards.values() if d.dashboard_type == dashboard_type]
        return list(self._dashboards.values())

    def add_widget(self, dashboard_id: str, title: str, chart_type: ChartType = ChartType.BAR) -> Optional[Widget]:
        dash = self._dashboards.get(dashboard_id)
        if not dash:
            return None
        widget = Widget(id=str(uuid.uuid4()), title=title, chart_type=chart_type)
        dash.widgets.append({"widget_id": widget.id, "title": title})
        return widget

    def refresh(self, dashboard_id: str) -> Optional[Dashboard]:
        dash = self._dashboards.get(dashboard_id)
        if dash:
            dash.last_refreshed = datetime.utcnow()
        return dash

    def count(self) -> int:
        return len(self._dashboards)
