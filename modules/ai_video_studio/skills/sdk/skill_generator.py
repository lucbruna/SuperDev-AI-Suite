"""Skill generator — writes skill modules to disk from metadata."""
from __future__ import annotations
import os

from modules.ai_video_studio.skills.sdk.skill_template import skill_template


def generate_skill_file(
    *,
    skill_id: str,
    name: str,
    output_dir: str,
    version: str = "1.0.0",
    category: str = "general",
    description: str = "",
    tags: list[str] | None = None,
    permissions: list[str] | None = None,
    entrypoint_body: str | None = None,
) -> str:
    """Write a skill module to ``output_dir`` and return its file path."""
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"{skill_id}_skill.py")
    source = skill_template(
        skill_id=skill_id,
        name=name,
        version=version,
        category=category,
        description=description,
        tags=tags,
        permissions=permissions,
        entrypoint_body=entrypoint_body,
    )
    with open(path, "w", encoding="utf-8") as f:
        f.write(source)
    return path
