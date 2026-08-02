"""Lawyer skill — legal presenter avatar."""
from __future__ import annotations

from modules.ai_video_studio.skills.avatar._base import AvatarSkillBase


class LawyerSkill(AvatarSkillBase):
    skill_id = "lawyer"
    skill_name = "Lawyer"
    skill_version = "1.0.0"
    skill_description = "Legal presenter for compliance, contracts and legal explainers."
    skill_tags = ["avatar", "presenter", "legal"]
    default_style = "realistic"
