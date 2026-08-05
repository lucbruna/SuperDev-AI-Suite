"""Video briefs — the standard unit every domain connector produces.

A ``VideoBrief`` is a JSON-serializable description of a video the studio
can generate: title, per-scene narration script, style, voice profile,
language, duration and domain metadata. Connectors build briefs via
:func:`build_brief`; downstream studio pipelines (AI Studio, Voice Studio,
Avatar Engine, Export) consume ``to_dict()``.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class VideoBrief:
    """A renderable video description produced by a domain connector."""

    domain: str
    title: str
    script: tuple[str, ...] = ()
    style: str = "corporate"
    voice: str = "default"
    language: str = "en"
    duration: float = 10.0
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def narration(self) -> str:
        return " ".join(self.script)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "video_brief",
            "domain": self.domain,
            "title": self.title,
            "script": list(self.script),
            "narration": self.narration,
            "style": self.style,
            "voice": self.voice,
            "language": self.language,
            "duration": round(float(self.duration), 2),
            "scenes": len(self.script),
            "meta": dict(self.meta),
        }


def build_brief(
    domain: str,
    title: str,
    scenes: list[str],
    *,
    style: str = "corporate",
    voice: str = "default",
    language: str = "en",
    seconds_per_scene: float = 4.0,
    **meta: Any,
) -> VideoBrief:
    """Build a brief from per-scene narration lines (≥1 scene)."""
    scenes = [s for s in scenes if s and s.strip()]
    if not scenes:
        scenes = [title]
    return VideoBrief(
        domain=domain,
        title=title,
        script=tuple(scenes),
        style=style,
        voice=voice,
        language=language,
        duration=len(scenes) * seconds_per_scene,
        meta=meta,
    )
