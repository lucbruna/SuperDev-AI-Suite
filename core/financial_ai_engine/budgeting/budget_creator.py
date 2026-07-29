"""
Budget Creator - Intelligent budget creation and planning.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from ..finance_context import FinanceContext
from ..financial_events import FinancialEventBus
from ..financial_models import BudgetLine
from ..financial_config import FinancialConfig

logger = logging.getLogger(__name__)


class BudgetCreator:
    def __init__(self, config: FinancialConfig, context: FinanceContext, event_bus: FinancialEventBus):
        self.config = config
        self.context = context

    async def create_department_budget(self, department: str, total: float) -> Dict[str, Any]:
        return {"department": department, "total": total, "categories": self._suggest_allocation(department, total), "status": "draft"}

    async def create_annual_budget(self, departments: Dict[str, float]) -> Dict[str, Any]:
        return {dept: await self.create_department_budget(dept, total) for dept, total in departments.items()}

    def _suggest_allocation(self, dept: str, total: float) -> Dict[str, float]:
        allocations = {"operacional": 0.5, "pessoal": 0.3, "investimento": 0.1, "reserva": 0.1}
        return {k: total * v for k, v in allocations.items()}

    async def suggest_budget_from_history(self, months: int = 12) -> Dict[str, Any]:
        return {"total": 12000000.0, "growth_rate": 0.08, "departments": {"operacional": 6000000.0, "comercial": 3600000.0, "adm": 2400000.0}}