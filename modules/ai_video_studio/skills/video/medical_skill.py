"""Medical skill — healthcare explainer plan with disclaimer and a11y notes."""
from __future__ import annotations
from typing import Any


class MedicalSkill:
    """Plan a patient-friendly medical explainer with safety rails."""

    skill_id = "medical"
    skill_name = "Medical"
    skill_version = "1.0.0"
    skill_description = "Medical explainer structure with disclaimer and accessibility."
    skill_category = "video"
    skill_tags = ["video", "medical", "healthcare", "accessibility"]
    skill_permissions = ["content:plan"]

    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        topic: str,
        *,
        audience: str = "patients",
    ) -> dict[str, Any]:
        """Return a safe, patient-first explainer plan for the given topic."""
        sections = [
            {"title": "What is it", "content": f"Explain {topic} in plain language."},
            {"title": "Signs and symptoms", "content": f"Describe common signs of {topic}."},
            {"title": "When to seek help", "content": f"List when {topic} needs professional care."},
        ]
        return {
            "platform": "medical",
            "topic": topic,
            "audience": audience,
            "disclaimer": "Educational content. Not a substitute for professional medical advice.",
            "sections": sections,
            "title_safe_zones": True,
            "accessibility": {
                "captions": True,
                "high_contrast": True,
                "simple_language": True,
            },
        }
