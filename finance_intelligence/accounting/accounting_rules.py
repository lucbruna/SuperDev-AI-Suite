"""Accounting rules for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from finance_intelligence.finance_models import (Account, AccountType,
                                                 JournalEntry)
from finance_intelligence.finance_registry import FinanceRegistry


class AccountingRules:
    """Double-entry and account-type validation rules."""

    def __init__(self, registry: FinanceRegistry) -> None:
        self.registry = registry

    def is_double_entry(self, entry: JournalEntry) -> bool:
        return entry.is_balanced()

    def valid_account_type(self, account: Account,
                           is_debit: bool) -> bool:
        """Any registered account may be debited or credited.

        Double-entry does not restrict direction per account type; the
        normal balance is a reporting convention (see
        ``normal_balance_side``), not a posting restriction.
        """
        return isinstance(account.account_type, AccountType)

    def normal_balance_side(self, account: Account) -> str:
        """Normal balance side: asset/expense debit, others credit."""
        if account.account_type in (AccountType.ASSET, AccountType.EXPENSE):
            return "debit"
        return "credit"

    def validate_entry(self, entry: JournalEntry) -> list[str]:
        errors: list[str] = []
        if not self.is_double_entry(entry):
            errors.append("entry is not balanced")
        for account_id, _amount in entry.debits:
            account = self.registry.get_account(account_id)
            if account is None:
                errors.append(f"debit account not found: {account_id}")
            elif not self.valid_account_type(account, is_debit=True):
                errors.append(
                    f"debit on invalid account type: {account_id}")
        for account_id, _amount in entry.credits:
            account = self.registry.get_account(account_id)
            if account is None:
                errors.append(f"credit account not found: {account_id}")
            elif not self.valid_account_type(account, is_debit=False):
                errors.append(
                    f"credit on invalid account type: {account_id}")
        return errors
