"""Voice profiles — curated voice presets for every use case.

The catalog merges the base narrator voices (``services/voice_studio``) with
the themed profiles in this package. ``build_catalog()`` returns a list of
``VoiceSpec`` used by the voice engine.
"""
from __future__ import annotations

from modules.ai_video_studio.ai_voice_studio.voice_models import VoiceSpec
from modules.ai_video_studio.ai_voice_studio.profiles.narrator_profiles import NARRATOR_PROFILES
from modules.ai_video_studio.ai_voice_studio.profiles.female_profiles import FEMALE_PROFILES
from modules.ai_video_studio.ai_voice_studio.profiles.male_profiles import MALE_PROFILES
from modules.ai_video_studio.ai_voice_studio.profiles.child_profiles import CHILD_PROFILES
from modules.ai_video_studio.ai_voice_studio.profiles.elderly_profiles import ELDERLY_PROFILES
from modules.ai_video_studio.ai_voice_studio.profiles.corporate_profiles import CORPORATE_PROFILES
from modules.ai_video_studio.ai_voice_studio.profiles.documentary_profiles import DOCUMENTARY_PROFILES
from modules.ai_video_studio.ai_voice_studio.profiles.advertising_profiles import ADVERTISING_PROFILES

_CATALOG: list[VoiceSpec] | None = None


def build_catalog() -> list[VoiceSpec]:
    """Build (once) the merged voice catalog."""
    global _CATALOG
    if _CATALOG is None:
        _CATALOG = [
            *(VoiceSpec.from_dict(p) for p in NARRATOR_PROFILES),
            *(VoiceSpec.from_dict(p) for p in FEMALE_PROFILES),
            *(VoiceSpec.from_dict(p) for p in MALE_PROFILES),
            *(VoiceSpec.from_dict(p) for p in CHILD_PROFILES),
            *(VoiceSpec.from_dict(p) for p in ELDERLY_PROFILES),
            *(VoiceSpec.from_dict(p) for p in CORPORATE_PROFILES),
            *(VoiceSpec.from_dict(p) for p in DOCUMENTARY_PROFILES),
            *(VoiceSpec.from_dict(p) for p in ADVERTISING_PROFILES),
        ]
    return list(_CATALOG)


def reset_catalog() -> None:
    global _CATALOG
    _CATALOG = None
