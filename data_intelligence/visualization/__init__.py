"""Visualization subsystem (Volume 22).

Dashboards tailored to each audience (Diretoria / Operação / TI) built
from bar, line, pie, KPI and table widgets. Prebuilt dashboard specs are
available through ``default_dashboard(audience)``.
"""

from __future__ import annotations

from data_intelligence.visualization.base import (VisualizationError, Widget)
from data_intelligence.visualization.charts import (BarChartBuilder,
                                                    CHART_BUILDERS,
                                                    KpiCardBuilder,
                                                    LineChartBuilder,
                                                    PieChartBuilder,
                                                    TableBuilder)
from data_intelligence.visualization.dashboard import DashboardBuilder
from data_intelligence.visualization.dashboard_specs import (
    PREBUILT_DASHBOARDS, default_dashboard, get_dashboard)
from data_intelligence.visualization.engine import VisualizationEngine

__all__ = [
    "VisualizationEngine", "DashboardBuilder", "Widget",
    "VisualizationError", "CHART_BUILDERS", "BarChartBuilder",
    "LineChartBuilder", "PieChartBuilder", "KpiCardBuilder",
    "TableBuilder", "PREBUILT_DASHBOARDS", "default_dashboard",
    "get_dashboard",
]
