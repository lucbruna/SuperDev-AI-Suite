"""
Accounting Engine - Core accounting intelligence coordinator.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..finance_context import FinanceContext
from ..financial_events import FinancialEvent, FinancialEventBus, EventType
from ..financial_models import FinancialStatement, AccountEntry, AccountType, Transaction, TransactionStatus
from ..financial_config import FinancialConfig
from .transaction_analyzer import TransactionAnalyzer
from .classification import ClassificationEngine
from .reconciliation import ReconciliationEngine
from .financial_reporting import FinancialReporting

logger = logging.getLogger(__name__)


class AccountingEngine:
    def __init__(self, config: FinancialConfig, context: FinanceContext, event_bus: FinancialEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.analyzer: Optional[TransactionAnalyzer] = None
        self.classifier: Optional[ClassificationEngine] = None
        self.reconciliation: Optional[ReconciliationEngine] = None
        self.reporting: Optional[FinancialReporting] = None

    async def initialize(self) -> None:
        self.analyzer = TransactionAnalyzer(self.config, self.context, self.event_bus)
        self.classifier = ClassificationEngine(self.config, self.context, self.event_bus)
        self.reconciliation = ReconciliationEngine(self.config, self.context, self.event_bus)
        self.reporting = FinancialReporting(self.config, self.context, self.event_bus)
        logger.info("AccountingEngine initialized")

    async def get_statements(self) -> FinancialStatement:
        return await self.reporting.get_statements()

    async def shutdown(self) -> None:
        logger.info("AccountingEngine shutdown")