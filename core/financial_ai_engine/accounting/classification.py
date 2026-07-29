"""
Classification Engine - Automatic transaction classification and categorization.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from ..finance_context import FinanceContext
from ..financial_events import FinancialEventBus
from ..financial_models import Transaction, TransactionType
from ..financial_config import FinancialConfig

logger = logging.getLogger(__name__)


class ClassificationEngine:
    def __init__(self, config: FinancialConfig, context: FinanceContext, event_bus: FinancialEventBus):
        self.config = config

    async def classify(self, transaction: Transaction) -> Dict[str, Any]:
        category = self._classify_by_description(transaction.description)
        return {"transaction_id": transaction.id, "category": category, "confidence": 0.85}

    async def batch_classify(self, transactions: List[Transaction]) -> List[Dict[str, Any]]:
        return [await self.classify(t) for t in transactions]

    def _classify_by_description(self, desc: str) -> str:
        rules = {
            "fornecedor": "custo_mercadorias", "salario": "folha", "aluguel": "despesa_operacional",
            "energia": "utilidades", "internet": "utilidades", "frete": "logistica",
            "marketing": "marketing", "venda": "receita", "imposto": "tributos",
        }
        for kw, cat in rules.items():
            if kw in desc.lower():
                return cat
        return "nao_classificado"

    async def suggest_account_code(self, category: str) -> str:
        codes = {
            "custo_mercadorias": "5.01", "folha": "5.02", "despesa_operacional": "5.03",
            "utilidades": "5.04", "logistica": "5.05", "marketing": "5.06",
            "receita": "3.01", "tributos": "5.07",
        }
        return codes.get(category, "9.99")