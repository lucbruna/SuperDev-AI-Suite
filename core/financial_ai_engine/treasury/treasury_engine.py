"""
Treasury Engine - Core treasury intelligence coordination.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from ..finance_context import FinanceContext
from ..financial_events import FinancialEvent, FinancialEventBus, EventType
from ..financial_models import TreasuryPosition
from ..financial_config import FinancialConfig
from .liquidity_manager import LiquidityManager
from .payment_manager import PaymentManager
from .bank_connector import BankConnector
from .cash_position import CashPosition

logger = logging.getLogger(__name__)


class TreasuryEngine:
    def __init__(self, config: FinancialConfig, context: FinanceContext, event_bus: FinancialEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.liquidity: Optional[LiquidityManager] = None
        self.payments: Optional[PaymentManager] = None
        self.bank: Optional[BankConnector] = None
        self.cash_position: Optional[CashPosition] = None

    async def initialize(self) -> None:
        self.liquidity = LiquidityManager(self.config, self.context, self.event_bus)
        self.payments = PaymentManager(self.config, self.context, self.event_bus)
        self.bank = BankConnector(self.config, self.context, self.event_bus)
        self.cash_position = CashPosition(self.config, self.context, self.event_bus)
        logger.info("TreasuryEngine initialized")

    async def get_position(self) -> TreasuryPosition:
        return await self.cash_position.get()

    async def handle_cash_crisis(self, payload: Dict[str, Any]) -> None:
        logger.warning(f"Cash crisis: {payload}")

    async def generate_alert(self, alert_type: str) -> None:
        await self.event_bus.publish(FinancialEvent(
            event_type=EventType.FINANCIAL_ALERT,
            payload={"type": alert_type, "timestamp": "now"},
        ))

    async def shutdown(self) -> None:
        logger.info("TreasuryEngine shutdown")