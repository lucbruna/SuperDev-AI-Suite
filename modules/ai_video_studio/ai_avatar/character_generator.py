"""Procedural character generation — unique virtual presenters on demand.

Given a seed, the generator deterministically produces a full character
spec: appearance (skin/hair/eyes), build, personality traits, wardrobe
preferences and a matching :class:`VirtualActor`. Two characters generated
with the same seed are identical; different seeds yield distinct people.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from modules.ai_video_studio.ai_avatar.actor_library import VirtualActor, get_actor_library
from modules.ai_video_studio.core.constants import AvatarStyle, VoiceGender

_STYLES = [s.value for s in AvatarStyle]
_GENDERS = [g.value for g in VoiceGender]
_AGE_GROUPS = ("young", "adult", "elderly")

_SKIN_TONES = ("#c68642", "#e8b48c", "#f0c8a0", "#8d5524", "#6b4226", "#ffd9a0", "#5a3a2a")
_HAIR_COLORS = ("#2b2b2b", "#3a2a1a", "#101010", "#8a4b2a", "#c9a2e0", "#e0c060", "#d8d8d8", "#c02020")
_EYE_COLORS = ("#3a2a1a", "#2a4a6a", "#4a7a3a", "#5a5a6a", "#8a6a3a")
_BUILDS = ("slim", "average", "athletic", "curvy", "tall")
_TRAITS = ("confident", "warm", "energetic", "calm", "curious", "authoritative",
           "playful", "serious", "friendly", "analytical")
_OCCASIONS = ("business", "casual", "formal", "tech", "sport", "minimal")


@dataclass
class CharacterSpec:
    """A procedurally generated character blueprint."""

    seed: int
    style: str
    dimension: str
    gender: str
    age_group: str
    name: str
    skin_tone: str
    hair_color: str
    eye_color: str
    build: str
    traits: list[str] = field(default_factory=list)
    preferred_occasions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "style": self.style,
            "dimension": self.dimension,
            "gender": self.gender,
            "age_group": self.age_group,
            "name": self.name,
            "skin_tone": self.skin_tone,
            "hair_color": self.hair_color,
            "eye_color": self.eye_color,
            "build": self.build,
            "traits": list(self.traits),
            "preferred_occasions": list(self.preferred_occasions),
        }

    def to_actor(self, actor_id: str | None = None) -> VirtualActor:
        """Convert the spec into a reusable :class:`VirtualActor`."""
        return VirtualActor(
            id=actor_id or f"gen_{self.seed}",
            name=self.name,
            style=self.style,
            dimension=self.dimension,
            gender=self.gender,
            age_group=self.age_group,
            voice=f"gen_{self.seed}_v",
            default_outfit=self.preferred_occasions[0] if self.preferred_occasions else "business",
            skin_tone=self.skin_tone,
            hair_color=self.hair_color,
            description=f"Procedurally generated {self.style} presenter (seed {self.seed})",
            tags=[self.build, self.style, "procedural"],
        )


# First names per gender for generated characters.
_NAMES_MALE = ("Aiden", "Elias", "Marco", "Theo", "Jules", "Owen", "Silas", "Rafael")
_NAMES_FEMALE = ("Aria", "Mira", "Sofia", "Nina", "Iris", "Lena", "Yara", "Clara")
_NAMES_NEUTRAL = ("Alex", "Riley", "Sam", "Jordan", "Casey", "Rowan", "Taylor", "Morgan")
_NAMES_LAST = ("Reed", "Vale", "Stone", "Reyes", "Nakamura", "Silva", "Keller", "Marsh")


class CharacterGenerator:
    """Deterministically generate unique characters from a seed."""

    def generate(
        self,
        seed: int,
        *,
        style: str | None = None,
        dimension: str | None = None,
        gender: str | None = None,
        age_group: str | None = None,
    ) -> CharacterSpec:
        """Build a full character spec. Same seed → same character."""
        rng = random.Random(seed)

        style = style if style in _STYLES else rng.choice(_STYLES)
        dimension = dimension if dimension in ("2d", "3d") else ("3d" if style in
                                                                 (AvatarStyle.REALISTIC.value, AvatarStyle.THREE_D.value) else "2d")
        gender = gender if gender in _GENDERS else rng.choice(_GENDERS)
        age_group = age_group if age_group in _AGE_GROUPS else rng.choice(_AGE_GROUPS)

        first_pool = _NAMES_MALE if gender == VoiceGender.MALE.value else (
            _NAMES_FEMALE if gender == VoiceGender.FEMALE.value else _NAMES_NEUTRAL
        )
        name = f"{rng.choice(first_pool)} {rng.choice(_NAMES_LAST)}"

        trait_pool = list(_TRAITS)
        rng.shuffle(trait_pool)
        traits = trait_pool[:3]
        occasions = list(_OCCASIONS)
        rng.shuffle(occasions)

        return CharacterSpec(
            seed=seed,
            style=style,
            dimension=dimension,
            gender=gender,
            age_group=age_group,
            name=name,
            skin_tone=rng.choice(_SKIN_TONES),
            hair_color=rng.choice(_HAIR_COLORS),
            eye_color=rng.choice(_EYE_COLORS),
            build=rng.choice(_BUILDS),
            traits=traits,
            preferred_occasions=occasions[:2],
        )

    def generate_actor(self, seed: int, **kw: Any) -> VirtualActor:
        """Generate a character and register it as a reusable actor.

        The actor is only registered once per seed; repeated calls return the
        existing (identical) actor.
        """
        spec = self.generate(seed, **kw)
        actor = spec.to_actor()
        library = get_actor_library()
        library.add(actor)
        return actor


_character_generator: CharacterGenerator | None = None


def get_character_generator() -> CharacterGenerator:
    """Return the shared character generator singleton."""
    global _character_generator
    if _character_generator is None:
        _character_generator = CharacterGenerator()
    return _character_generator
