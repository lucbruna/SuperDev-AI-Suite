"""Transaction processing for the Finance Intelligence Engine (V35).

Converts raw financial transactions into double-entry journal entries.
"""

from __future__ import annotations

import time
from typing import Any

from finance_intelligence.finance_events import (FinanceEventType,
                                                 FinanceEvents)
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_models import (AccountType,
                                                 JournalEntry,
                                                 Transaction,
                                                 TransactionType)
from finance_intelligence.finance_protocols import new_id
from finance_intelligence.finance_registry import FinanceRegistry


class TransactionProcessor:
    """Convert transactions into balanced journal entries."""

    def __init__(self, registry: FinanceRegistry,
                 events: FinanceEvents,
                 metrics: FinanceMetrics) -> None:
        self.registry = registry
        self.events = events
        self.metrics = metrics
        self._processed: list[dict[str, Any]] = []

    def process(self, transaction: Transaction) -> dict[str, Any]:
        """Creates a balanced entry for a revenue/expense transaction."""
        cash_id = None
        for account in self.registry.list_accounts():
            if account.account_type == AccountType.ASSET:
                cash_id = account.account_id
                break
        if cash_id is None:
            return {"entry_id": "", "status": "error",
                    "message": "no cash (asset) account available"}
        counter_type = (AccountType.REVENUE
                        if transaction.kind == TransactionType.REVENUE
                        else AccountType.EXPENSE)
        counter_id = None
        for account in self.registry.list_accounts():
            if account.account_type == counter_type:
                counter_id = account.account_id
                break
        if counter_id is None:
            return {"entry_id": "", "status": "error",
                    "message": f"no {counter_type.value} account available"}

        if transaction.kind == TransactionType.REVENUE:
            debits = [(cash_id, transaction.amount)]
            credits = [(counter_id, transaction.amount)]
        else:
            debits = [(counter_id, transaction.amount)]
            credits = [(cash_id, transaction.amount)]

        entry = JournalEntry(
            entry_id=new_id("entry"),
            description=transaction.description or transaction.kind.value,
            debits=debits, credits=credits, date=time.time(),
            reference=transaction.transaction_id, created_at=time.time())
        self.registry.register_entry(entry)
        for account_id, amount in debits:
            account = self.registry.get_account(account_id)
            if account is not None:
                account.balance = round(account.balance + amount, 2)
        for account_id, amount in credits:
            account = self.registry.get_account(account_id)
            if account is not None:
                account.balance = round(account.balance - amount, 2)

        self.metrics.increment("fi.transactions.processed")
        self.events.publish(FinanceEventType.JOURNAL_ENTRY_RECORDED,
                            {"entry_id": entry.entry_id,
                             "reference": transaction.transaction_id})
        result = {"entry_id": entry.entry_id, "status": "processed",
                  "message": "entry recorded"}
        self._processed.append(result)
        return result

    def list_processed(self) -> list[dict[str, Any]]:
        return list(self._processed)
