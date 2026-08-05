"""Video skills bundle — concrete skills backed by real studio services."""
from __future__ import annotations

from modules.ai_video_studio.skills.video.advertising_skill import AdvertisingSkill
from modules.ai_video_studio.skills.video.agriculture_skill import AgricultureSkill
from modules.ai_video_studio.skills.video.cinematic_skill import CinematicSkill
from modules.ai_video_studio.skills.video.corporate_skill import CorporateSkill
from modules.ai_video_studio.skills.video.documentary_skill import DocumentarySkill
from modules.ai_video_studio.skills.video.educational_skill import EducationalSkill
from modules.ai_video_studio.skills.video.medical_skill import MedicalSkill
from modules.ai_video_studio.skills.video.tiktok_skill import TikTokSkill
from modules.ai_video_studio.skills.video.youtube_skill import YouTubeSkill

__all__ = [
    "AdvertisingSkill",
    "AgricultureSkill",
    "CinematicSkill",
    "CorporateSkill",
    "DocumentarySkill",
    "EducationalSkill",
    "MedicalSkill",
    "TikTokSkill",
    "YouTubeSkill",
]
