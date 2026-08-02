"""Create skill — one-shot skill scaffolding and loading.

Generates a skill module, imports it dynamically and returns a ready-to-run
``SkillDefinition`` (entrypoint bound to a fresh instance), matching how the
``bundles`` module registers concrete skills.
"""
from __future__ import annotations
import importlib.util
import os
import tempfile
from typing import Any

from modules.ai_video_studio.skills.sdk.skill_generator import generate_skill_file
from modules.ai_video_studio.skills.skill_registry import SkillDefinition


def _load_class_from_file(path: str, class_name: str) -> type:
    spec = importlib.util.spec_from_file_location(f"_generated_{class_name}", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load generated skill from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cls = getattr(module, class_name)
    if not isinstance(cls, type):
        raise TypeError(f"{class_name} in {path} is not a class")
    return cls


def create_skill(
    *,
    skill_id: str,
    name: str,
    category: str = "general",
    description: str = "",
    output_dir: str | None = None,
    version: str = "1.0.0",
    tags: list[str] | None = None,
    permissions: list[str] | None = None,
) -> dict[str, Any]:
    """Scaffold a skill module and return ``{"file_path", "definition"}``."""
    output_dir = output_dir or os.path.join(tempfile.gettempdir(), "avs_skill_sdk")
    file_path = generate_skill_file(
        skill_id=skill_id,
        name=name,
        output_dir=output_dir,
        version=version,
        category=category,
        description=description,
        tags=tags,
        permissions=permissions,
    )
    cls = _load_class_from_file(file_path, f"{name.replace(' ', '')}Skill")
    definition = SkillDefinition(
        id=skill_id,
        name=name,
        version=version,
        description=description,
        category=category,
        entrypoint=cls(),
        permissions=permissions or [],
        tags=tags or [],
        metadata={},
    )
    return {"file_path": file_path, "definition": definition}
