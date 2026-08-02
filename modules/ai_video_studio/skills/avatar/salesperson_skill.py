"""Salesperson skill — sales presenter avatar."""
from __future__ import annotations

from modules.ai_video_studio.skills.avatar._base import AvatarSkillBase


class SalespersonSkill(AvatarSkillBase):
    skill_id = "salesperson"
    skill_name = "Salesperson"
    skill_version = "1.0.0"
    skill_description = "Sales presenter for pitches, demos and marketing videos."
    skill_tags = ["avatar", "presenter", "sales", "marketing"]
    default_style = "realistic"
    default_gender = "female"
