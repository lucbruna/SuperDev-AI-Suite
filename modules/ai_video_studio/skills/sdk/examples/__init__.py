"""SDK example skills — ready-to-register sample skill classes."""
from __future__ import annotations

from modules.ai_video_studio.skills.sdk.examples.avatar_skill import AvatarSkill
from modules.ai_video_studio.skills.sdk.examples.hello_world_skill import (
    HelloWorldSkill,
)
from modules.ai_video_studio.skills.sdk.examples.video_skill import VideoSkill
from modules.ai_video_studio.skills.sdk.examples.voice_skill import VoiceSkill

__all__ = ["AvatarSkill", "HelloWorldSkill", "VideoSkill", "VoiceSkill"]
