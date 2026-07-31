"""Journal entry management for the Finance Intelligence Engine (V35)."""

from __future__ import annotations

import time

from finance_intelligence.finance_events import (FinanceEventType,
                                                 FinanceEvents)
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_models import (JournalEntry,
                                                 TransactionStatus)
from finance_intelligence.finance_protocols import new_id
from finance_intelligence.finance_registry import FinanceRegistry

_APPROVAL_ROLES = {"admin", "finance", "manager"}


class JournalEntryManager:
    """Create, approve and reject double-entry journal entries."""

    def __init__(self, registry: FinanceRegistry,
                 events: FinanceEvents,
                 metrics: FinanceMetrics) -> None:
        self.registry = registry
        self.events = events
        self.metrics = metrics

    def create(self, description: str,
               debits: list[tuple[str, float]],
               credits: list[tuple[str, float]],
               reference: str = "") -> JournalEntry | None:
        from finance_intelligence.accounting.accounting_rules import (
            AccountingRules)
        rules = AccountingRules(self.registry)
        entry = JournalEntry(
            entry_id=new_id("entry"), description=description,
            debits=list(debits), credits=list(credits),
            date=time.time(), reference=reference, created_at=time.time())
        if rules.validate_entry(entry):
            return None
        self.registry.register_entry(entry)
        for account_id, amount in entry.debits:
            account = self.registry.get_account(account_id)
            if account is not None:
                account.balance = round(account.balance + amount, 2)
        for account_id, amount in entry.credits:
            account = self.registry.get_account(account_id)
            if account is not None:
                account.balance = round(account.balance - amount, 2)
        self.metrics.increment("fi.entries")
        self.events.publish(FinanceEventType.JOURNAL_ENTRY_RECORDED,
                            {"entry_id": entry.entry_id,
                             "reference": reference})
        return entry

    def list(self) -> list[JournalEntry]:
        return self.registry.list_entries()

    def approve(self, entry_id: str, actor: str) -> bool:
        entry = self.registry.get_entry(entry_id)
        if entry is None or actor.lower() not in _APPROVAL_ROLES:
            return False
        entry.status = TransactionStatus.APPROVED
        self.events.publish(FinanceEventType.TRANSACTION_APPROVED,
                            {"entry_id": entry_id, "actor": actor})
        return True

    def reject(self, entry_id: str, actor: str) -> bool:
        entry = self.registry.get_entry(entry_id)
        if entry is None or actor.lower() not in _APPROVAL_ROLES:
            return False
        entry.status = TransactionStatus.REJECTED
        self.events.publish(FinanceEventType.TRANSACTION_REJECTED,
                            {"entry_id": entry_id, "actor": actor})
        return True
