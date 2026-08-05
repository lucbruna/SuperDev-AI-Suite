"""Business Intelligence — dashboard rendering, KPI visuals, executive reports and realtime charts."""
from modules.ai_video_studio.integration.business_intelligence.bi_connector import (
    BIConnector,
    get_bi_connector,
)
from modules.ai_video_studio.integration.business_intelligence.dashboard_renderer import (
    DashboardRenderer,
    get_dashboard_renderer,
)
from modules.ai_video_studio.integration.business_intelligence.kpi_visualizer import (
    KPIVisualizer,
    get_kpi_visualizer,
)

__all__ = [
    "BIConnector",
    "get_bi_connector",
    "DashboardRenderer",
    "get_dashboard_renderer",
    "KPIVisualizer",
    "get_kpi_visualizer",
]
