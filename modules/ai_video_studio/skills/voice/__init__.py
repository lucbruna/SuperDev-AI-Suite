"""Voice skills bundle — concrete skills backed by real studio services."""
from __future__ import annotations

from modules.ai_video_studio.skills.voice.dubbing_skill import DubbingSkill
from modules.ai_video_studio.skills.voice.narrator_skill import NarratorSkill
from modules.ai_video_studio.skills.voice.translator_skill import TranslatorSkill

__all__ = ["DubbingSkill", "NarratorSkill", "TranslatorSkill"]
