"""Financial Reports — periodic financial summaries in video form."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief


class FinancialReportGenerator:
    """Builds narration scripts for financial reports."""

    def generate(self, *, period: str = "Q3", revenue: float = 500000.0,
                 ebitda: float = 120000.0, voice: str = "default") -> dict[str, Any]:
        margin = ebitda / revenue if revenue else 0.0
        title = f"Financial report — {period}"
        scenes = [
            f"Financial report for {period}.",
            f"Revenue reached {revenue:,.0f} with EBITDA of {ebitda:,.0f}.",
            f"EBITDA margin {margin:.1%} vs. the previous period.",
            "Balance sheet and cash-flow highlights follow.",
        ]
        return build_brief("finance", title, scenes, voice=voice,
                           period=period, revenue=round(revenue, 2),
                           ebitda=round(ebitda, 2), margin=round(margin, 4)).to_dict()


_financial_report_generator: FinancialReportGenerator | None = None


def get_financial_report_generator() -> FinancialReportGenerator:
    global _financial_report_generator
    if _financial_report_generator is None:
        _financial_report_generator = FinancialReportGenerator()
    return _financial_report_generator
