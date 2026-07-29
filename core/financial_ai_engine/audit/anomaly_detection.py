"""
Anomaly Detection - AI-powered financial anomaly detection.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from ..finance_context import FinanceContext
from ..financial_events import FinancialEvent, FinancialEventBus, EventType
from ..financial_models import AnomalyReport
from ..financial_config import FinancialConfig

logger = logging.getLogger(__name__)


class AnomalyDetection:
    def __init__(self, config: FinancialConfig, context: FinanceContext, event_bus: FinancialEventBus):
        self.config = config
        self.event_bus = event_bus

    async def detect(self, transactions: List[Dict[str, Any]]) -> List[AnomalyReport]:
        anomalies = []
        for tx in transactions:
            if tx.get("amount", 0) > 500000:
                a = AnomalyReport(
                    anomaly_id=f"ANM-{tx.get('id', 'unknown')}",
                    type="high_value", description=f"Transação de alto valor: R$ {tx.get('amount', 0):.2f}",
                    severity="high", amount=tx.get("amount", 0),
                )
                anomalies.append(a)
                await self.event_bus.publish(FinancialEvent(
                    event_type=EventType.ANOMALY_DETECTED,
                    payload={"id": a.anomaly_id, "amount": a.amount, "type": a.type},
                ))
            if tx.get("is_duplicate", False):
                a = AnomalyReport(
                    anomaly_id=f"ANM-DUP-{tx.get('id', 'unknown')}",
                    type="duplicate", description="Transação duplicada detectada",
                    severity="medium", amount=tx.get("amount", 0),
                )
                anomalies.append(a)
        return anomalies

    async def detect_patterns(self, days: int = 30) -> Dict[str, Any]:
        return {"anomalies_found": 3, "patterns": ["picos_quarta-feira", "valores_acima_media"],
                "affected_accounts": ["contas_pagar", "contas_receber"]}

    async def get_anomaly_stats(self) -> Dict[str, Any]:
        return {"total_detected": 15, "confirmed": 8, "false_positives": 5, "avg_severity": "medium"}