"""Finance models."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    REFUND = "refund"


class AccountType(Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class BudgetStatus(Enum):
    UNDER = "under_budget"
    ON_TARGET = "on_target"
    OVER = "over_budget"


@dataclass
class Transaction:
    transaction_id: str
    amount: float
    transaction_type: TransactionType
    category: str = ""
    description: str = ""
    date: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Account:
    account_id: str
    name: str
    account_type: AccountType
    balance: float = 0.0
    currency: str = "USD"
    parent_id: str | None = None


@dataclass
class Budget:
    budget_id: str
    name: str
    amount: float
    spent: float = 0.0
    period_start: datetime | None = None
    period_end: datetime | None = None
    category: str = ""

    @property
    def remaining(self) -> float:
        return self.amount - self.spent

    @property
    def utilization(self) -> float:
        return (self.spent / self.amount * 100) if self.amount > 0 else 0.0

    @property
    def status(self) -> BudgetStatus:
        r = self.utilization
        if r > 100:
            return BudgetStatus.OVER
        elif r >= 90:
            return BudgetStatus.ON_TARGET
        return BudgetStatus.UNDER


@dataclass
class PnLReport:
    period: str
    revenue: float = 0.0
    expenses: float = 0.0
    net_income: float = 0.0
    categories: dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class CashFlowEntry:
    date: datetime
    inflow: float = 0.0
    outflow: float = 0.0
    net: float = 0.0
    category: str = ""


@dataclass
class CashFlowReport:
    period: str
    entries: list[CashFlowEntry] = field(default_factory=list)
    total_inflow: float = 0.0
    total_outflow: float = 0.0
    net_cash_flow: float = 0.0
