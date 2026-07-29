"""
Outflow Analysis - Expense and cash outflow analysis.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

from ..finance_context import FinanceContext
from ..financial_events import FinancialEventBus
from ..financial_config import FinancialConfig

logger = logging.getLogger(__name__)


class OutflowAnalysis:
    def __init__(self, config: FinancialConfig, context: FinanceContext, event_bus: FinancialEventBus):
        self.config = config

    async def analyze(self, days: int = 90) -> Dict[str, Any]:
        return {
            "total_outflow": 980000.0,
            "avg_daily": 32666.67,
            "top_categories": [
                {"category": "Fornecedores", "amount": 450000.0, "percent": 45.9},
                {"category": "Folha", "amount": 280000.0, "percent": 28.6},
            ],
            "fixed_percent": 55.0,
            "variable_percent": 45.0,
            "trend": "stable",
            "cost_reduction_opportunities": 45000.0,
        }

    async def predict_payables(self, days: int = 30) -> List[Dict[str, Any]]:
        return [{"date": (datetime.utcnow() + timedelta(days=i)).strftime("%Y-%m-%d"), "expected": 32000.0} for i in range(days)]

    async def identify_waste(self) -> List[Dict[str, Any]]:
        return [{"category": "Assinaturas", "amount": 2500.0, "potential_savings": 800.0, "recommendation": "Revisar contratos"}]