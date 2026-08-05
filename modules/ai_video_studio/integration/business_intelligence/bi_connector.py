"""BI Connector — facade over the business-intelligence components."""
from __future__ import annotations


from modules.ai_video_studio.integration.business_intelligence.dashboard_renderer import (
    get_dashboard_renderer,
)
from modules.ai_video_studio.integration.business_intelligence.executive_reports import (
    get_executive_report_generator,
)
from modules.ai_video_studio.integration.business_intelligence.kpi_visualizer import (
    get_kpi_visualizer,
)
from modules.ai_video_studio.integration.business_intelligence.realtime_charts import (
    get_realtime_charts,
)
from modules.ai_video_studio.integration.connector_base import DomainConnector


class BIConnector(DomainConnector):
    """Renders dashboards, KPI visuals, executive reports and realtime charts."""

    domain = "business_intelligence"
    description = "Dashboard rendering, KPI visuals, executive reports and realtime charts"

    def __init__(self) -> None:
        super().__init__()
        self._register("render_dashboard", lambda d: get_dashboard_renderer().render(**d))
        self._register("visualize_kpi", lambda d: get_kpi_visualizer().visualize(**d))
        self._register("executive_report", lambda d: get_executive_report_generator().generate(**d))
        self._register("realtime_sample", lambda d: get_realtime_charts().sample(**d))


_bi_connector: BIConnector | None = None


def get_bi_connector() -> BIConnector:
    global _bi_connector
    if _bi_connector is None:
        _bi_connector = BIConnector()
    return _bi_connector
