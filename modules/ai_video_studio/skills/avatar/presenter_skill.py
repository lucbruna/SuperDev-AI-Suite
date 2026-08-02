"""Presenter skill — corporate host avatar."""
from __future__ import annotations

from modules.ai_video_studio.skills.avatar._base import AvatarSkillBase


class PresenterSkill(AvatarSkillBase):
    skill_id = "presenter"
    skill_name = "Presenter"
    skill_version = "1.0.0"
    skill_description = "Corporate host presenter for news, intros and product content."
    skill_tags = ["avatar", "presenter", "host", "corporate"]
    default_style = "realistic"
    default_gender = "female"
