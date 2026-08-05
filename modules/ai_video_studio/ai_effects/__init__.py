"""AI Visual Effects — Volume 5 subsystem.

Effects operate on float frames in ``[0, 1]`` with shape ``(H, W, 3)`` and are
deterministic given a ``seed`` where randomness is involved.
"""
from __future__ import annotations

from .effects_engine import EffectsEngine, add_glow, draw_particles, make_fire_particles
from .effects_library import EffectsLibrary, get_effect, list_effects

__all__ = [
    "EffectsEngine",
    "EffectsLibrary",
    "get_effect",
    "list_effects",
    "add_glow",
    "draw_particles",
    "make_fire_particles",
    "engine",
    "library",
    "get_effects_engine",
]

engine = EffectsEngine()
library = EffectsLibrary()


def get_effects_engine() -> EffectsEngine:
    """Return the shared engine with all built-in effects registered."""
    from modules.ai_video_studio.ai_effects.effects_library import register_builtin_effects

    register_builtin_effects(engine)
    return engine
