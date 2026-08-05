"""Pitch deck skill — investor pitch deck outline."""
from __future__ import annotations
from typing import Any


class PitchDeckSkill:
    """Build an investor pitch deck narrative slide by slide."""

    skill_id = "pitch_deck"
    skill_name = "Pitch Deck"
    skill_version = "1.0.0"
    skill_description = "Investor pitch deck outline with the classic story arc."
    skill_category = "business"
    skill_tags = ["business", "pitch", "fundraising", "startup"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        company: str,
        *,
        sector: str = "technology",
        language: str = "en",
    ) -> dict[str, Any]:
        """Return a 10-slide pitch deck structure."""
        return {
            "company": company,
            "sector": sector,
            "language": language,
            "deck": [
                {"slide": 1, "title": "Title", "content": f"{company} — one-line value proposition."},
                {"slide": 2, "title": "Problem", "content": f"The pain {sector} customers face today."},
                {"slide": 3, "title": "Solution", "content": f"How {company} solves it differently."},
                {"slide": 4, "title": "Market", "content": f"TAM/SAM/SOM for {sector}."},
                {"slide": 5, "title": "Product", "content": f"Demo and core features of {company}."},
                {"slide": 6, "title": "Traction", "content": f"Metrics proving demand for {company}."},
                {"slide": 7, "title": "Business Model", "content": f"How {company} makes money."},
                {"slide": 8, "title": "Competition", "content": f"{company} vs. the alternatives."},
                {"slide": 9, "title": "Team", "content": f"Why this team can build {company}."},
                {"slide": 10, "title": "The Ask", "content": f"Funding round and use of funds for {company}."},
            ],
            "pitch_length_min": 10,
        }
