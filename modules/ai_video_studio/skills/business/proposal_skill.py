"""Proposal skill — client proposal structure."""
from __future__ import annotations
from typing import Any


class ProposalSkill:
    """Structure a client proposal: scope, plan, pricing, terms."""

    skill_id = "proposal"
    skill_name = "Proposal"
    skill_version = "1.0.0"
    skill_description = "Client proposal outline with scope, timeline, and pricing."
    skill_category = "business"
    skill_tags = ["business", "proposal", "sales", "deliverables"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        client: str,
        service: str,
        *,
        budget: float = 10000.0,
        language: str = "en",
    ) -> dict[str, Any]:
        """Return a proposal outline sized to the budget."""
        return {
            "client": client,
            "service": service,
            "language": language,
            "budget": budget,
            "sections": [
                {"section": "Executive Summary", "content": f"What {service} delivers for {client}."},
                {"section": "Understanding", "content": f"Restate {client}'s goals and constraints."},
                {"section": "Scope of Work", "content": f"Concrete deliverables within {service}."},
                {"section": "Timeline", "content": f"Milestones and dates for the {service} engagement."},
                {"section": "Investment", "content": f"Fee structure within the {budget:,.0f} range."},
                {"section": "Terms", "content": "Payment schedule, revisions, and acceptance."},
            ],
            "deliverables_note": "Itemize each deliverable with an acceptance criterion.",
        }
