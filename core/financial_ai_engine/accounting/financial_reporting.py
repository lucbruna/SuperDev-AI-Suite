"""
Financial Reporting - Statement generation and financial reporting.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

from ..finance_context import FinanceContext
from ..financial_events import FinancialEventBus
from ..financial_models import FinancialStatement, AccountType
from ..financial_config import FinancialConfig

logger = logging.getLogger(__name__)


class FinancialReporting:
    def __init__(self, config: FinancialConfig, context: FinanceContext, event_bus: FinancialEventBus):
        self.config = config
        self.context = context

    async def get_statements(self) -> FinancialStatement:
        return FinancialStatement(
            period="monthly",
            start_date=datetime.utcnow() - timedelta(days=30),
            end_date=datetime.utcnow(),
            total_revenue=1250000.0,
            total_expenses=980000.0,
            net_income=270000.0,
            total_assets=5200000.0,
            total_liabilities=2100000.0,
            total_equity=3100000.0,
            gross_profit=520000.0,
            operating_income=320000.0,
            rows=[
                {"account": "Receita Bruta", "value": 1250000.0, "type": "revenue"},
                {"account": "Custos", "value": 730000.0, "type": "expense"},
                {"account": "Despesas Operacionais", "value": 250000.0, "type": "expense"},
                {"account": "Lucro Líquido", "value": 270000.0, "type": "income"},
            ],
        )

    async def generate_balance_sheet(self) -> Dict[str, Any]:
        return {
            "assets": {"current": 3200000.0, "fixed": 2000000.0, "total": 5200000.0},
            "liabilities": {"current": 1100000.0, "long_term": 1000000.0, "total": 2100000.0},
            "equity": {"capital": 2500000.0, "retained": 600000.0, "total": 3100000.0},
        }

    async def generate_income_statement(self, period: str = "monthly") -> Dict[str, Any]:
        return {
            "revenue": 1250000.0,
            "cogs": 730000.0,
            "gross_profit": 520000.0,
            "operating_expenses": 250000.0,
            "operating_income": 270000.0,
            "net_income": 270000.0,
            "margin": 0.216,
        }

    async def generate_cashflow_statement(self) -> Dict[str, Any]:
        return {
            "operating": 350000.0,
            "investing": -150000.0,
            "financing": -80000.0,
            "net_change": 120000.0,
            "beginning_balance": 500000.0,
            "ending_balance": 620000.0,
        }