"""
Payroll Engine - Core payroll intelligence coordination.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..employee_context import EmployeeContext
from ..hr_events import HREvent, HREventBus, EventType
from ..hr_models import PayrollSummary
from ..hr_config import HRConfig
from .salary_analysis import SalaryAnalysis
from .benefits_manager import BenefitsManager
from .compensation import CompensationEngine

logger = logging.getLogger(__name__)


class PayrollEngine:
    def __init__(self, config: HRConfig, context: EmployeeContext, event_bus: HREventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.salary: Optional[SalaryAnalysis] = None
        self.benefits: Optional[BenefitsManager] = None
        self.compensation: Optional[CompensationEngine] = None

    async def initialize(self) -> None:
        self.salary = SalaryAnalysis(self.config, self.context, self.event_bus)
        self.benefits = BenefitsManager(self.config, self.context, self.event_bus)
        self.compensation = CompensationEngine(self.config, self.context, self.event_bus)
        logger.info("PayrollEngine initialized")

    async def get_summary(self, period: str = "monthly") -> PayrollSummary:
        return PayrollSummary(
            period=period,
            total_employees=500,
            total_gross_pay=4500000.0,
            total_net_pay=3200000.0,
            total_benefits_cost=800000.0,
            average_salary=9000.0,
        )

    async def process_payroll(self, period: str) -> PayrollSummary:
        summary = await self.get_summary(period)
        await self.event_bus.publish(HREvent(
            event_type=EventType.PAYROLL_PROCESSED,
            payload={"period": period, "total": summary.total_gross_pay},
        ))
        return summary

    async def shutdown(self) -> None:
        logger.info("PayrollEngine shutdown")
