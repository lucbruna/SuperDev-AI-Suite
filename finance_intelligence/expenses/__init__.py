"""Expenses subsystem for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from finance_intelligence.expenses.approval_system import ApprovalSystem
from finance_intelligence.expenses.category_manager import CategoryManager
from finance_intelligence.expenses.cost_optimizer import CostOptimizer
from finance_intelligence.expenses.expense_analysis import ExpenseAnalysis
from finance_intelligence.expenses.expense_engine import ExpenseEngine

__all__ = [
    "ExpenseEngine",
    "CategoryManager",
    "ApprovalSystem",
    "ExpenseAnalysis",
    "CostOptimizer",
]
