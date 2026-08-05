"""Management Presentations — board and executive deck videos."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief


class ManagementPresentationGenerator:
    """Builds narration scripts for executive presentations."""

    def generate(self, *, topic: str = "Strategy update", audience: str = "board",
                 slides: int = 8, voice: str = "default") -> dict[str, Any]:
        title = f"{topic} — {audience} deck"
        scenes = [
            f"Welcome to the {topic} presentation for the {audience}.",
            f"Agenda: {slides} slides covering progress, risks and plans.",
            "Key metrics and decisions that need your input.",
            "Appendix with full detail and supporting data.",
        ]
        return build_brief("finance", title, scenes, voice=voice,
                           topic=topic, audience=audience, slides=slides).to_dict()


_management_presentation_generator: ManagementPresentationGenerator | None = None


def get_management_presentation_generator() -> ManagementPresentationGenerator:
    global _management_presentation_generator
    if _management_presentation_generator is None:
        _management_presentation_generator = ManagementPresentationGenerator()
    return _management_presentation_generator
