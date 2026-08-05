"""Meeting summary skill — structured meeting minutes and actions."""
from __future__ import annotations
from typing import Any


class MeetingSummarySkill:
    """Turn meeting notes into structured minutes with action items."""

    skill_id = "meeting_summary"
    skill_name = "Meeting Summary"
    skill_version = "1.0.0"
    skill_description = "Structured meeting minutes: decisions, actions, owners."
    skill_category = "business"
    skill_tags = ["business", "meetings", "minutes", "actions"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        topic: str,
        *,
        attendees: tuple[str, ...] = ("team",),
        language: str = "en",
    ) -> dict[str, Any]:
        """Return a minutes template with deterministic placeholders."""
        return {
            "topic": topic,
            "attendees": list(attendees),
            "language": language,
            "minutes": {
                "decisions": [f"{topic}: decision to record after discussion."],
                "action_items": [
                    {
                        "action": f"Follow up on {topic} action item {index}.",
                        "owner": attendees[index % len(attendees)],
                        "due": "Next meeting",
                    }
                    for index in range(3)
                ],
                "open_questions": [f"Open question on {topic} for the next session."],
            },
            "format": "decisions → actions → open questions",
        }
