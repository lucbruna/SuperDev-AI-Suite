"""
Return Calculator - ROI and return calculation for investments.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from ..finance_context import FinanceContext
from ..financial_events import FinancialEventBus
from ..financial_config import FinancialConfig

logger = logging.getLogger(__name__)


class ReturnCalculator:
    def __init__(self, config: FinancialConfig, context: FinanceContext, event_bus: FinancialEventBus):
        self.config = config

    async def calculate_roi(self, investment: float, returns: float, years: int = 5) -> Dict[str, Any]:
        total_return = returns * years
        roi = ((total_return - investment) / investment) * 100
        annual_roi = roi / years
        return {"investment": investment, "annual_return": returns, "total_return": total_return,
                "roi_percent": round(roi, 2), "annual_roi_percent": round(annual_roi, 2)}

    async def calculate_npv(self, investment: float, cashflows: list, rate: float = 0.10) -> Dict[str, Any]:
        npv = -investment
        for i, cf in enumerate(cashflows, 1):
            npv += cf / ((1 + rate) ** i)
        return {"investment": investment, "cashflows": cashflows, "discount_rate": rate,
                "npv": round(npv, 2), "viable": npv > 0}

    async def calculate_payback(self, investment: float, annual_cashflow: float) -> Dict[str, Any]:
        years = investment / annual_cashflow if annual_cashflow else 0
        return {"investment": investment, "annual_cashflow": annual_cashflow,
                "payback_years": round(years, 1), "payback_months": round(years * 12)}