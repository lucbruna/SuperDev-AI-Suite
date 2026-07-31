"""Accounting subsystem facade (Volume 35).

Aggregates ledger management, journal entries, transaction processing,
reconciliation and accounting rules.
"""

from __future__ import annotations

from typing import Any

from finance_intelligence.accounting.accounting_rules import AccountingRules
from finance_intelligence.accounting.journal_entries import (
    JournalEntryManager)
from finance_intelligence.accounting.ledger_manager import LedgerManager
from finance_intelligence.accounting.reconciliation import Reconciliation
from finance_intelligence.accounting.transaction_processor import (
    TransactionProcessor)
from finance_intelligence.finance_events import FinanceEvents
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_models import Transaction
from finance_intelligence.finance_registry import FinanceRegistry


class AccountingEngine:
    """Aggregate facade over the accounting subsystems."""

    def __init__(self, registry: FinanceRegistry | None = None,
                 events: FinanceEvents | None = None,
                 metrics: FinanceMetrics | None = None) -> None:
        self.registry = registry or FinanceRegistry()
        self.events = events or FinanceEvents()
        self.metrics = metrics or FinanceMetrics()
        self.rules = AccountingRules(self.registry)
        self.ledger = LedgerManager(self.registry)
        self.journal = JournalEntryManager(
            self.registry, self.events, self.metrics)
        self.processor = TransactionProcessor(
            self.registry, self.events, self.metrics)
        self.reconciliation = Reconciliation(self.registry, self.events)

    # -- conveniences --------------------------------------------------------
    def trial_balance(self) -> dict[str, Any]:
        return self.ledger.trial_balance()

    def create_entry(self, description: str,
                     debits: list[tuple[str, float]],
                     credits: list[tuple[str, float]],
                     reference: str = ""):
        return self.journal.create(description, debits, credits, reference)

    def process_transaction(self, transaction: Transaction) -> dict[str, Any]:
        return self.processor.process(transaction)

    def reconcile(self, account_id: str,
                  expected_balance: float) -> dict[str, Any]:
        return self.reconciliation.reconcile(account_id, expected_balance)

    def stats(self) -> dict[str, Any]:
        return {
            "ledger": self.ledger.trial_balance(),
            "entries": len(self.journal.list()),
        }
