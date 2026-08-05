"""Effects Engine — generates real sound-effect audio files.

Each effect is synthesized with real DSP (noise, filters, FM, envelopes).
The engine looks up a generator by name, renders it, and writes a real file
under ``modules/downloads/effects/``.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable

import numpy as np

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.media import dsp
from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename
from modules.ai_video_studio.ai_sound_effects import (
    ambience_generator, rain_generator, thunder_generator, ocean_generator,
    forest_generator, city_generator, birds_generator, animals_generator,
    explosion_generator, footsteps_generator, vehicle_generator, machine_generator,
    crowd_generator, sports_generator, ui_sounds, transition_sounds,
)

logger = logging.getLogger(__name__)

# name → (generator, default duration seconds)
_REGISTRY: dict[str, tuple[Callable[..., np.ndarray], float]] = {
    "ambience": (ambience_generator.generate, 10.0),
    "rain": (rain_generator.generate, 8.0),
    "thunder": (thunder_generator.generate, 5.0),
    "ocean": (ocean_generator.generate, 10.0),
    "forest": (forest_generator.generate, 10.0),
    "city": (city_generator.generate, 10.0),
    "birds": (birds_generator.generate, 6.0),
    "animals": (animals_generator.generate, 5.0),
    "explosion": (explosion_generator.generate, 4.0),
    "footsteps": (footsteps_generator.generate, 4.0),
    "vehicle": (vehicle_generator.generate, 6.0),
    "machine": (machine_generator.generate, 6.0),
    "crowd": (crowd_generator.generate, 8.0),
    "sports": (sports_generator.generate, 6.0),
    "ui": (ui_sounds.generate, 0.5),
    "transition": (transition_sounds.generate, 2.0),
}

_EFFECTS = None


def get_effects_engine() -> EffectsEngine:
    global _EFFECTS
    if _EFFECTS is None:
        _EFFECTS = EffectsEngine()
    return _EFFECTS


class EffectsEngine:
    """Renders any registered sound effect to a real audio file."""

    def list_effects(self) -> list[str]:
        return sorted(_REGISTRY)

    def generate(self, effect: str, *, duration: float | None = None,
                 output_path: str | None = None, **params: Any) -> dict[str, Any]:
        name = effect.lower().strip()
        if name not in _REGISTRY:
            raise ValidationError(f"Unknown effect: {effect}", field="effect")
        generator, default_duration = _REGISTRY[name]
        duration = max(0.2, duration or default_duration)
        samples = generator(duration, **params)
        samples = dsp.normalize_peak(samples, 0.95)

        out_dir = Path(output_path).parent if output_path else get_subsystem_dir("effects")
        out_path = output_path or str(unique_filename(out_dir, f"sfx_{name}", "wav"))
        dsp.write_audio(out_path, samples)
        return {
            "output_path": out_path,
            "bytes": int(Path(out_path).stat().st_size),
            "duration": round(len(samples) / dsp.SAMPLE_RATE, 3),
            "effect": name,
        }
