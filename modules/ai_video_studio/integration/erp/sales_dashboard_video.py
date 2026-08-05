"""Sales Dashboard Video — narrates a KPI dashboard."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief


class SalesDashboardVideoGenerator:
    """Builds narration scripts for sales dashboards."""

    def generate(self, *, period: str = "last quarter", revenue: float = 250000.0,
                 growth: float = 0.12, voice: str = "default") -> dict[str, Any]:
        title = f"Sales dashboard — {period}"
        scenes = [
            f"Sales overview for {period}.",
            f"Revenue reached {revenue:,.0f}, a growth of {growth:.0%}.",
            "Top products, regions and channels are highlighted.",
            "Drill into any metric to see the supporting detail.",
        ]
        return build_brief("erp", title, scenes, voice=voice,
                           period=period, revenue=round(revenue, 2),
                           growth=round(growth, 4)).to_dict()


_sales_dashboard_video_generator: SalesDashboardVideoGenerator | None = None


def get_sales_dashboard_video_generator() -> SalesDashboardVideoGenerator:
    global _sales_dashboard_video_generator
    if _sales_dashboard_video_generator is None:
        _sales_dashboard_video_generator = SalesDashboardVideoGenerator()
    return _sales_dashboard_video_generator
