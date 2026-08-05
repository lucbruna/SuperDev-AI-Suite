"""Avatar profiles — shared data model for virtual presenters.

Every avatar in the engine is an :class:`AvatarProfile`: a frozen, validated
descriptor with identity, art style, dimension, gender, age group, voice
profile, wardrobe preference and generated appearance traits (skin, hair,
eyes, build). Profiles are the currency of the whole avatar engine — all
subsystems (digital humans, clothing, hairstyles, library, training) read
and write profiles.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from modules.ai_video_studio.core.constants import AvatarStyle, VoiceGender

VALID_STYLES = {s.value for s in AvatarStyle}
VALID_GENDERS = {g.value for g in VoiceGender}
VALID_DIMENSIONS = ("2d", "3d")
VALID_AGE_GROUPS = ("child", "young", "adult", "elderly")


@dataclass(frozen=True)
class AvatarProfile:
    """A complete, reusable virtual-presenter descriptor."""

    id: str
    name: str
    style: str = AvatarStyle.REALISTIC.value
    dimension: str = "3d"
    gender: str = VoiceGender.NEUTRAL.value
    age_group: str = "adult"
    voice: str = "default"
    default_outfit: str = "business"
    skin_tone: str = "#c68642"
    hair_color: str = "#2b2b2b"
    hair_style: str = "medium"
    eye_color: str = "#3a2a1a"
    build: str = "average"
    height_cm: int = 172
    description: str = ""
    tags: list[str] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id or not self.name:
            raise ValueError("avatar id and name are required")
        if self.style not in VALID_STYLES:
            raise ValueError(f"invalid style '{self.style}'")
        if self.dimension not in VALID_DIMENSIONS:
            raise ValueError(f"invalid dimension '{self.dimension}'")
        if self.gender not in VALID_GENDERS:
            raise ValueError(f"invalid gender '{self.gender}'")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "style": self.style,
            "dimension": self.dimension,
            "gender": self.gender,
            "age_group": self.age_group,
            "voice": self.voice,
            "default_outfit": self.default_outfit,
            "skin_tone": self.skin_tone,
            "hair_color": self.hair_color,
            "hair_style": self.hair_style,
            "eye_color": self.eye_color,
            "build": self.build,
            "height_cm": self.height_cm,
            "description": self.description,
            "tags": list(self.tags),
            "attributes": dict(self.attributes),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AvatarProfile:
        """Rebuild a profile from a serialized dict (tolerates missing keys)."""
        allowed = {f for f in cls.__dataclass_fields__}  # noqa: PIE793 — dataclass fields
        return cls(**{k: v for k, v in data.items() if k in allowed})


def profile_from_dict(data: dict[str, Any]) -> AvatarProfile:
    """Module-level convenience constructor (used by importers/registry)."""
    return AvatarProfile.from_dict(data)
