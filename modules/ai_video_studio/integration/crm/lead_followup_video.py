"""Lead Follow-up Video — personalized follow-ups for captured leads."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief


class LeadFollowupGenerator:
    """Builds personalized follow-up narration scripts."""

    def generate(self, *, lead: str = "you", interest: str = "pricing",
                 team: str = "our sales team", voice: str = "default") -> dict[str, Any]:
        title = "Thank you for your interest"
        scenes = [
            f"Thanks for reaching out, {lead}.",
            f"We noticed you asked about {interest}.",
            f"{team} is ready to answer and prepared a quick summary.",
            "Book a call — it takes two minutes and there is no pressure.",
        ]
        return build_brief("crm", title, scenes, voice=voice,
                           lead=lead, interest=interest, team=team).to_dict()


_lead_followup_generator: LeadFollowupGenerator | None = None


def get_lead_followup_generator() -> LeadFollowupGenerator:
    global _lead_followup_generator
    if _lead_followup_generator is None:
        _lead_followup_generator = LeadFollowupGenerator()
    return _lead_followup_generator
