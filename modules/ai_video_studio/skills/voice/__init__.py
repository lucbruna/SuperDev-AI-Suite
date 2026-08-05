"""Voice skills bundle — concrete skills backed by real studio services."""
from __future__ import annotations

from modules.ai_video_studio.skills.voice.audiobook_skill import AudiobookSkill
from modules.ai_video_studio.skills.voice.dubbing_skill import DubbingSkill
from modules.ai_video_studio.skills.voice.interview_skill import InterviewSkill
from modules.ai_video_studio.skills.voice.narrator_skill import NarratorSkill
from modules.ai_video_studio.skills.voice.podcast_skill import PodcastSkill
from modules.ai_video_studio.skills.voice.storyteller_skill import StorytellerSkill
from modules.ai_video_studio.skills.voice.translator_skill import TranslatorSkill

__all__ = [
    "AudiobookSkill",
    "DubbingSkill",
    "InterviewSkill",
    "NarratorSkill",
    "PodcastSkill",
    "StorytellerSkill",
    "TranslatorSkill",
]
