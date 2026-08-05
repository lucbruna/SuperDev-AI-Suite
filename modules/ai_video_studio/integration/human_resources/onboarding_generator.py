"""Onboarding Generator — employee onboarding welcome videos."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief


class OnboardingGenerator:
    """Builds employee onboarding narration scripts."""

    def generate(self, *, name: str = "new teammate", role: str = "your role",
                 team: str = "the team", voice: str = "default") -> dict[str, Any]:
        title = f"Welcome, {name}!"
        scenes = [
            f"Welcome to {team}, {name}!",
            f"In your {role} you will find everything you need to start.",
            "Complete your profile, review policies and meet your buddy.",
            "Your first-week checklist is attached below.",
        ]
        return build_brief("human_resources", title, scenes, voice=voice,
                           name=name, role=role, team=team).to_dict()


_onboarding_generator: OnboardingGenerator | None = None


def get_onboarding_generator() -> OnboardingGenerator:
    global _onboarding_generator
    if _onboarding_generator is None:
        _onboarding_generator = OnboardingGenerator()
    return _onboarding_generator
