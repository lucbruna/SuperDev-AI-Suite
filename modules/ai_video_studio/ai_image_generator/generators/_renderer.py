"""Shared real-PNG renderer for style generators.

Every style generator calls :func:`render` to turn its prompt into a real
PNG file under ``modules/downloads/images/`` and returns structured output
with the actual file path, size and dimensions.
"""
from __future__ import annotations

import time
import zlib
from typing import Any

from modules.ai_video_studio.media import style_scenes
from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename
from modules.ai_video_studio.media.render import render_still


def render(style: str, prompt: str, *, size: tuple[int, int] = (1024, 1024), seed: int | None = None) -> dict[str, Any]:
    """Render a real PNG for a style and prompt; return structured result."""
    width, height = size
    started = time.time()
    scene = style_scenes.scene_for_style(style, text=prompt)
    seed = seed if seed is not None else zlib.crc32(f"{style}:{prompt}".encode())
    out = unique_filename(get_subsystem_dir("images"), f"{style}", "png")
    path = render_still(scene, out, width=width, height=height, seed=seed)
    return {
        "style": style,
        "prompt": prompt,
        "width": width,
        "height": height,
        "output_path": str(path),
        "output_bytes": path.stat().st_size,
        "elapsed_seconds": round(time.time() - started, 3),
        "seed": seed,
        "status": "ok",
    }


def make_generator(style: str, default_size: tuple[int, int], default_model: str) -> Any:
    """Create a generator class factory bound to a style."""
    from typing import Any as _Any

    class _StyledGenerator:
        name = style

        def generate(self, prompt: str, *, size: tuple[int, int] | None = None, model: str | None = None, **params: _Any) -> dict[str, _Any]:
            target_size = size or (params.pop("size", None) or default_size)
            seed = params.get("seed")
            result = render(style, prompt, size=tuple(target_size), seed=seed)
            result["model"] = model or default_model
            result["sample_count"] = params.get("samples", 1)
            for key, value in params.items():
                if key not in result:
                    result[key] = value
            return result

    _StyledGenerator.__name__ = f"{style.capitalize()}Generator"
    _StyledGenerator.__qualname__ = _StyledGenerator.__name__
    _StyledGenerator.__doc__ = f"""Generates real {style} images via the media canvas."""
    return _StyledGenerator
