"""Accounting Dashboard — narrates accounting KPIs."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief


class AccountingDashboardGenerator:
    """Builds narration scripts for accounting dashboards."""

    def generate(self, *, period: str = "this month", revenue: float = 120000.0,
                 expenses: float = 95000.0, voice: str = "default") -> dict[str, Any]:
        margin = (revenue - expenses) / revenue if revenue else 0.0
        title = f"Accounting dashboard — {period}"
        scenes = [
            f"Accounting overview for {period}.",
            f"Revenue {revenue:,.0f} against expenses {expenses:,.0f}.",
            f"Net margin of {margin:.1%} — {('positive' if margin >= 0 else 'negative')}.",
            "Cash flow, receivables and payables are shown below.",
        ]
        return build_brief("finance", title, scenes, voice=voice,
                           period=period, revenue=round(revenue, 2),
                           expenses=round(expenses, 2), margin=round(margin, 4)).to_dict()


_accounting_dashboard_generator: AccountingDashboardGenerator | None = None


def get_accounting_dashboard_generator() -> AccountingDashboardGenerator:
    global _accounting_dashboard_generator
    if _accounting_dashboard_generator is None:
        _accounting_dashboard_generator = AccountingDashboardGenerator()
    return _accounting_dashboard_generator
