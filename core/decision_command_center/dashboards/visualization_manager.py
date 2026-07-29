from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..decision_config import DecisionConfig
from ..decision_models import ChartType, DashboardType

logger = logging.getLogger(__name__)

CHART_TEMPLATES = {
    ChartType.LINE: {"type": "line", "options": {"xaxis": "time", "yaxis": "value", "smoothing": True}},
    ChartType.BAR: {"type": "bar", "options": {"orientation": "vertical", "stacked": False}},
    ChartType.PIE: {"type": "pie", "options": {"show_labels": True, "donut": False}},
    ChartType.AREA: {"type": "area", "options": {"stacked": True, "opacity": 0.7}},
    ChartType.GAUGE: {"type": "gauge", "options": {"min": 0, "max": 100, "thresholds": [40, 70]}},
    ChartType.HEATMAP: {"type": "heatmap", "options": {"color_scheme": "viridis"}},
    ChartType.FUNNEL: {"type": "funnel", "options": {"show_percent": True}},
    ChartType.TABLE: {"type": "table", "options": {"page_size": 20, "sortable": True}},
}


class VisualizationManager:
    def __init__(self, config: DecisionConfig):
        self._config = config

    def render(self, chart_type: ChartType, data: Dict[str, Any]) -> Dict[str, Any]:
        template = CHART_TEMPLATES.get(chart_type, CHART_TEMPLATES[ChartType.BAR])
        return {
            "chart_type": chart_type.value,
            "config": template["options"],
            "data": data,
            "layout": self._get_layout(chart_type),
        }

    def _get_layout(self, chart_type: ChartType) -> Dict[str, Any]:
        sizes = {
            ChartType.GAUGE: {"width": 1, "height": 1},
            ChartType.PIE: {"width": 2, "height": 2},
            ChartType.TABLE: {"width": 4, "height": 3},
            ChartType.HEATMAP: {"width": 3, "height": 2},
        }
        return sizes.get(chart_type, {"width": 2, "height": 2})

    def create_kpi_card(self, label: str, value: float, unit: str = "", trend: str = "stable") -> Dict[str, Any]:
        return {
            "type": "kpi_card",
            "label": label,
            "value": value,
            "unit": unit,
            "trend": trend,
            "config": {"show_sparkline": True, "color_by_trend": True},
        }

    def create_chart_config(self, data_source: str, chart_type: ChartType, title: str) -> Dict[str, Any]:
        return {
            "data_source": data_source,
            "chart_type": chart_type.value,
            "title": title,
            "config": CHART_TEMPLATES.get(chart_type, {}).get("options", {}),
        }
