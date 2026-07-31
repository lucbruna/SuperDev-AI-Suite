"""Visualization engine (attached by the facade as ``visualization``)."""

from __future__ import annotations

from typing import Any

from data_intelligence.data_events import (DataIntelligenceEventType,
                                           DataIntelligenceEvents)
from data_intelligence.data_logger import get_logger
from data_intelligence.data_metrics import DataIntelligenceMetrics
from data_intelligence.data_models import DashboardSpec
from data_intelligence.visualization.base import (VisualizationError, Widget)
from data_intelligence.visualization.charts import CHART_BUILDERS
from data_intelligence.visualization.dashboard import DashboardBuilder
from data_intelligence.visualization.dashboard_specs import (
    PREBUILT_DASHBOARDS, default_dashboard as default_dashboard_spec)


class VisualizationEngine:
    """Coordinates dashboards per audience and chart building."""

    def __init__(self, events: DataIntelligenceEvents,
                 metrics: DataIntelligenceMetrics, config: Any,
                 context: Any) -> None:
        self._log = get_logger()
        self.events = events
        self.metrics = metrics
        self.config = config
        self.context = context
        self.builder = DashboardBuilder()
        for dashboard_id, spec in PREBUILT_DASHBOARDS.items():
            self.builder.dashboards[dashboard_id] = spec

    def default_dashboard(self, audience: str) -> DashboardSpec:
        return default_dashboard_spec(audience)

    def create_dashboard(self, dashboard_id: str, name: str,
                         audience: str = "executive") -> DashboardSpec:
        spec = self.builder.create(dashboard_id, name, audience)
        self._log.info("created dashboard %s for %s", dashboard_id, audience)
        return spec

    def add_widget(self, spec: DashboardSpec, widget_id: str,
                   widget_type: str, title: str, **config: Any) -> Widget:
        return self.builder.add_widget(spec, widget_id, widget_type,
                                       title, **config)

    def render(self, dashboard_id: str,
               data: dict[str, Any]) -> dict[str, Any]:
        """Renders a dashboard by id with the given widget data."""
        spec = self.builder.dashboards.get(dashboard_id)
        if spec is None:
            raise VisualizationError(f"unknown dashboard: {dashboard_id}")
        rendered = self.builder.render(spec, data)
        self.metrics.increment("visualization.renders")
        self.events.publish(DataIntelligenceEventType.DASHBOARD_UPDATED,
                            {"dashboard_id": dashboard_id})
        return rendered

    def build_chart(self, widget_type: str, title: str,
                    data: Any, **config: Any) -> dict[str, Any]:
        builder = CHART_BUILDERS.get(widget_type)
        if builder is None:
            raise VisualizationError(f"unsupported widget type: {widget_type}")
        widget = Widget(f"tmp-{widget_type}", widget_type, title, **config)
        return builder.build(widget, data)

    def stats(self) -> dict[str, Any]:
        return self.builder.stats()
