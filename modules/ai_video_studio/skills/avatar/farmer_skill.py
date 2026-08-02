"""Farmer skill — agriculture presenter avatar."""
from __future__ import annotations

from modules.ai_video_studio.skills.avatar._base import AvatarSkillBase


class FarmerSkill(AvatarSkillBase):
    skill_id = "farmer"
    skill_name = "Farmer"
    skill_version = "1.0.0"
    skill_description = "Agriculture presenter for crop, livestock and rural content."
    skill_tags = ["avatar", "presenter", "agriculture"]
    default_style = "realistic"
