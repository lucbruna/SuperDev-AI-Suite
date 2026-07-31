"""Final wiring tests for the Finance Intelligence Engine (Volume 35).

Attaches every subsystem engine to the FinanceEngine facade and proves a
cross-subsystem financial workflow holds together.
"""

from __future__ import annotations

import pytest

from finance_intelligence.accounting.accounting_engine import \
    AccountingEngine
from finance_intelligence.advisor.advisor_engine import AdvisorEngine
from finance_intelligence.auditing.audit_engine import AuditEngine
from finance_intelligence.budgeting.budget_engine import BudgetEngine
from finance_intelligence.cashflow.cashflow_engine import CashflowEngine
from finance_intelligence.expenses.expense_engine import ExpenseEngine
from finance_intelligence.finance_engine import FinanceEngine
from finance_intelligence.finance_models import TransactionType
from finance_intelligence.forecasting.forecast_engine import ForecastEngine
from finance_intelligence.payments.payment_engine import PaymentEngine
from finance_intelligence.receivables.receivable_engine import \
    ReceivableEngine
from finance_intelligence.taxation.tax_engine import TaxEngine


@pytest.fixture()
def engine() -> FinanceEngine:
    engine = FinanceEngine()
    accounting = AccountingEngine(engine.registry, engine.events,
                                  engine.metrics)
    cashflow = CashflowEngine(engine.registry, engine.events,
                              engine.metrics)
    payments = PaymentEngine(engine.registry, engine.events, engine.metrics)
    receivables = ReceivableEngine(engine.registry, engine.events,
                                   engine.metrics)
    expenses = ExpenseEngine(engine.registry, engine.events, engine.metrics)
    taxation = TaxEngine(engine.registry, engine.events, engine.metrics)
    auditing = AuditEngine(engine.registry, engine.events, engine.metrics)
    forecasting = ForecastEngine(engine.registry, engine.events,
                                 engine.metrics)
    budgeting = BudgetEngine(engine.registry, engine.events, engine.metrics)
    advisor = AdvisorEngine(engine.registry, engine.events, engine.metrics,
                            budget_engine=budgeting)

    engine.attach_subsystem("accounting_engine", accounting)
    engine.attach_subsystem("cashflow_engine", cashflow)
    engine.attach_subsystem("payment_engine", payments)
    engine.attach_subsystem("receivable_engine", receivables)
    engine.attach_subsystem("expense_engine", expenses)
    engine.attach_subsystem("tax_engine", taxation)
    engine.attach_subsystem("audit_engine", auditing)
    engine.attach_subsystem("forecast_engine", forecasting)
    engine.attach_subsystem("budget_engine", budgeting)
    engine.attach_subsystem("advisor_engine", advisor)
    return engine


class TestWiring:
    def test_all_subsystems_attached(self, engine: FinanceEngine) -> None:
        expected = {"accounting_engine", "cashflow_engine",
                    "payment_engine", "receivable_engine",
                    "expense_engine", "tax_engine", "audit_engine",
                    "forecast_engine", "budget_engine", "advisor_engine"}
        assert expected <= set(engine.stats()["subsystems"])

    def test_subsystems_exposed_on_engine(self, engine: FinanceEngine) -> None:
        for name in ("accounting_engine", "cashflow_engine",
                     "payment_engine", "receivable_engine",
                     "expense_engine", "tax_engine", "audit_engine",
                     "forecast_engine", "budget_engine", "advisor_engine"):
            assert getattr(engine, name) is not None

    def test_subsystems_exposed_on_manager(self, engine: FinanceEngine) -> None:
        for name in ("accounting_engine", "cashflow_engine",
                     "payment_engine", "receivable_engine",
                     "expense_engine", "tax_engine", "audit_engine",
                     "forecast_engine", "budget_engine", "advisor_engine"):
            assert getattr(engine.manager, name) is not None


class TestCrossSubsystemFlow:
    def test_full_financial_workflow(self, engine: FinanceEngine) -> None:
        # 1. core: record revenue and expense
        engine.record_transaction(TransactionType.REVENUE, 5000.0,
                                  description="sale")
        engine.record_transaction(TransactionType.EXPENSE, 2000.0,
                                  description="hosting")
        # 2. expenses: categorize and register
        expense = engine.expense_engine.register_expense(
            "office rent", 1000.0)
        assert expense.kind == TransactionType.EXPENSE

        # 3. forecasting: project from shared registry
        forecasts = engine.forecast_engine.forecast(periods=2)
        assert forecasts["revenue"].value > 0

        # 4. taxation: compute obligations (all transactions recorded,
        #    only revenue is taxable)
        records = engine.tax_engine.calculate_all()
        assert len(records) == 3
        taxable = [record for record in records if record.amount > 0]
        assert len(taxable) == 1
        assert taxable[0].amount == pytest.approx(300.0)

        # 5. auditing: record trail and check compliance
        engine.audit_engine.record("workflow.executed", actor="system")
        assert engine.audit_engine.trail.count() >= 1

        # 6. budgeting: plan and advisory reflects it
        budget = engine.budget_engine.create_budget(
            "2026-07", "hosting", 3000.0)
        budget.actual = 3500.0
        report = engine.advisor_engine.report()
        types = {insight["type"] for insight in report["insights"]}
        assert "budget_overrun" in types

        # 7. metrics and stats are shared
        stats = engine.stats()
        assert len(stats["subsystems"]) >= 10
        assert engine.metrics.count("fi.transactions") == 2

    def test_payments_receivables_shared_registry(
            self, engine: FinanceEngine) -> None:
        payment = engine.payment_engine.schedule_payment(500.0)
        assert payment.payment_id
        invoice = engine.receivable_engine.issue_invoice(
            "acme", 1000.0)
        assert invoice.invoice_id
        assert engine.registry.list_transactions() is not None
