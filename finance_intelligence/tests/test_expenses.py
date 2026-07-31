"""Tests for the expenses subsystem (Volume 35, Fase 4)."""

from __future__ import annotations

import pytest

from finance_intelligence.expenses.expense_engine import ExpenseEngine
from finance_intelligence.finance_models import (TransactionStatus,
                                                 TransactionType)


@pytest.fixture()
def engine() -> ExpenseEngine:
    return ExpenseEngine()


def category_id(engine: ExpenseEngine, name: str) -> str:
    category = engine.categories.find_by_name(name)
    assert category is not None
    return category["category_id"]


class TestCategories:
    def test_default_categories(self, engine: ExpenseEngine) -> None:
        assert len(engine.categories.list()) == 7
        assert engine.categories.find_by_name("Operacional") is not None

    def test_classify(self, engine: ExpenseEngine) -> None:
        assert engine.categories.classify("laptop Tecnologia") == \
            category_id(engine, "Tecnologia")
        assert engine.categories.classify("aluguel") == \
            category_id(engine, "Outros")

    def test_add_custom_category(self, engine: ExpenseEngine) -> None:
        engine.categories.add("Treinamento", "courses")
        assert engine.categories.find_by_name("Treinamento") is not None

    def test_spending_by_category(self, engine: ExpenseEngine) -> None:
        operational = category_id(engine, "Operacional")
        marketing = category_id(engine, "Marketing")
        engine.register_expense("aluguel", 200.0, category=operational)
        engine.register_expense("campanha", 100.0, category=marketing)
        spending = engine.spending_by_category()
        assert spending[operational] == pytest.approx(200.0)
        assert spending[marketing] == pytest.approx(100.0)


class TestApproval:
    def test_small_expense_auto_approved(self, engine: ExpenseEngine) -> None:
        expense = engine.register_expense("cafe", 100.0)
        request = engine.request_approval(expense)
        assert request["status"] == "auto_approved"
        assert expense.status == TransactionStatus.APPROVED

    def test_large_expense_requires_approval(self, engine: ExpenseEngine) -> None:
        expense = engine.register_expense("infra", 60000.0)
        request = engine.request_approval(expense)
        assert request["status"] == "approval_required"
        assert expense.status == TransactionStatus.PENDING

    def test_approve_with_role(self, engine: ExpenseEngine) -> None:
        expense = engine.register_expense("infra", 60000.0)
        request = engine.request_approval(expense)
        assert engine.approvals.approve(
            request["request_id"], "manager") is True

    def test_reject_with_role(self, engine: ExpenseEngine) -> None:
        expense = engine.register_expense("infra", 60000.0)
        request = engine.request_approval(expense)
        assert engine.approvals.reject(
            request["request_id"], "director") is True

    def test_low_role_denied(self, engine: ExpenseEngine) -> None:
        expense = engine.register_expense("infra", 60000.0)
        request = engine.request_approval(expense)
        assert engine.approvals.reject(
            request["request_id"], "employee") is False


class TestAnalysis:
    def test_monthly_totals(self, engine: ExpenseEngine) -> None:
        engine.register_expense("cafe", 100.0)
        engine.register_expense("almoco", 150.0)
        totals = engine.analysis.monthly_totals(
            engine.registry.list_transactions())
        assert totals["2026-01"] == pytest.approx(250.0)

    def test_top_expenses(self, engine: ExpenseEngine) -> None:
        engine.register_expense("cafe", 50.0)
        engine.register_expense("infra", 500.0)
        top = engine.analysis.top_expenses(
            engine.registry.list_transactions(), limit=1)
        assert len(top) == 1
        assert top[0].amount == pytest.approx(500.0)

    def test_by_category_breakdown(self, engine: ExpenseEngine) -> None:
        operational = category_id(engine, "Operacional")
        pessoal = category_id(engine, "Pessoal")
        engine.register_expense("almoco", 100.0, category=pessoal)
        engine.register_expense("aluguel", 300.0, category=operational)
        categories = {category["category_id"]: category
                      for category in engine.categories.list()}
        breakdown = engine.analysis.by_category(
            engine.registry.list_transactions(), categories)
        assert breakdown["Operacional"]["total"] == pytest.approx(300.0)
        assert breakdown["Pessoal"]["total"] == pytest.approx(100.0)


class TestOptimizer:
    def test_suggestions(self, engine: ExpenseEngine) -> None:
        for _ in range(5):
            engine.register_expense("infra recorrente", 400.0)
        categories = {category["category_id"]: category
                      for category in engine.categories.list()}
        suggestions = engine.optimizer.suggestions(
            engine.registry.list_transactions(), categories)
        assert isinstance(suggestions, list)
        assert len(suggestions) >= 1

    def test_recurring_estimate(self, engine: ExpenseEngine) -> None:
        engine.register_expense("cafe", 1000.0)
        estimate = engine.optimizer.recurring_estimate(
            engine.registry.list_transactions())
        assert estimate["annual_projection"] == pytest.approx(12000.0)


class TestEngine:
    def test_register_expense(self, engine: ExpenseEngine) -> None:
        expense = engine.register_expense("cafe", 100.0)
        assert expense.kind == TransactionType.EXPENSE
        assert len(engine.registry.list_transactions()) == 1

    def test_stats(self, engine: ExpenseEngine) -> None:
        engine.register_expense("cafe", 100.0)
        engine.register_expense("cafe", 50.0)
        stats = engine.stats()
        assert stats["total"] == pytest.approx(150.0)
        assert stats["expenses"] == 2

    def test_suggestions_facade(self, engine: ExpenseEngine) -> None:
        engine.register_expense("cafe", 100.0)
        assert isinstance(engine.suggestions(), list)
