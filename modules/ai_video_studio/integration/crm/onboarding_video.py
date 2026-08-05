"""Onboarding Video — welcomes new customers and explains first steps."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief


class OnboardingVideoGenerator:
    """Builds welcome/onboarding narration scripts for new customers."""

    def generate(self, *, customer: str = "new customer", product: str = "our platform",
                 voice: str = "default") -> dict[str, Any]:
        title = f"Welcome to {product}"
        scenes = [
            f"Welcome aboard, {customer}!",
            f"Here is how to get the most from {product}.",
            "Set up your profile and invite your team.",
            "Follow the 5-minute tour to see the key features.",
            "Need help? Our support team is one message away.",
        ]
        return build_brief("crm", title, scenes, voice=voice,
                           customer=customer, product=product).to_dict()


_onboarding_video_generator: OnboardingVideoGenerator | None = None


def get_onboarding_video_generator() -> OnboardingVideoGenerator:
    global _onboarding_video_generator
    if _onboarding_video_generator is None:
        _onboarding_video_generator = OnboardingVideoGenerator()
    return _onboarding_video_generator
