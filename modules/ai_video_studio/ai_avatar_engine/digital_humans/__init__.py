"""Digital Humans — procedural generation of virtual presenters.

Generators produce deterministic parameter descriptors for every part of a
digital human: body, face, skin, eyes, brows, lashes, hair, beard, teeth,
tongue, hands, feet, clothing and accessories. The ``DigitalHumanEngine``
assembles them into a full character descriptor.
"""
from modules.ai_video_studio.ai_avatar_engine.digital_humans.digital_human_engine import (
    DigitalHumanEngine,
    get_digital_human_engine,
)

__all__ = ["DigitalHumanEngine", "get_digital_human_engine"]
