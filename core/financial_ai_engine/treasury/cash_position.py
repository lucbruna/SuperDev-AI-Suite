"""
Cash Position - Real-time cash position tracking and analysis.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict

from ..finance_context import FinanceContext
from ..financial_events import FinancialEvent, FinancialEventBus, EventType
from ..financial_models import TreasuryPosition
from ..financial_config import FinancialConfig

logger = logging.getLogger(__name__)


class CashPosition:
    def __init__(self, config: FinancialConfig, context: FinanceContext, event_bus: FinancialEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus

    async def get(self) -> TreasuryPosition:
        pos = TreasuryPosition(
            cash_balance=680000.0, bank_balance=650000.0,
            receivables=420000.0, payables=380000.0,
            short_term_investments=500000.0, available_credit=1000000.0,
            total_liquidity=2220000.0,
        )
        self.context.treasury.set("position", {
            "cash": pos.cash_balance,
            "bank": pos.bank_balance,
            "receivables": pos.receivables,
            "payables": pos.payables,
        })
        return pos

    async def get_daily(self) -> Dict[str, Any]:
        return {
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "opening": 650000.0,
            "inflows": 180000.0,
            "outflows": 150000.0,
            "closing": 680000.0,
            "reserve_ratio": 0.35,
        }

    async def update(self, amount: float, reason: str) -> None:
        await self.event_bus.publish(FinancialEvent(
            event_type=EventType.CASH_POSITION_UPDATED,
            payload={"amount": amount, "reason": reason},
        ))