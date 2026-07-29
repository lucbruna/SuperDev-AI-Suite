from __future__ import annotations

from decimal import Decimal

from .cost_analyzer import BudgetManager

__all__ = ["BudgetManager"]


def create_default_budgets(manager: BudgetManager):
    manager.set_budget("Monthly Global", Decimal("500.00"), "monthly", "global")
    manager.set_budget("Project Alpha", Decimal("200.00"), "monthly", "project:alpha")
    manager.set_budget("Project Beta", Decimal("100.00"), "monthly", "project:beta")


def alert_summary(manager: BudgetManager) -> str:
    statuses = manager.budget_status()
    alerts = []
    for s in statuses:
        for a in s["alerts"]:
            alerts.append(f"[{s['name']}] {a['message']}")
    return "\n".join(alerts) if alerts else "No active alerts"