"""Effects library — registers every built-in effect into an EffectsEngine.

Each effect module exposes an ``apply(frame, params)`` callable; this module
imports them and wires them into the engine's registry with metadata so a UI
can list available effects and their parameters.
"""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.ai_effects import (
    lens_flare, glow, bloom, depth_of_field, motion_blur, speed_ramp,
    film_grain, vignette, sharpen, denoise, chromatic_aberration,
    rain_effect, snow_effect, smoke_effect, fire_effect,
    dust_particles, sparks, explosions, cinematic_effects,
)

_BUILTINS: list[tuple[str, Any, dict[str, Any]]] = [
    ("lens_flare", lens_flare.apply, {"category": "light"}),
    ("glow", glow.apply, {"category": "light"}),
    ("bloom", bloom.apply, {"category": "light"}),
    ("depth_of_field", depth_of_field.apply, {"category": "camera"}),
    ("motion_blur", motion_blur.apply, {"category": "camera"}),
    ("speed_ramp", speed_ramp.apply, {"category": "time"}),
    ("film_grain", film_grain.apply, {"category": "stylize"}),
    ("vignette", vignette.apply, {"category": "stylize"}),
    ("sharpen", sharpen.apply, {"category": "enhance"}),
    ("denoise", denoise.apply, {"category": "enhance"}),
    ("chromatic_aberration", chromatic_aberration.apply, {"category": "distort"}),
    ("rain", rain_effect.apply, {"category": "weather", "params": {"intensity": 0.5, "angle": 0.15}}),
    ("snow", snow_effect.apply, {"category": "weather", "params": {"intensity": 0.5}}),
    ("smoke", smoke_effect.apply, {"category": "weather", "params": {"density": 0.4}}),
    ("fire", fire_effect.apply, {"category": "pyro", "params": {"intensity": 0.5}}),
    ("dust", dust_particles.apply, {"category": "pyro", "params": {"count": 120}}),
    ("sparks", sparks.apply, {"category": "pyro", "params": {"count": 80}}),
    ("explosion", explosions.apply, {"category": "pyro", "params": {"radius": 60}}),
    ("letterbox", cinematic_effects.letterbox, {"category": "cinematic", "params": {"bars": 0.1}}),
    ("film_look", cinematic_effects.film_look, {"category": "cinematic", "params": {"grain": 0.06, "contrast": 0.1}}),
]


def register_builtin_effects(engine: Any) -> int:
    """Register all built-in effects; returns how many were added."""
    count = 0
    for name, fn, meta in _BUILTINS:
        if not engine.registry.has(name):
            engine.register(name, fn, **meta)
            count += 1
    return count


def builtin_names() -> list[str]:
    return [name for name, _, _ in _BUILTINS]


class EffectsLibrary:
    """A ready-to-use effects engine with all built-in effects registered."""

    def __init__(self) -> None:
        from modules.ai_video_studio.ai_effects.effects_engine import EffectsEngine

        self.engine = EffectsEngine()
        register_builtin_effects(self.engine)
        self.registry = self.engine.registry

    def apply(self, name: str, frame: Any, params: dict[str, Any] | None = None) -> Any:
        return self.engine.apply(name, frame, params)

    def apply_chain(self, frame: Any, effects: list[dict[str, Any]]) -> Any:
        return self.engine.apply_chain(frame, effects)

    def names(self) -> list[str]:
        return self.registry.names()

    def describe(self, name: str) -> dict[str, Any]:
        return self.registry.meta(name)

    def has(self, name: str) -> bool:
        return self.registry.has(name)

    def __len__(self) -> int:
        return len(self.registry)


def get_effect(name: str) -> Any:
    """Return the registered effect callable for ``name``."""
    from modules.ai_video_studio.ai_effects.effects_engine import get_effects_engine

    return get_effects_engine().registry.get(name)


def list_effects() -> list[str]:
    """Return the names of all registered effects."""
    from modules.ai_video_studio.ai_effects.effects_engine import get_effects_engine

    return get_effects_engine().registry.names()
