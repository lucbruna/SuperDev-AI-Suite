"""Digital Human Engine — assembles a full digital-human descriptor.

The engine calls every feature generator (body, face, skin, eyes, brows,
lashes, hair, beard, teeth, tongue, hands, feet, clothing, accessories)
and composes a complete, deterministic character descriptor for a profile.
"""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile
from modules.ai_video_studio.ai_avatar_engine.digital_humans.accessories_generator import (
    get_accessories_generator,
)
from modules.ai_video_studio.ai_avatar_engine.digital_humans.age_variations import (
    get_age_variations,
)
from modules.ai_video_studio.ai_avatar_engine.digital_humans.beard_generator import (
    get_beard_generator,
)
from modules.ai_video_studio.ai_avatar_engine.digital_humans.body_generator import (
    get_body_generator,
)
from modules.ai_video_studio.ai_avatar_engine.digital_humans.clothing_generator import (
    get_clothing_generator,
)
from modules.ai_video_studio.ai_avatar_engine.digital_humans.eye_generator import (
    get_eye_generator,
)
from modules.ai_video_studio.ai_avatar_engine.digital_humans.eyebrow_generator import (
    get_eyebrow_generator,
)
from modules.ai_video_studio.ai_avatar_engine.digital_humans.eyelash_generator import (
    get_eyelash_generator,
)
from modules.ai_video_studio.ai_avatar_engine.digital_humans.face_generator import (
    get_face_generator,
)
from modules.ai_video_studio.ai_avatar_engine.digital_humans.feet_generator import (
    get_feet_generator,
)
from modules.ai_video_studio.ai_avatar_engine.digital_humans.hair_generator import (
    get_hair_generator,
)
from modules.ai_video_studio.ai_avatar_engine.digital_humans.hand_generator import (
    get_hand_generator,
)
from modules.ai_video_studio.ai_avatar_engine.digital_humans.skin_generator import (
    get_skin_generator,
)
from modules.ai_video_studio.ai_avatar_engine.digital_humans.teeth_generator import (
    get_teeth_generator,
)
from modules.ai_video_studio.ai_avatar_engine.digital_humans.tongue_generator import (
    get_tongue_generator,
)


class DigitalHumanEngine:
    """Composes all feature generators into one digital-human descriptor."""

    def generate(self, profile: AvatarProfile, *, settings: dict[str, Any] | None = None,
                 seed: int | None = None) -> dict[str, Any]:
        """Return a complete digital-human descriptor for ``profile``."""
        seed = seed if seed is not None else hash(profile.id) % 100000
        body = get_body_generator().generate(
            build=profile.build, height_cm=profile.height_cm, age_group=profile.age_group, seed=seed)
        face = get_face_generator().generate(age_group=profile.age_group, seed=seed)
        skin = get_skin_generator().generate(tone=_tone_from_hex(profile.skin_tone), seed=seed)
        eyes = get_eye_generator().generate(color=profile.eye_color, seed=seed)
        brows = get_eyebrow_generator().generate(hair_color=profile.hair_color, seed=seed)
        lashes = get_eyelash_generator().generate(seed=seed, gender=profile.gender)
        hair = get_hair_generator().generate(color=profile.hair_color, style=profile.hair_style, seed=seed)
        beard = get_beard_generator().generate(color=profile.hair_color, seed=seed)
        teeth = get_teeth_generator().generate(seed=seed)
        tongue = get_tongue_generator().generate(seed=seed)
        hands = get_hand_generator().generate(seed=seed)
        feet = get_feet_generator().generate(height_cm=profile.height_cm, seed=seed)
        clothing = get_clothing_generator().generate(outfit=profile.default_outfit, body=body, seed=seed)
        accessories = get_accessories_generator().generate(outfit=profile.default_outfit, seed=seed)
        age = get_age_variations().get(profile.age_group)

        return {
            "status": "generated",
            "identity": {"id": profile.id, "name": profile.name, "style": profile.style,
                         "dimension": profile.dimension},
            "body": body,
            "face": face,
            "skin": skin,
            "eyes": eyes,
            "eyebrows": brows,
            "eyelashes": lashes,
            "hair": hair,
            "beard": beard,
            "teeth": teeth,
            "tongue": tongue,
            "hands": hands,
            "feet": feet,
            "clothing": clothing,
            "accessories": accessories,
            "age_variations": age,
            "seed": seed,
        }

    def summary(self, profile: AvatarProfile, **kw: Any) -> dict[str, Any]:
        """Compact human-readable summary of a generated human."""
        generated = self.generate(profile, **kw)
        return {
            "profile": profile.id,
            "style": profile.style,
            "dimension": profile.dimension,
            "build": generated["body"]["build"],
            "height_cm": generated["body"]["height_cm"],
            "skin": generated["skin"]["hex"],
            "hair": generated["hair"]["style"],
            "eyes": generated["eyes"]["iris_color"],
            "outfit": generated["clothing"]["outfit"],
        }


def _tone_from_hex(hex_color: str) -> str | None:
    """Best-effort reverse lookup of a hex color to a tone name."""
    from modules.ai_video_studio.ai_avatar_engine.digital_humans.skin_generator import (
        _SKIN_TONES,
        get_skin_generator,
    )

    lowered = hex_color.lower()
    for tone, tone_hex in _SKIN_TONES.items():
        if lowered == tone_hex.lower() or lowered == "#" + tone_hex.lstrip("#").lower():
            return tone
    return get_skin_generator().tones()[0]


_digital_human_engine: DigitalHumanEngine | None = None


def get_digital_human_engine() -> DigitalHumanEngine:
    """Return the shared digital-human engine singleton."""
    global _digital_human_engine
    if _digital_human_engine is None:
        _digital_human_engine = DigitalHumanEngine()
    return _digital_human_engine
