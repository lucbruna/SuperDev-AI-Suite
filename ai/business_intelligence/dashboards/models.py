"""Dashboard models."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


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
    config: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, int] = field(default_factory=lambda: {"x": 0, "y": 0, "w": 6, "h": 4})
    refresh_interval: int = 60
    visible: bool = True


@dataclass
class Dashboard:
    dashboard_id: str
    name: str
    description: str = ""
    widgets: List[Widget] = field(default_factory=list)
    layout: Dict[str, Any] = field(default_factory=dict)
    theme: str = "light"
    refresh_mode: RefreshMode = RefreshMode.AUTO
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class DashboardFilter:
    filter_id: str
    name: str
    filter_type: str = "dropdown"
    options: List[str] = field(default_factory=list)
    default_value: Any = None
    applies_to: List[str] = field(default_factory=list)


@dataclass
class WidgetData:
    widget_id: str
    data: Any = None
    timestamp: Optional[datetime] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
