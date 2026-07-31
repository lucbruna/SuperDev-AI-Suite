"""Ledger management for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_models import Account, AccountType
from finance_intelligence.finance_registry import FinanceRegistry


class LedgerManager:
    """Trial balance and period operations over the registry accounts."""

    def __init__(self, registry: FinanceRegistry) -> None:
        self.registry = registry

    def open_ledger(self, account_id: str,
                    opening_balance: float = 0.0) -> dict[str, Any]:
        account = self.registry.get_account(account_id)
        if account is None:
            return {"account_id": account_id, "status": "not_found"}
        account.balance = round(opening_balance, 2)
        return {"account_id": account_id, "opening_balance": account.balance,
                "status": "opened"}

    def get_balance(self, account_id: str) -> float:
        account = self.registry.get_account(account_id)
        return round(account.balance, 2) if account else 0.0

    def trial_balance(self) -> dict[str, Any]:
        accounts = self.registry.list_accounts()
        total_debits = 0.0
        total_credits = 0.0
        balances = {}
        for account in accounts:
            balance = round(account.balance, 2)
            balances[account.account_id] = balance
            if balance >= 0:
                total_debits += balance
            else:
                total_credits += -balance
        return {
            "accounts": balances,
            "total_debits": round(total_debits, 2),
            "total_credits": round(total_credits, 2),
            "balanced": abs(total_debits - total_credits) < 1e-9,
        }

    def close_period(self) -> dict[str, Any]:
        trial = self.trial_balance()
        account_count = len(self.registry.list_accounts())
        return {
            "period_closed": True,
            "account_count": account_count,
            "total_debits": trial["total_debits"],
            "total_credits": trial["total_credits"],
            "balanced": trial["balanced"],
        }
