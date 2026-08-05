"""Email campaign skill — nurture email sequence drafts."""
from __future__ import annotations
from typing import Any


class EmailCampaignSkill:
    """Draft a multi-email nurture sequence for an audience."""

    skill_id = "email_campaign"
    skill_name = "Email Campaign"
    skill_version = "1.0.0"
    skill_description = "Multi-email nurture sequence (subject + body) for an audience."
    skill_category = "marketing"
    skill_tags = ["marketing", "email", "nurture", "sequence"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        product: str,
        audience: str,
        *,
        emails: int = 3,
        language: str = "en",
    ) -> dict[str, Any]:
        """Return ``emails`` sequential draft emails."""
        purposes = ("Welcome", "Value", "Offer")
        sequence: list[dict[str, Any]] = []
        for index in range(1, emails + 1):
            purpose = purposes[(index - 1) % len(purposes)]
            sequence.append(
                {
                    "position": index,
                    "purpose": purpose,
                    "subject": f"{purpose}: {product} for {audience}",
                    "body": (
                        f"Hi {audience},\n\n"
                        f"{purpose} email about {product}. "
                        f"Here is the practical value we promised.\n\n"
                        f"Next steps: {product}.\n\n— Your team"
                    ),
                }
            )
        return {
            "product": product,
            "audience": audience,
            "language": language,
            "sequence": sequence,
            "strategy": "educational-first, offer-last",
        }
