"""Finance engine."""

from datetime import datetime

from .models import (
    Account,
    Budget,
    CashFlowEntry,
    CashFlowReport,
    PnLReport,
    Transaction,
    TransactionType,
)


class FinanceEngine:
    def __init__(self):
        self._accounts: dict[str, Account] = {}
        self._transactions: list[Transaction] = []
        self._budgets: dict[str, Budget] = {}

    def create_account(self, account: Account) -> Account:
        self._accounts[account.account_id] = account
        return account

    def get_account(self, account_id: str) -> Account | None:
        return self._accounts.get(account_id)

    def record_transaction(self, transaction: Transaction) -> Transaction:
        self._transactions.append(transaction)
        for acc in self._accounts.values():
            if transaction.transaction_type == TransactionType.INCOME:
                acc.balance += transaction.amount
            elif transaction.transaction_type == TransactionType.EXPENSE:
                acc.balance -= transaction.amount
            elif transaction.transaction_type == TransactionType.REFUND:
                acc.balance += transaction.amount
        for b in self._budgets.values():
            if b.category and b.category == transaction.category:
                if transaction.transaction_type == TransactionType.EXPENSE:
                    b.spent += transaction.amount
        return transaction

    def get_transactions(self, category: str | None = None, since: datetime | None = None) -> list[Transaction]:
        result = self._transactions
        if category:
            result = [t for t in result if t.category == category]
        if since:
            result = [t for t in result if t.date >= since]
        return result

    def create_budget(self, budget: Budget) -> Budget:
        self._budgets[budget.budget_id] = budget
        return budget

    def get_budgets(self) -> list[Budget]:
        return list(self._budgets.values())

    def generate_pnl(self, period: str = "monthly") -> PnLReport:
        revenue = sum(t.amount for t in self._transactions if t.transaction_type == TransactionType.INCOME)
        expenses = sum(t.amount for t in self._transactions if t.transaction_type == TransactionType.EXPENSE)
        categories: dict[str, float] = {}
        for t in self._transactions:
            if t.transaction_type == TransactionType.EXPENSE and t.category:
                categories[t.category] = categories.get(t.category, 0) + t.amount
        return PnLReport(
            period=period,
            revenue=revenue,
            expenses=expenses,
            net_income=revenue - expenses,
            categories=categories,
        )

    def generate_cash_flow(self, period: str = "monthly") -> CashFlowReport:
        entries: list[CashFlowEntry] = []
        total_in = 0.0
        total_out = 0.0
        for t in self._transactions:
            inflow = t.amount if t.transaction_type in (TransactionType.INCOME, TransactionType.REFUND) else 0.0
            outflow = t.amount if t.transaction_type == TransactionType.EXPENSE else 0.0
            entries.append(
                CashFlowEntry(date=t.date, inflow=inflow, outflow=outflow, net=inflow - outflow, category=t.category)
            )
            total_in += inflow
            total_out += outflow
        return CashFlowReport(
            period=period,
            entries=entries,
            total_inflow=total_in,
            total_outflow=total_out,
            net_cash_flow=total_in - total_out,
        )
