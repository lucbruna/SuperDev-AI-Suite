"""Personalization — adapts avatars to user preferences."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_avatar_engine.training.identity_learning import (
    get_identity_learning,
)
from modules.ai_video_studio.ai_avatar_engine.training.speech_learning import (
    get_speech_learning,
)


class Personalization:
    """Applies learned preferences to avatar/profile generation."""

    def recommend_profile_id(self, candidates: list[str]) -> str | None:
        preferred = get_identity_learning().preferred()
        if preferred and preferred in candidates:
            return preferred
        return candidates[0] if candidates else None

    def speech_profile(self) -> dict[str, Any]:
        return get_speech_learning().preferred()

    def personalize(self, descriptor: dict[str, Any]) -> dict[str, Any]:
        """Inject learned preferences into an avatar descriptor."""
        out = dict(descriptor)
        speech = self.speech_profile()
        out["speech_preferences"] = speech
        identity = get_identity_learning().preferred()
        if identity:
            out.setdefault("identity", {})["preferred"] = identity
        return out


_personalization: Personalization | None = None


def get_personalization() -> Personalization:
    global _personalization
    if _personalization is None:
        _personalization = Personalization()
    return _personalization
