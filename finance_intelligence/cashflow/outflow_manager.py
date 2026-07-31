"""Outflow management for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_events import (FinanceEventType,
                                                 FinanceEvents)
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_models import (RiskLevel, Transaction,
                                                 TransactionStatus,
                                                 TransactionType)
from finance_intelligence.finance_protocols import new_id, round_money
from finance_intelligence.finance_registry import FinanceRegistry


class OutflowManager:
    """Register and project cash outflows (expenses)."""

    def __init__(self, registry: FinanceRegistry,
                 events: FinanceEvents,
                 metrics: FinanceMetrics) -> None:
        self.registry = registry
        self.events = events
        self.metrics = metrics

    def register(self, description: str, amount: float,
                 payee: str = "", scheduled_for: float = 0.0,
                 risk_level: RiskLevel = RiskLevel.LOW) -> Transaction:
        transaction = Transaction(
            transaction_id=new_id("transaction"),
            kind=TransactionType.EXPENSE, amount=round_money(amount),
            counterparty=payee, status=TransactionStatus.PENDING,
            risk_level=risk_level, description=description,
            created_at=scheduled_for or 0.0,
            metadata={"scheduled_for": scheduled_for})
        self.registry.register_transaction(transaction)
        self.metrics.increment("fi.outflows")
        self.events.publish(FinanceEventType.TRANSACTION_RECORDED,
                            {"transaction_id": transaction.transaction_id,
                             "kind": "expense", "amount": transaction.amount})
        return transaction

    def list_outflows(self) -> list[Transaction]:
        return [tx for tx in self.registry.list_transactions()
                if tx.kind == TransactionType.EXPENSE]

    def total(self) -> float:
        return round_money(sum(tx.amount for tx in self.list_outflows()))

    def projected(self, horizon_days: int = 30) -> float:
        return round_money(
            sum(tx.amount for tx in self.list_outflows()
                if tx.created_at and tx.created_at <= horizon_days))
