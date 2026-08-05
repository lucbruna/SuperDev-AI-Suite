"""Financial report skill — structured financial summary and metrics."""
from __future__ import annotations
from typing import Any


class FinancialReportSkill:
    """Summarize financials into a report with headline metrics."""

    skill_id = "financial_report"
    skill_name = "Financial Report"
    skill_version = "1.0.0"
    skill_description = "Structured financial report: P&L, cash, and key ratios."
    skill_category = "business"
    skill_tags = ["business", "finance", "reporting", "metrics"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        entity: str,
        *,
        revenue: float = 0.0,
        expenses: float = 0.0,
        language: str = "en",
    ) -> dict[str, Any]:
        """Return a financial report skeleton with computed margins."""
        gross = revenue - expenses
        margin = (gross / revenue) if revenue else 0.0
        return {
            "entity": entity,
            "language": language,
            "currency": "USD",
            "headline": {
                "revenue": revenue,
                "expenses": expenses,
                "gross_profit": gross,
                "gross_margin": round(margin, 4),
            },
            "statements": [
                {"statement": "Profit & Loss", "content": "Revenue lines, COGS, OPEX, and net result."},
                {"statement": "Cash Flow", "content": "Operating, investing, and financing flows."},
                {"statement": "Balance Sheet", "content": "Assets, liabilities, and equity."},
            ],
            "ratios": ["gross margin", "operating margin", "burn rate", "runway"],
            "notes": "Fill each statement with verified figures before distribution.",
        }
