"""
Transaction Analyzer - AI-powered transaction analysis and insights.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..finance_context import FinanceContext
from ..financial_events import FinancialEventBus
from ..financial_models import Transaction, TransactionType, TransactionStatus
from ..financial_config import FinancialConfig

logger = logging.getLogger(__name__)


class TransactionAnalyzer:
    def __init__(self, config: FinancialConfig, context: FinanceContext, event_bus: FinancialEventBus):
        self.config = config
        self.context = context

    async def analyze(self, transaction: Transaction) -> Dict[str, Any]:
        return {
            "id": transaction.id,
            "type": transaction.type.value,
            "amount": transaction.amount,
            "category": await self._suggest_category(transaction),
            "cost_center": await self._suggest_cost_center(transaction),
            "anomaly_score": await self._calculate_anomaly_score(transaction),
            "insights": self._generate_insights(transaction),
        }

    async def batch_analyze(self, transactions: List[Transaction]) -> List[Dict[str, Any]]:
        return [await self.analyze(t) for t in transactions]

    async def _suggest_category(self, t: Transaction) -> str:
        keywords = {"fornecedor": "custo_operacional", "salario": "folha_pagamento",
                    "aluguel": "despesa_fixa", "energia": "utilidades"}
        for kw, cat in keywords.items():
            if kw in t.description.lower():
                return cat
        return "outros"

    async def _suggest_cost_center(self, t: Transaction) -> str:
        return "administrativo"

    async def _calculate_anomaly_score(self, t: Transaction) -> float:
        return 0.05

    def _generate_insights(self, t: Transaction) -> List[str]:
        insights = []
        if t.amount > 50000:
            insights.append("Transação de alto valor")
        return insights