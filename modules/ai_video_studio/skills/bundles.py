"""Concrete skill bundles — register real, service-backed skills on the engine.

Each bundle class is registered as an *instance* entrypoint so the runtime
calls ``instance(**kwargs)`` → ``__call__``, letting concrete skills keep a
plain ``__init__`` and a clean async ``__call__`` signature.
"""
from __future__ import annotations
from typing import Any

from modules.ai_video_studio.skills.skill_loader import load
from modules.ai_video_studio.skills.skill_registry import SkillDefinition
from modules.ai_video_studio.skills.avatar import (
    DoctorSkill,
    EngineerSkill,
    FarmerSkill,
    LawyerSkill,
    PresenterSkill,
    SalespersonSkill,
    TeacherSkill,
)
from modules.ai_video_studio.skills.video import (
    CinematicSkill,
    TikTokSkill,
    YouTubeSkill,
)
from modules.ai_video_studio.skills.voice import (
    DubbingSkill,
    NarratorSkill,
    TranslatorSkill,
)

# All concrete skill classes shipped with the studio.
CONCRETE_SKILL_CLASSES: list[type] = [
    CinematicSkill,
    YouTubeSkill,
    TikTokSkill,
    NarratorSkill,
    DubbingSkill,
    TranslatorSkill,
    PresenterSkill,
    TeacherSkill,
    DoctorSkill,
    LawyerSkill,
    FarmerSkill,
    EngineerSkill,
    SalespersonSkill,
]


def _definition_with_instance(cls: type) -> SkillDefinition:
    """Build a definition whose entrypoint is a fresh instance of ``cls``."""
    definition = load(cls)
    return SkillDefinition(
        id=definition.id,
        name=definition.name,
        version=definition.version,
        description=definition.description,
        category=definition.category,
        entrypoint=cls(),
        permissions=definition.permissions,
        tags=definition.tags,
        metadata=definition.metadata,
    )


def register_all_concrete(
    engine: Any,
    *,
    categories: tuple[str, ...] | None = None,
) -> dict[str, bool]:
    """Register every concrete skill (optionally filtered by category) on ``engine``.

    Returns a mapping of ``skill_id -> registered``.
    """
    results: dict[str, bool] = {}
    for cls in CONCRETE_SKILL_CLASSES:
        category = getattr(cls, "skill_category", "general")
        if categories and category not in categories:
            continue
        engine.register(_definition_with_instance(cls))
        results[getattr(cls, "skill_id", cls.__name__.lower())] = True
    return results
