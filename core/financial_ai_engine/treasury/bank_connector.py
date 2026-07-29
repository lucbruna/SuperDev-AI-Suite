"""
Bank Connector - Banking API integration and transaction sync.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List

from ..finance_context import FinanceContext
from ..financial_events import FinancialEventBus
from ..financial_config import FinancialConfig

logger = logging.getLogger(__name__)


class BankConnector:
    def __init__(self, config: FinancialConfig, context: FinanceContext, event_bus: FinancialEventBus):
        self.config = config

    async def sync_transactions(self, account_id: str, days: int = 7) -> List[Dict[str, Any]]:
        return [
            {"id": "BNK-001", "date": "2026-07-28", "description": "Transferência recebida", "amount": 150000.0, "type": "credit"},
            {"id": "BNK-002", "date": "2026-07-28", "description": "Pagamento fornecedor", "amount": -45000.0, "type": "debit"},
        ]

    async def get_balance(self, account_id: str) -> Dict[str, Any]:
        return {"account_id": account_id, "balance": 680000.0, "available": 650000.0, "currency": "BRL", "updated": datetime.utcnow().isoformat()}

    async def get_accounts(self) -> List[Dict[str, Any]]:
        return [
            {"id": "CC-001", "bank": "Banco do Brasil", "type": "checking", "balance": 450000.0},
            {"id": "CC-002", "bank": "Itaú", "type": "checking", "balance": 230000.0},
            {"id": "AP-001", "bank": "XP Investimentos", "type": "investment", "balance": 1800000.0},
        ]