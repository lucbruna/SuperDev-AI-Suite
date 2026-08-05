"""Investment Reports — portfolio and project investment summaries."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief


class InvestmentReportGenerator:
    """Builds narration scripts for investment reports."""

    def generate(self, *, portfolio: str = "growth portfolio", value: float = 1000000.0,
                 return_pct: float = 0.08, voice: str = "default") -> dict[str, Any]:
        title = f"Investment report — {portfolio}"
        scenes = [
            f"Investment overview for the {portfolio}.",
            f"Portfolio value {value:,.0f} with a return of {return_pct:.1%}.",
            "Asset allocation and top performers are highlighted.",
            "Risk metrics and recommendations for the next period.",
        ]
        return build_brief("finance", title, scenes, voice=voice,
                           portfolio=portfolio, value=round(value, 2),
                           return_pct=round(return_pct, 4)).to_dict()


_investment_report_generator: InvestmentReportGenerator | None = None


def get_investment_report_generator() -> InvestmentReportGenerator:
    global _investment_report_generator
    if _investment_report_generator is None:
        _investment_report_generator = InvestmentReportGenerator()
    return _investment_report_generator
