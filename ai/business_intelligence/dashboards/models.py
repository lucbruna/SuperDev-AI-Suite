"""Dashboard models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class WidgetType(Enum):
    CHART = "chart"
    TABLE = "table"
    KPI = "kpi"
    FILTER = "filter"
    TEXT = "text"
    MAP = "map"


class ChartType(Enum):
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    HEATMAP = "heatmap"
    AREA = "area"
    FUNNEL = "funnel"


class RefreshMode(Enum):
    AUTO = "auto"
    MANUAL = "manual"
    PUSH = "push"


@dataclass
class Widget:
    widget_id: str
    widget_type: WidgetType
    title: str
    data_source: str = ""
    config: dict[str, Any] = field(default_factory=dict)
    position: dict[str, int] = field(default_factory=lambda: {"x": 0, "y": 0, "w": 6, "h": 4})
    refresh_interval: int = 60
    visible: bool = True


@dataclass
class Dashboard:
    dashboard_id: str
    name: str
    description: str = ""
    widgets: list[Widget] = field(default_factory=list)
    layout: dict[str, Any] = field(default_factory=dict)
    theme: str = "light"
    refresh_mode: RefreshMode = RefreshMode.AUTO
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class DashboardFilter:
    filter_id: str
    name: str
    filter_type: str = "dropdown"
    options: list[str] = field(default_factory=list)
    default_value: Any = None
    applies_to: list[str] = field(default_factory=list)


@dataclass
class WidgetData:
    widget_id: str
    data: Any = None
    timestamp: datetime | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
