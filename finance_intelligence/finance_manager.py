"""Manager for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

import time
from typing import Any

from finance_intelligence.finance_config import FinanceConfig
from finance_intelligence.finance_context import FinanceContext
from finance_intelligence.finance_events import (FinanceEventType,
                                                 FinanceEvents)
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_models import (Account, AccountStatus,
                                                 AccountType, AuditLog,
                                                 FinancialAlert,
                                                 JournalEntry, RiskLevel,
                                                 Transaction,
                                                 TransactionStatus,
                                                 TransactionType)
from finance_intelligence.finance_protocols import new_id
from finance_intelligence.finance_registry import FinanceRegistry
from finance_intelligence.finance_security import FinanceSecurity


class FinanceManager:
    """Core operations: accounts, journal entries, transactions and the
    audit/alert trail."""

    def __init__(self, registry: FinanceRegistry,
                 events: FinanceEvents,
                 metrics: FinanceMetrics,
                 config: FinanceConfig,
                 context: FinanceContext,
                 security: FinanceSecurity,
                 engine: Any = None) -> None:
        self.registry = registry
        self.events = events
        self.metrics = metrics
        self.config = config
        self.context = context
        self.security = security
        self.engine = engine

    # -- accounts ------------------------------------------------------------
    def create_account(self, name: str,
                       account_type: AccountType = AccountType.ASSET,
                       balance: float = 0.0,
                       currency: str = "") -> Account:
        account = Account(
            account_id=new_id("account"), name=name,
            account_type=account_type, balance=balance,
            currency=currency or self.config.currency,
            created_at=time.time())
        self.registry.register_account(account)
        self.metrics.increment("fi.accounts")
        self.events.publish(FinanceEventType.ACCOUNT_CREATED,
                            {"account_id": account.account_id, "name": name})
        return account

    def get_account(self, account_id: str) -> Account | None:
        return self.registry.get_account(account_id)

    def list_accounts(self) -> list[Account]:
        return self.registry.list_accounts()

    def remove_account(self, account_id: str) -> bool:
        if not self.registry.remove_account(account_id):
            return False
        self.metrics.increment("fi.accounts", -1)
        self.events.publish(FinanceEventType.ACCOUNT_REMOVED,
                            {"account_id": account_id})
        return True

    def set_account_status(self, account_id: str,
                           status: AccountStatus) -> bool:
        account = self.registry.get_account(account_id)
        if account is None:
            return False
        account.status = status
        self.events.publish(FinanceEventType.ACCOUNT_UPDATED,
                            {"account_id": account_id,
                             "status": status.value})
        return True

    def update_balance(self, account_id: str, delta: float) -> bool:
        account = self.registry.get_account(account_id)
        if account is None:
            return False
        account.balance = round(account.balance + delta, 2)
        self.events.publish(FinanceEventType.ACCOUNT_UPDATED,
                            {"account_id": account_id,
                             "balance": account.balance})
        return True

    # -- journal entries -----------------------------------------------------
    def post_entry(self, description: str,
                   debits: list[tuple[str, float]],
                   credits: list[tuple[str, float]],
                   reference: str = "") -> JournalEntry | None:
        entry = JournalEntry(
            entry_id=new_id("entry"), description=description,
            debits=list(debits), credits=list(credits),
            date=time.time(), reference=reference,
            created_at=time.time())
        if not entry.is_balanced():
            return None
        self.registry.register_entry(entry)
        self.metrics.increment("fi.entries")
        for account_id, amount in entry.debits:
            self.update_balance(account_id, amount)
        for account_id, amount in entry.credits:
            self.update_balance(account_id, -amount)
        self.events.publish(FinanceEventType.JOURNAL_ENTRY_RECORDED,
                            {"entry_id": entry.entry_id,
                             "reference": reference})
        return entry

    def list_entries(self) -> list[JournalEntry]:
        return self.registry.list_entries()

    # -- transactions --------------------------------------------------------
    def record_transaction(self, kind: TransactionType,
                           amount: float,
                           counterparty: str = "",
                           risk_level: RiskLevel = RiskLevel.LOW,
                           description: str = "") -> Transaction:
        transaction = Transaction(
            transaction_id=new_id("transaction"), kind=kind, amount=amount,
            counterparty=counterparty, risk_level=risk_level,
            description=description, created_at=time.time())
        self.registry.register_transaction(transaction)
        self.metrics.increment("fi.transactions")
        self.events.publish(FinanceEventType.TRANSACTION_RECORDED,
                            {"transaction_id": transaction.transaction_id,
                             "kind": kind.value, "amount": amount})
        return transaction

    def get_transaction(self, transaction_id: str) -> Transaction | None:
        return self.registry.get_transaction(transaction_id)

    def list_transactions(self) -> list[Transaction]:
        return self.registry.list_transactions()

    def approve_transaction(self, transaction_id: str,
                            actor: str) -> bool:
        transaction = self.registry.get_transaction(transaction_id)
        if transaction is None:
            return False
        if not self.security.approve(actor):
            self.security.audit_deny(actor, transaction_id)
            return False
        transaction.status = TransactionStatus.APPROVED
        self.events.publish(FinanceEventType.TRANSACTION_APPROVED,
                            {"transaction_id": transaction_id,
                             "actor": actor})
        return True

    def reject_transaction(self, transaction_id: str,
                           actor: str) -> bool:
        transaction = self.registry.get_transaction(transaction_id)
        if transaction is None:
            return False
        if not self.security.approve(actor):
            self.security.audit_deny(actor, transaction_id)
            return False
        transaction.status = TransactionStatus.REJECTED
        self.events.publish(FinanceEventType.TRANSACTION_REJECTED,
                            {"transaction_id": transaction_id,
                             "actor": actor})
        return True

    def settle_transaction(self, transaction_id: str) -> bool:
        transaction = self.registry.get_transaction(transaction_id)
        if transaction is None:
            return False
        transaction.status = TransactionStatus.SETTLED
        transaction.settled_at = time.time()
        return True

    # -- audit trail ---------------------------------------------------------
    def record_audit(self, event: str, actor: str = "system",
                     target: str = "",
                     detail: dict[str, Any] | None = None) -> AuditLog:
        audit = AuditLog(
            audit_id=new_id("audit"), event=event, actor=actor,
            target=target, detail=dict(detail or {}),
            created_at=time.time())
        self.registry.record_audit(audit)
        self.events.publish(FinanceEventType.AUDIT_RECORDED,
                            {"audit_id": audit.audit_id, "event": event})
        return audit

    def list_audits(self) -> list[AuditLog]:
        return self.registry.list_audits()

    # -- alerts --------------------------------------------------------------
    def raise_alert(self, level: RiskLevel, message: str,
                    source: str = "core") -> FinancialAlert | None:
        open_alerts = len(self.registry.open_alerts())
        if open_alerts >= self.config.max_open_alerts:
            return None
        alert = FinancialAlert(
            alert_id=new_id("alert"), level=level, message=message,
            source=source, created_at=time.time())
        self.registry.register_alert(alert)
        self.events.publish(FinanceEventType.RISK_FLAGGED,
                            {"alert_id": alert.alert_id,
                             "level": level.value, "source": source})
        return alert

    def resolve_alert(self, alert_id: str) -> bool:
        return self.registry.resolve_alert(alert_id)

    def list_alerts(self) -> list[FinancialAlert]:
        return self.registry.list_alerts()

    # -- stats ---------------------------------------------------------------
    def stats(self) -> dict[str, Any]:
        return {
            "registry": self.registry.stats(),
            "metrics": self.metrics.snapshot(),
            "config": self.config.snapshot(),
            "context": self.context.snapshot(),
        }
