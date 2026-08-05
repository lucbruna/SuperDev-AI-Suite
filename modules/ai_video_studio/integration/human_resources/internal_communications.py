"""Internal Communications — company announcements and updates."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief


class InternalCommunicationsGenerator:
    """Builds announcement narration scripts."""

    def generate(self, *, headline: str = "Company update", detail: str = "New office opening",
                 voice: str = "default") -> dict[str, Any]:
        title = headline
        scenes = [
            f"{headline} — an update for everyone.",
            detail,
            "What this means for you and the next steps.",
            "Questions? Talk to your manager or HR.",
        ]
        return build_brief("human_resources", title, scenes, voice=voice,
                           headline=headline, detail=detail).to_dict()


_internal_communications_generator: InternalCommunicationsGenerator | None = None


def get_internal_communications_generator() -> InternalCommunicationsGenerator:
    global _internal_communications_generator
    if _internal_communications_generator is None:
        _internal_communications_generator = InternalCommunicationsGenerator()
    return _internal_communications_generator
