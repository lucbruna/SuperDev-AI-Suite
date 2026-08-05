"""Corporate skill — corporate video structure, b-roll and lower thirds."""
from __future__ import annotations
from typing import Any


class CorporateSkill:
    """Plan a corporate video: structure, b-roll suggestions, lower thirds."""

    skill_id = "corporate"
    skill_name = "Corporate"
    skill_version = "1.0.0"
    skill_description = "Corporate video planning with on-brand structure and b-roll."
    skill_category = "video"
    skill_tags = ["video", "corporate", "brand", "lower-thirds"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        company: str,
        *,
        message: str = "",
        tone: str = "professional",
    ) -> dict[str, Any]:
        """Return a corporate video structure derived from the company brief."""
        core_message = message or f"What {company} does, and why it matters."
        structure = [
            {"section": "Intro", "content": f"Open with {company} in one line."},
            {"section": "Message", "content": core_message},
            {"section": "Proof", "content": f"Show {company} in action with real results."},
            {"section": "CTA", "content": f"Direct viewers to engage with {company}."},
        ]
        return {
            "platform": "corporate",
            "company": company,
            "tone": tone,
            "structure": structure,
            "b_roll_suggestions": [
                f"Office and team footage of {company}",
                f"Product or service close-ups from {company}",
                f"Customer interactions with {company}",
                f"Brand assets and signage for {company}",
            ],
            "lower_thirds": ["Name", "Role", "Company"],
        }
