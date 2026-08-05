"""Asset generation — produce real placeholder assets.

* Textures/materials → real PNG files (procedural noise/checker/gradient).
* Sounds → real WAV files (tone, chord, noise) via numpy.

Files land in ``modules/downloads/assets/``.
"""
from __future__ import annotations

import time
from typing import Any

import numpy as np

from modules.ai_video_studio.media.audio import chord, silence, tone, white_noise, write_wav
from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename


def generate_texture(name: str, *, size: tuple[int, int] = (256, 256), kind: str = "noise", seed: int = 0) -> dict[str, Any]:
    """Generate a real PNG texture (noise, checker or gradient)."""
    from PIL import Image

    started = time.time()
    width, height = size
    rng = np.random.default_rng(seed)
    if kind == "checker":
        cell = 32
        arr = np.zeros((height, width, 3), dtype=np.uint8)
        for y in range(height):
            for x in range(width):
                if (x // cell + y // cell) % 2 == 0:
                    arr[y, x] = (90, 90, 110)
                else:
                    arr[y, x] = (200, 200, 220)
    elif kind == "gradient":
        t = np.linspace(0, 1, width, dtype=np.float32)[None, :, None]
        base = np.array([30, 60, 120], dtype=np.float32)
        arr = (base * (1 - t) + (255 - base) * t).astype(np.uint8)
        arr = np.repeat(arr, height, axis=0)
    else:  # noise
        base = rng.integers(40, 90, (height, width, 1), dtype=np.uint8)
        grain = rng.integers(0, 60, (height, width, 1), dtype=np.uint8)
        arr = np.clip(base.astype(np.int16) + grain, 0, 255).astype(np.uint8)
        arr = np.repeat(arr, 3, axis=2)

    out = unique_filename(get_subsystem_dir("assets"), f"texture_{name}", "png")
    Image.fromarray(arr).save(out, format="PNG")
    return {
        "kind": "texture",
        "name": name,
        "output_path": str(out),
        "output_bytes": out.stat().st_size,
        "width": width,
        "height": height,
        "elapsed_seconds": round(time.time() - started, 3),
    }


def generate_sound(name: str, *, kind: str = "tone", duration: float = 2.0, frequency: float = 440.0) -> dict[str, Any]:
    """Generate a real WAV sound (tone, chord, noise, silence)."""
    started = time.time()
    if kind == "tone":
        samples = tone(frequency, duration)
    elif kind == "chord":
        samples = chord([frequency, frequency * 1.25, frequency * 1.5], duration)
    elif kind == "noise":
        import zlib

        samples = white_noise(duration, seed=zlib.crc32(name.encode("utf-8")))
    else:
        samples = silence(duration)
    out = unique_filename(get_subsystem_dir("assets"), f"sound_{name}", "wav")
    write_wav(out, samples)
    return {
        "kind": "sound",
        "name": name,
        "output_path": str(out),
        "output_bytes": out.stat().st_size,
        "duration_seconds": duration,
        "elapsed_seconds": round(time.time() - started, 3),
    }
