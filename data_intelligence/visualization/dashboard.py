"""Dashboard assembly helpers."""

from __future__ import annotations

from typing import Any

from data_intelligence.data_models import DashboardSpec
from data_intelligence.visualization.base import (VisualizationError, Widget)
from data_intelligence.visualization.charts import CHART_BUILDERS


class DashboardBuilder:
    """Builds dashboard definitions for a given audience."""

    AUDIENCES = ("executive", "operations", "it")

    def __init__(self) -> None:
        self.dashboards: dict[str, DashboardSpec] = {}

    def create(self, dashboard_id: str, name: str,
               audience: str = "executive") -> DashboardSpec:
        if audience not in self.AUDIENCES:
            raise VisualizationError(f"unknown audience: {audience}")
        spec = DashboardSpec(dashboard_id=dashboard_id, name=name,
                             audience=audience)
        self.dashboards[dashboard_id] = spec
        return spec

    def add_widget(self, spec: DashboardSpec, widget_id: str,
                   widget_type: str, title: str,
                   **config: Any) -> Widget:
        widget = Widget(widget_id, widget_type, title, **config)
        spec.widgets.append(widget.to_dict())
        return widget

    def render(self, spec: DashboardSpec,
               data: dict[str, Any]) -> dict[str, Any]:
        """Builds every widget's chart payload from the data mapping."""
        if spec.dashboard_id not in self.dashboards:
            self.dashboards[spec.dashboard_id] = spec
        rendered: list[dict[str, Any]] = []
        for widget_cfg in spec.widgets:
            widget = Widget(widget_cfg["widget_id"],
                            widget_cfg["type"], widget_cfg["title"],
                            **widget_cfg.get("config", {}))
            builder = CHART_BUILDERS.get(widget.widget_type)
            if builder is None:
                raise VisualizationError(
                    f"unsupported widget type: {widget.widget_type}")
            chart = builder.build(widget, data.get(widget.widget_id))
            rendered.append(chart)
        return {"dashboard_id": spec.dashboard_id, "name": spec.name,
                "audience": spec.audience, "widgets": rendered}

    def stats(self) -> dict[str, Any]:
        return {"dashboards": list(self.dashboards),
                "audiences": sorted({s.audience
                                     for s in self.dashboards.values()})}
