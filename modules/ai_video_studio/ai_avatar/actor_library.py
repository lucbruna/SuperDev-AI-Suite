"""Virtual actor library — 2D and 3D digital humans (blueprint Volume 6).

Every avatar in the library is a :class:`VirtualActor`: a reusable virtual
presenter with a style (realistic / anime / cartoon / pixel_art / 3d /
minimalist), a dimension (2d | 3d), gender, age group, voice profile,
default wardrobe and scene-tagging so the engine can pick the best actor
for a given scene type automatically.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from modules.ai_video_studio.core.constants import AvatarStyle, VoiceGender


@dataclass(frozen=True)
class VirtualActor:
    """A reusable digital-human presenter."""

    id: str
    name: str
    style: str  # one of AvatarStyle values
    dimension: str  # "2d" | "3d"
    gender: str  # one of VoiceGender values
    age_group: str  # young | adult | elderly
    voice: str = "default"  # voice profile id used by the voice studio
    default_outfit: str = "business"  # wardrobe occasion
    skin_tone: str = "#c68642"
    hair_color: str = "#2b2b2b"
    description: str = ""
    tags: list[str] = field(default_factory=list)

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
            "description": self.description,
            "tags": list(self.tags),
        }


# ── The virtual actor library ────────────────────────────────────
ACTOR_LIBRARY: list[VirtualActor] = [
    # 3D / realistic digital humans
    VirtualActor("maya", "Maya Chen", AvatarStyle.REALISTIC.value, "3d", VoiceGender.FEMALE.value, "adult",
                 voice="maya_f", default_outfit="business", skin_tone="#e8b48c", hair_color="#1a1a1a",
                 description="Confident host for corporate and tech content", tags=["host", "corporate", "3d"]),
    VirtualActor("noah", "Noah Rivers", AvatarStyle.REALISTIC.value, "3d", VoiceGender.MALE.value, "adult",
                 voice="noah_m", default_outfit="formal", skin_tone="#c68642", hair_color="#3a2a1a",
                 description="Warm narrator for documentary and news", tags=["narrator", "documentary", "3d"]),
    VirtualActor("nova", "Nova 3D", AvatarStyle.THREE_D.value, "3d", VoiceGender.FEMALE.value, "adult",
                 voice="nova_f", default_outfit="tech", skin_tone="#d9b18c", hair_color="#4a3b8a",
                 description="Futuristic 3D digital human for product demos", tags=["product", "futuristic", "3d"]),
    VirtualActor("eve", "Eve", AvatarStyle.REALISTIC.value, "3d", VoiceGender.FEMALE.value, "young",
                 voice="eve_f", default_outfit="casual", skin_tone="#f0c8a0", hair_color="#8a4b2a",
                 description="Energetic lifestyle and social content host", tags=["lifestyle", "social", "3d"]),
    # 2D / stylized avatars
    VirtualActor("luna", "Luna", AvatarStyle.ANIME.value, "2d", VoiceGender.FEMALE.value, "young",
                 voice="luna_f", default_outfit="casual", skin_tone="#ffe3c9", hair_color="#c9a2e0",
                 description="Energetic anime presenter for gaming and youth content", tags=["gaming", "youth", "2d"]),
    VirtualActor("rex", "Rex", AvatarStyle.CARTOON.value, "2d", VoiceGender.MALE.value, "young",
                 voice="rex_m", default_outfit="casual", skin_tone="#ffd9a0", hair_color="#5a3a1a",
                 description="Playful cartoon character for explainers", tags=["explainer", "kids", "2d"]),
    VirtualActor("pixel", "Pixel", AvatarStyle.PIXEL_ART.value, "2d", VoiceGender.NEUTRAL.value, "adult",
                 voice="pixel_n", default_outfit="tech", skin_tone="#b8a0d0", hair_color="#202040",
                 description="Retro pixel presenter for indie and game content", tags=["retro", "game", "2d"]),
    VirtualActor("min", "Min", AvatarStyle.MINIMALIST.value, "2d", VoiceGender.NEUTRAL.value, "adult",
                 voice="min_n", default_outfit="minimal", skin_tone="#d8d8d8", hair_color="#404040",
                 description="Clean minimalist presenter for slides and summaries", tags=["minimal", "slides", "2d"]),
    VirtualActor("tia", "Tia", AvatarStyle.ANIME.value, "2d", VoiceGender.FEMALE.value, "elderly",
                 voice="tia_f", default_outfit="formal", skin_tone="#f2c9a4", hair_color="#d8d8d8",
                 description="Wise narrator for stories and history content", tags=["story", "history", "2d"]),
    VirtualActor("kai", "Kai", AvatarStyle.THREE_D.value, "3d", VoiceGender.MALE.value, "adult",
                 voice="kai_m", default_outfit="sport", skin_tone="#c07a3a", hair_color="#101010",
                 description="Dynamic presenter for sports and fitness content", tags=["sports", "fitness", "3d"]),
]


class ActorLibrary:
    """Query / filter the virtual actor library."""

    def __init__(self, actors: list[VirtualActor] | None = None) -> None:
        self._actors = list(actors if actors is not None else ACTOR_LIBRARY)

    def list(self, *, style: str | None = None, dimension: str | None = None,
             gender: str | None = None, scene_type: str | None = None) -> list[dict[str, Any]]:
        """List actors, optionally filtered by style/dimension/gender/tags."""
        candidates = list(self._actors)
        if style:
            candidates = [a for a in candidates if a.style == style]
        if dimension:
            candidates = [a for a in candidates if a.dimension == dimension]
        if gender:
            candidates = [a for a in candidates if a.gender == gender]
        if scene_type:
            pref = _SCENE_ACTOR_PREF.get(scene_type)
            if pref:
                pref_actor = next((a for a in candidates if a.id in pref), None)
                if pref_actor:
                    return [pref_actor.to_dict()]
        return [a.to_dict() for a in candidates]

    def get(self, actor_id: str) -> VirtualActor:
        for a in self._actors:
            if a.id == actor_id:
                return a
        raise KeyError(f"unknown actor '{actor_id}'")

    def add(self, actor: VirtualActor) -> bool:
        """Register an actor if its id is not already present.

        Returns ``True`` when a new actor was added, ``False`` when an actor
        with the same id already exists (no-op).
        """
        if any(a.id == actor.id for a in self._actors):
            return False
        self._actors.append(actor)
        return True

    def select_for_scene(self, scene_type: str = "content", *, style: str | None = None,
                         gender: str | None = None) -> VirtualActor:
        """Pick the best-matching actor for a scene (falls back gracefully)."""
        candidates = [a for a in self._actors if a.style == style] if style else list(self._actors)
        if not candidates:
            candidates = list(self._actors)
        if gender:
            gendered = [a for a in candidates if a.gender == gender]
            if gendered:
                candidates = gendered
        for aid in _SCENE_ACTOR_PREF.get(scene_type, []):
            match = next((a for a in candidates if a.id == aid), None)
            if match:
                return match
        return candidates[0]


_SCENE_ACTOR_PREF: dict[str, tuple[str, ...]] = {
    "intro": ("maya", "eve", "luna"),
    "title_card": ("nova", "pixel", "min"),
    "outro": ("maya", "tia", "min"),
    "b_roll": ("min", "pixel", "rex"),
    "content": ("noah", "kai", "eve"),
    "highlight": ("kai", "luna", "rex"),
    "credits": ("min", "tia", "pixel"),
}


_actor_library: ActorLibrary | None = None


def get_actor_library() -> ActorLibrary:
    """Return the shared actor library singleton."""
    global _actor_library
    if _actor_library is None:
        _actor_library = ActorLibrary()
    return _actor_library
