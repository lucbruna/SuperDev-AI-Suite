from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..decision_config import DecisionConfig
from ..decision_models import Dashboard, DashboardType, Widget, ChartType
from ..decision_security import DecisionSecurityManager
from .dashboard_builder import DashboardBuilder
from .visualization_manager import VisualizationManager
from .realtime_dashboard import RealtimeDashboard
from .executive_dashboard import ExecutiveDashboard

logger = logging.getLogger(__name__)


class DashboardEngine:
    def __init__(self, config: DecisionConfig, security: DecisionSecurityManager):
        self.config = config
        self.security = security
        self.builder: Optional[DashboardBuilder] = None
        self.visualization: Optional[VisualizationManager] = None
        self.realtime: Optional[RealtimeDashboard] = None
        self.executive: Optional[ExecutiveDashboard] = None

    async def initialize(self) -> None:
        self.builder = DashboardBuilder(self.config)
        self.visualization = VisualizationManager(self.config)
        self.realtime = RealtimeDashboard(self.config)
        self.executive = ExecutiveDashboard(self.config)
        logger.info("DashboardEngine initialized")

    async def get_all(self) -> List[Dashboard]:
        return self.builder.list_dashboards()

    async def create(self, name: str, dashboard_type: DashboardType = DashboardType.OPERATIONAL) -> Dashboard:
        return self.builder.create(name, dashboard_type)

    async def get(self, dashboard_id: str) -> Optional[Dashboard]:
        return self.builder.get(dashboard_id)

    async def build_executive(self) -> Dashboard:
        return self.executive.build()

    async def get_realtime_status(self) -> Dict[str, Any]:
        return self.realtime.get_status()

    async def refresh(self, dashboard_id: str) -> Optional[Dashboard]:
        return self.builder.refresh(dashboard_id)

    async def shutdown(self) -> None:
        logger.info("DashboardEngine shutdown")
