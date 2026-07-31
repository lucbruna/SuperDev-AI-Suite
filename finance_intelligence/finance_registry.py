"""Central registry for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_models import (Account, AuditLog,
                                                 FinancialAlert, JournalEntry,
                                                 Transaction)


class FinanceRegistry:
    """Public CRUD over accounts, journal entries, transactions, audits and
    alerts. Subsystems keep their own specialized stores."""

    def __init__(self) -> None:
        self._accounts: dict[str, Account] = {}
        self._entries: dict[str, JournalEntry] = {}
        self._transactions: dict[str, Transaction] = {}
        self._audits: dict[str, AuditLog] = {}
        self._alerts: dict[str, FinancialAlert] = {}
        self._max_audits = 2000

    # -- accounts ------------------------------------------------------------
    def register_account(self, account: Account) -> None:
        self._accounts[account.account_id] = account

    def get_account(self, account_id: str) -> Account | None:
        return self._accounts.get(account_id)

    def list_accounts(self) -> list[Account]:
        return list(self._accounts.values())

    def remove_account(self, account_id: str) -> bool:
        return self._accounts.pop(account_id, None) is not None

    def count_accounts(self) -> int:
        return len(self._accounts)

    # -- journal entries -----------------------------------------------------
    def register_entry(self, entry: JournalEntry) -> None:
        self._entries[entry.entry_id] = entry

    def get_entry(self, entry_id: str) -> JournalEntry | None:
        return self._entries.get(entry_id)

    def list_entries(self) -> list[JournalEntry]:
        return list(self._entries.values())

    def count_entries(self) -> int:
        return len(self._entries)

    # -- transactions --------------------------------------------------------
    def register_transaction(self, transaction: Transaction) -> None:
        self._transactions[transaction.transaction_id] = transaction

    def get_transaction(self, transaction_id: str) -> Transaction | None:
        return self._transactions.get(transaction_id)

    def list_transactions(self) -> list[Transaction]:
        return list(self._transactions.values())

    def remove_transaction(self, transaction_id: str) -> bool:
        return self._transactions.pop(transaction_id, None) is not None

    def count_transactions(self) -> int:
        return len(self._transactions)

    # -- audit trail ---------------------------------------------------------
    def record_audit(self, audit: AuditLog) -> None:
        self._audits[audit.audit_id] = audit
        if len(self._audits) > self._max_audits:
            oldest = next(iter(self._audits))
            del self._audits[oldest]

    def get_audit(self, audit_id: str) -> AuditLog | None:
        return self._audits.get(audit_id)

    def list_audits(self) -> list[AuditLog]:
        return list(self._audits.values())

    def count_audits(self) -> int:
        return len(self._audits)

    # -- alerts --------------------------------------------------------------
    def register_alert(self, alert: FinancialAlert) -> None:
        self._alerts[alert.alert_id] = alert

    def get_alert(self, alert_id: str) -> FinancialAlert | None:
        return self._alerts.get(alert_id)

    def list_alerts(self) -> list[FinancialAlert]:
        return list(self._alerts.values())

    def resolve_alert(self, alert_id: str) -> bool:
        alert = self._alerts.get(alert_id)
        if alert is None:
            return False
        alert.resolved = True
        return True

    def count_alerts(self) -> int:
        return len(self._alerts)

    def open_alerts(self) -> list[FinancialAlert]:
        return [alert for alert in self._alerts.values()
                if not alert.resolved]

    # -- stats ---------------------------------------------------------------
    def stats(self) -> dict[str, Any]:
        return {
            "accounts": self.count_accounts(),
            "entries": self.count_entries(),
            "transactions": self.count_transactions(),
            "audits": self.count_audits(),
            "alerts": self.count_alerts(),
        }
