"""Instruments — real synthesisers for the music generator.

Each instrument exposes ``render(name, frequency, duration_s, *, amplitude,
sample_rate) -> np.ndarray``. The registry lets the engine address them by
string (``"piano"``, ``"drums"``, ...).
"""
from __future__ import annotations

from typing import Callable

import numpy as np

from modules.ai_video_studio.ai_music_generator.instruments import (
    piano,
    violin,
    guitar,
    bass,
    drums,
    flute,
    trumpet,
    cello,
    choir,
    synthesizer,
)

_REGISTRY: dict[str, Callable[..., np.ndarray]] = {
    "piano": piano.render,
    "violin": violin.render,
    "guitar": guitar.render,
    "bass": bass.render,
    "drums": drums.render,
    "flute": flute.render,
    "trumpet": trumpet.render,
    "cello": cello.render,
    "choir": choir.render,
    "synthesizer": synthesizer.render,
    "synth": synthesizer.render,
    "fiddle": violin.render,      # alias used by country
    "organ": synthesizer.render,  # alias used by gospel
}


def get_instrument(name: str) -> Callable[..., np.ndarray]:
    return _REGISTRY.get(name, piano.render)


def available_instruments() -> list[str]:
    return sorted(_REGISTRY)
