"""Engineer skill — tech presenter avatar."""
from __future__ import annotations

from modules.ai_video_studio.skills.avatar._base import AvatarSkillBase


class EngineerSkill(AvatarSkillBase):
    skill_id = "engineer"
    skill_name = "Engineer"
    skill_version = "1.0.0"
    skill_description = "Technical presenter for product demos, docs and developer content."
    skill_tags = ["avatar", "presenter", "tech", "developer"]
    default_style = "minimalist"
