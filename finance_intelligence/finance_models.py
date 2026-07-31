"""Models for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AccountType(Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class AccountStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FROZEN = "frozen"


class TransactionType(Enum):
    REVENUE = "revenue"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"
    PAYMENT = "payment"
    RECEIPT = "receipt"


class TransactionStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SETTLED = "settled"
    CANCELLED = "cancelled"


class InvoiceStatus(Enum):
    DRAFT = "draft"
    ISSUED = "issued"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class PaymentStatus(Enum):
    SCHEDULED = "scheduled"
    APPROVAL_REQUIRED = "approval_required"
    APPROVED = "approved"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PaymentMethod(Enum):
    PIX = "pix"
    BOLETO = "boleto"
    CARD = "card"
    TRANSFER = "transfer"
    CASH = "cash"


class FiscalRegime(Enum):
    SIMPLES_NACIONAL = "simples_nacional"
    LUCRO_PRESUMIDO = "lucro_presumido"
    LUCRO_REAL = "lucro_real"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def rank(self) -> int:
        return {"low": 0, "medium": 1, "high": 2, "critical": 3}[self.value]


@dataclass
class Account:
    """A ledger account in the chart of accounts."""
    account_id: str
    name: str
    account_type: AccountType = AccountType.ASSET
    balance: float = 0.0
    currency: str = "BRL"
    status: AccountStatus = AccountStatus.ACTIVE
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_active(self) -> bool:
        return self.status == AccountStatus.ACTIVE

    def can_debit(self) -> bool:
        return self.account_type in (AccountType.ASSET,
                                     AccountType.EXPENSE)

    def can_credit(self) -> bool:
        return self.account_type in (AccountType.LIABILITY,
                                     AccountType.EQUITY,
                                     AccountType.REVENUE)


@dataclass
class JournalEntry:
    """A double-entry bookkeeping record."""
    entry_id: str
    description: str
    debits: list[tuple[str, float]] = field(default_factory=list)
    credits: list[tuple[str, float]] = field(default_factory=list)
    date: float = 0.0
    reference: str = ""
    status: TransactionStatus = TransactionStatus.PENDING
    created_at: float = 0.0

    def debit_total(self) -> float:
        return sum(amount for _, amount in self.debits)

    def credit_total(self) -> float:
        return sum(amount for _, amount in self.credits)

    def is_balanced(self) -> bool:
        return abs(self.debit_total() - self.credit_total()) < 1e-9


@dataclass
class Transaction:
    """A financial movement between accounts or counterparties."""
    transaction_id: str
    kind: TransactionType = TransactionType.REVENUE
    amount: float = 0.0
    counterparty: str = ""
    status: TransactionStatus = TransactionStatus.PENDING
    risk_level: RiskLevel = RiskLevel.LOW
    description: str = ""
    created_at: float = 0.0
    settled_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Invoice:
    """A billing document issued to a customer."""
    invoice_id: str
    customer: str
    amount: float = 0.0
    due_date: float = 0.0
    status: InvoiceStatus = InvoiceStatus.DRAFT
    paid_amount: float = 0.0
    issued_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def outstanding(self) -> float:
        return max(0.0, round(self.amount - self.paid_amount, 2))


@dataclass
class Payment:
    """A scheduled or executed payment."""
    payment_id: str
    amount: float = 0.0
    method: PaymentMethod = PaymentMethod.PIX
    counterparty: str = ""
    status: PaymentStatus = PaymentStatus.SCHEDULED
    due_date: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Budget:
    """A spending plan for a period and category."""
    budget_id: str
    period: str
    category: str
    planned: float = 0.0
    actual: float = 0.0
    owner: str = ""
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def variance(self) -> float:
        return round(self.actual - self.planned, 2)

    def utilization(self) -> float:
        return (self.actual / self.planned) if self.planned else 0.0


@dataclass
class Forecast:
    """A predicted financial outcome for a horizon."""
    forecast_id: str
    kind: str
    horizon: str
    value: float = 0.0
    confidence: float = 0.0
    created_at: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class TaxRecord:
    """A computed tax obligation."""
    tax_id: str
    kind: str
    amount: float = 0.0
    period: str = ""
    base: float = 0.0
    rate: float = 0.0
    regime: FiscalRegime = FiscalRegime.SIMPLES_NACIONAL
    created_at: float = 0.0


@dataclass
class AuditLog:
    """An immutable audit trail entry."""
    audit_id: str
    event: str
    actor: str = "system"
    target: str = ""
    detail: dict[str, Any] = field(default_factory=dict)
    created_at: float = 0.0


@dataclass
class FinancialAlert:
    """A risk or compliance alert raised by a subsystem."""
    alert_id: str
    level: RiskLevel = RiskLevel.LOW
    message: str = ""
    source: str = ""
    created_at: float = 0.0
    resolved: bool = False
