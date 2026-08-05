"""Recruitment Videos — job posting and employer-brand videos."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration._brief import build_brief


class RecruitmentVideoGenerator:
    """Builds recruitment narration scripts for open roles."""

    def generate(self, *, role: str = "Software Engineer", company: str = "Acme",
                 location: str = "remote", voice: str = "default") -> dict[str, Any]:
        title = f"We are hiring — {role}"
        scenes = [
            f"{company} is hiring a {role} ({location}).",
            "Why join us: growth, culture and impact.",
            "What we expect: passion, collaboration and ownership.",
            "Apply today — the process takes less than a week.",
        ]
        return build_brief("human_resources", title, scenes, voice=voice,
                           role=role, company=company, location=location).to_dict()


_recruitment_video_generator: RecruitmentVideoGenerator | None = None


def get_recruitment_video_generator() -> RecruitmentVideoGenerator:
    global _recruitment_video_generator
    if _recruitment_video_generator is None:
        _recruitment_video_generator = RecruitmentVideoGenerator()
    return _recruitment_video_generator
