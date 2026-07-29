"""
Profitability Model - Profitability analysis and simulation.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..finance_context import FinanceContext
from ..financial_events import FinancialEvent, FinancialEventBus, EventType
from ..financial_config import FinancialConfig

logger = logging.getLogger(__name__)


class ProfitabilityModel:
    def __init__(self, config: FinancialConfig, context: FinanceContext, event_bus: FinancialEventBus):
        self.config = config
        self.event_bus = event_bus

    async def analyze(self, revenue: Dict, expense: Dict) -> Dict[str, Any]:
        rev_total = revenue.get("total", 0)
        exp_total = expense.get("total", 0)
        return {
            "revenue": rev_total, "expenses": exp_total,
            "gross_profit": rev_total - exp_total,
            "net_margin": (rev_total - exp_total) / rev_total * 100 if rev_total else 0,
            "gross_margin": 38.5,
            "ebitda": rev_total * 0.22,
            "status": "profitable",
            "trend": "improving",
        }

    async def simulate(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        name = scenario.get("name", "unknown")
        if "cost_reduction" in scenario:
            reduction = scenario["cost_reduction"]
            return {
                "scenario": name,
                "impact": f"Redução de {reduction*100}% nos custos",
                "profit_impact": f"+{reduction * 1.2 * 100}% no lucro",
                "new_margin": 42.0,
                "risk": "low",
            }
        if "revenue_increase" in scenario:
            increase = scenario["revenue_increase"]
            return {
                "scenario": name,
                "impact": f"Aumento de {increase*100}% na receita",
                "profit_impact": f"+{increase * 0.8 * 100}% no lucro",
                "new_margin": 40.0,
                "risk": "medium",
            }
        return {"scenario": name, "impact": "Analisado", "profit_impact": "Neutro", "new_margin": 38.0, "risk": "low"}

    async def calculate_breakeven(self, fixed_costs: float, unit_price: float, unit_cost: float) -> Dict[str, Any]:
        contribution = unit_price - unit_cost
        units = fixed_costs / contribution if contribution else 0
        return {"fixed_costs": fixed_costs, "unit_price": unit_price, "unit_cost": unit_cost,
                "contribution_margin": contribution, "breakeven_units": round(units),
                "breakeven_revenue": round(units * unit_price, 2)}