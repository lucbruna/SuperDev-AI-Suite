"""Teacher skill — educational presenter avatar."""
from __future__ import annotations

from modules.ai_video_studio.skills.avatar._base import AvatarSkillBase


class TeacherSkill(AvatarSkillBase):
    skill_id = "teacher"
    skill_name = "Teacher"
    skill_version = "1.0.0"
    skill_description = "Educational presenter for tutorials, courses and explainers."
    skill_tags = ["avatar", "presenter", "education"]
    default_style = "realistic"
    default_gender = "female"
