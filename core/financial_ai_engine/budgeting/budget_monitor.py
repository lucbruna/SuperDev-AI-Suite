"""
Budget Monitor - Real-time budget tracking and monitoring.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from ..finance_context import FinanceContext
from ..financial_events import FinancialEvent, FinancialEventBus, EventType
from ..financial_models import BudgetLine, BudgetReport
from ..financial_config import FinancialConfig

logger = logging.getLogger(__name__)


class BudgetMonitor:
    def __init__(self, config: FinancialConfig, context: FinanceContext, event_bus: FinancialEventBus):
        self.config = config
        self.event_bus = event_bus

    async def get_report(self, period: str = "monthly") -> BudgetReport:
        lines = [
            BudgetLine(id="BL-01", category="Operacional", department="Operações", planned_amount=500000.0,
                       actual_amount=480000.0, variance=-20000.0, variance_percent=-4.0, period=period),
            BudgetLine(id="BL-02", category="Marketing", department="Comercial", planned_amount=100000.0,
                       actual_amount=160000.0, variance=60000.0, variance_percent=60.0, period=period),
            BudgetLine(id="BL-03", category="Folha", department="RH", planned_amount=300000.0,
                       actual_amount=295000.0, variance=-5000.0, variance_percent=-1.7, period=period),
        ]
        total_planned = sum(l.planned_amount for l in lines)
        total_actual = sum(l.actual_amount for l in lines)
        return BudgetReport(period=period, total_planned=total_planned, total_actual=total_actual,
            total_variance=total_actual - total_planned, lines=lines,
            status="attention", recommendations=["Revisar orçamento de marketing - desvio de 60%"])

    async def check_deviations(self) -> List[Dict[str, Any]]:
        deviations = []
        report = await self.get_report()
        for line in report.lines:
            if abs(line.variance_percent) > self.config.budgeting.deviation_warning_percent:
                deviations.append({"category": line.category, "variance": line.variance_percent, "severity": "warning"})
            if abs(line.variance_percent) > self.config.budgeting.deviation_critical_percent:
                deviations[-1]["severity"] = "critical"
                await self.event_bus.publish(FinancialEvent(
                    event_type=EventType.BUDGET_DEVIATION,
                    payload={"line": line.id, "variance": line.variance_percent},
                ))
        return deviations