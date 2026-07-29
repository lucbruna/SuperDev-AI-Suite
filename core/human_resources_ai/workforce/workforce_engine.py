"""
Workforce Engine - Core workforce intelligence coordination.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..employee_context import EmployeeContext
from ..hr_events import HREvent, HREventBus, EventType
from ..hr_models import WorkforcePlan, ShiftSchedule
from ..hr_config import HRConfig
from .demand_prediction import DemandPrediction
from .scheduling import SchedulingEngine
from .capacity_analysis import CapacityAnalysis

logger = logging.getLogger(__name__)


class WorkforceEngine:
    def __init__(self, config: HRConfig, context: EmployeeContext, event_bus: HREventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.demand: Optional[DemandPrediction] = None
        self.scheduling: Optional[SchedulingEngine] = None
        self.capacity: Optional[CapacityAnalysis] = None

    async def initialize(self) -> None:
        self.demand = DemandPrediction(self.config, self.context, self.event_bus)
        self.scheduling = SchedulingEngine(self.config, self.context, self.event_bus)
        self.capacity = CapacityAnalysis(self.config, self.context, self.event_bus)
        logger.info("WorkforceEngine initialized")

    async def get_plan(self) -> WorkforcePlan:
        return WorkforcePlan(period="2026-H2", total_headcount=500, open_positions=15)

    async def predict_demand(self, months: int = 12) -> WorkforcePlan:
        plan = WorkforcePlan(period=f"next_{months}m", projected_hires=10)
        await self.event_bus.publish(HREvent(
            event_type=EventType.WORKFORCE_DEMAND_CHANGED,
            payload={"months": months, "projected_hires": plan.projected_hires},
        ))
        return plan

    async def shutdown(self) -> None:
        logger.info("WorkforceEngine shutdown")
