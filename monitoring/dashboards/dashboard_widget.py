from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Literal

WidgetType = Literal[
    "chart", "stat", "table", "heatmap", "log",
    "gauge", "progress", "list", "text", "image",
]


@dataclass
class WidgetDefinition:
    widget_type: WidgetType = "stat"
    title: str = ""
    metric: str = ""
    aggregation: str = "last"  # last, sum, avg, min, max, count
    unit: str = ""
    thresholds: dict[str, float] = field(default_factory=lambda: {"warn": 0.7, "critical": 0.9})
    config: dict[str, Any] = field(default_factory=dict)


class WidgetFactory:
    """Creates widget definitions for dashboards."""

    @staticmethod
    def stat(title: str, metric: str, unit: str = "", **kwargs: Any) -> WidgetDefinition:
        return WidgetDefinition(
            widget_type="stat", title=title, metric=metric, unit=unit, **kwargs
        )

    @staticmethod
    def chart(title: str, metric: str, **kwargs: Any) -> WidgetDefinition:
        return WidgetDefinition(
            widget_type="chart", title=title, metric=metric, **kwargs
        )

    @staticmethod
    def table(title: str, metric: str, **kwargs: Any) -> WidgetDefinition:
        return WidgetDefinition(
            widget_type="table", title=title, metric=metric, **kwargs
        )

    @staticmethod
    def heatmap(title: str, metric: str, **kwargs: Any) -> WidgetDefinition:
        return WidgetDefinition(
            widget_type="heatmap", title=title, metric=metric, **kwargs
        )

    @staticmethod
    def log(title: str, metric: str = "", **kwargs: Any) -> WidgetDefinition:
        return WidgetDefinition(
            widget_type="log", title=title, metric=metric, **kwargs
        )

    @staticmethod
    def gauge(title: str, metric: str, **kwargs: Any) -> WidgetDefinition:
        return WidgetDefinition(
            widget_type="gauge", title=title, metric=metric, **kwargs
        )
