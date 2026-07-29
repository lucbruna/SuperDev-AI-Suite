"""
Financial Models - Core financial data models.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class AccountType(Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class TransactionType(Enum):
    SALE = "sale"
    PURCHASE = "purchase"
    PAYMENT = "payment"
    RECEIPT = "receipt"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"
    DEPRECIATION = "depreciation"
    TAX = "tax"
    INVESTMENT = "investment"
    LOAN = "loan"


class TransactionStatus(Enum):
    PENDING = "pending"
    POSTED = "posted"
    RECONCILED = "reconciled"
    FLAGGED = "flagged"
    CANCELLED = "cancelled"


class CashflowDirection(Enum):
    INFLOW = "inflow"
    OUTFLOW = "outflow"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AccountEntry:
    id: str
    account_code: str
    account_name: str
    account_type: AccountType
    balance: float = 0.0
    currency: str = "BRL"
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Transaction:
    id: str
    type: TransactionType
    description: str
    amount: float
    currency: str = "BRL"
    date: datetime = field(default_factory=datetime.utcnow)
    category: str = ""
    cost_center: str = ""
    debit_account: str = ""
    credit_account: str = ""
    status: TransactionStatus = TransactionStatus.PENDING
    reference: str = ""
    notes: str = ""


@dataclass
class FinancialStatement:
    period: str
    start_date: datetime
    end_date: datetime
    total_revenue: float = 0.0
    total_expenses: float = 0.0
    net_income: float = 0.0
    total_assets: float = 0.0
    total_liabilities: float = 0.0
    total_equity: float = 0.0
    gross_profit: float = 0.0
    operating_income: float = 0.0
    rows: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TreasuryPosition:
    cash_balance: float = 0.0
    bank_balance: float = 0.0
    receivables: float = 0.0
    payables: float = 0.0
    short_term_investments: float = 0.0
    available_credit: float = 0.0
    total_liquidity: float = 0.0
    currency: str = "BRL"
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CashflowForecast:
    horizon_days: int
    projections: Dict[str, float] = field(default_factory=dict)
    inflows: Dict[str, float] = field(default_factory=dict)
    outflows: Dict[str, float] = field(default_factory=dict)
    total_inflow: float = 0.0
    total_outflow: float = 0.0
    net_cashflow: float = 0.0
    ending_balance: float = 0.0
    min_balance_date: Optional[str] = None
    min_balance: float = 0.0
    confidence_score: float = 0.85


@dataclass
class BudgetLine:
    id: str
    category: str
    department: str
    planned_amount: float = 0.0
    actual_amount: float = 0.0
    variance: float = 0.0
    variance_percent: float = 0.0
    period: str = ""
    notes: str = ""


@dataclass
class BudgetReport:
    period: str
    total_planned: float = 0.0
    total_actual: float = 0.0
    total_variance: float = 0.0
    lines: List[BudgetLine] = field(default_factory=list)
    status: str = "on_track"
    recommendations: List[str] = field(default_factory=list)


@dataclass
class InvestmentAnalysis:
    project_name: str
    initial_investment: float = 0.0
    expected_return: float = 0.0
    roi_percent: float = 0.0
    payback_months: int = 0
    npv: float = 0.0
    irr_percent: float = 0.0
    risk_score: float = 0.0
    recommendation: str = ""
    confidence: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    analyzed_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PortfolioHolding:
    asset: str
    type: str
    value: float
    percent: float
    return_ytd: float = 0.0
    risk: str = "medium"


@dataclass
class RiskAssessment:
    overall_score: float = 0.0
    liquidity_risk: float = 0.0
    credit_risk: float = 0.0
    market_risk: float = 0.0
    operational_risk: float = 0.0
    fraud_risk: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    factors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    assessed_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class FraudAlert:
    id: str
    transaction_id: str
    alert_type: str
    severity: str
    description: str
    amount: float = 0.0
    detected_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "open"
    reviewed_by: Optional[str] = None


@dataclass
class CreditAnalysis:
    customer_id: str
    customer_name: str
    credit_score: float = 0.0
    risk_level: str = "medium"
    recommended_limit: float = 0.0
    payment_history: str = "good"
    dso_days: int = 30
    analyzed_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AnomalyReport:
    anomaly_id: str
    type: str
    description: str
    severity: str = "medium"
    affected_accounts: List[str] = field(default_factory=list)
    amount: float = 0.0
    detected_at: datetime = field(default_factory=datetime.utcnow)
    status: str = "open"


@dataclass
class AuditReport:
    report_id: str
    period: str
    status: str = "completed"
    total_transactions_reviewed: int = 0
    anomalies_found: int = 0
    compliance_issues: int = 0
    findings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    completed_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ScenarioSimulation:
    scenario_id: str
    name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    execution_time_ms: float = 0.0


@dataclass
class FinancialAlert:
    id: str
    alert_type: str
    severity: str
    title: str
    message: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    resolved: bool = False