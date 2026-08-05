"""Campaign analytics skill — KPI framework for a marketing campaign."""
from __future__ import annotations
from typing import Any


class CampaignAnalyticsSkill:
    """Define KPIs, targets, and reporting cadence for a campaign."""

    skill_id = "campaign_analytics"
    skill_name = "Campaign Analytics"
    skill_version = "1.0.0"
    skill_description = "KPI framework, targets, and report cadence for a campaign."
    skill_category = "marketing"
    skill_tags = ["marketing", "analytics", "kpi", "reporting"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        campaign: str,
        *,
        budget: float = 10000.0,
        language: str = "en",
    ) -> dict[str, Any]:
        """Return a KPI plan with targets proportional to the budget."""
        kpis = ("impressions", "clicks", "conversions", "roas")
        targets = {
            "impressions": int(budget * 100),
            "clicks": int(budget * 4),
            "conversions": int(budget * 0.2),
            "roas": 3.0,
        }
        return {
            "campaign": campaign,
            "budget": budget,
            "language": language,
            "kpis": [
                {"metric": kpi, "target": targets[kpi]} for kpi in kpis
            ],
            "reporting": {"cadence": "weekly", "owner": "marketing"},
            "notes": "Rebaseline targets after the first week of data.",
        }
