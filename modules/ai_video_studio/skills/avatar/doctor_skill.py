"""Doctor skill — medical presenter avatar."""
from __future__ import annotations

from modules.ai_video_studio.skills.avatar._base import AvatarSkillBase


class DoctorSkill(AvatarSkillBase):
    skill_id = "doctor"
    skill_name = "Doctor"
    skill_version = "1.0.0"
    skill_description = "Medical presenter for health content and patient explainers."
    skill_tags = ["avatar", "presenter", "health", "medical"]
    default_style = "realistic"
    default_gender = "male"
