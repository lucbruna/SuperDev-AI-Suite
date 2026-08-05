"""GIF export — animated GIF (Pillow-backed, always works without FFmpeg)."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np


def export_gif(
    frames: list[np.ndarray],
    output_path: str | Path,
    *,
    fps: int = 15,
    resolution: tuple[int, int] | None = None,
    loop: int = 0,
    optimize: bool = True,
) -> dict[str, Any]:
    """Write an animated GIF from frames using Pillow."""
    from PIL import Image

    if not frames:
        raise ValueError("export_gif: no frames provided")
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    imgs: list[Image.Image] = []
    for frame in frames:
        arr = np.asarray(frame, dtype=np.uint8)
        if resolution and (arr.shape[1] != resolution[0] or arr.shape[0] != resolution[1]):
            arr = np.asarray(Image.fromarray(arr).resize(resolution, Image.LANCZOS))
        if arr.shape[2] == 4:
            imgs.append(Image.fromarray(arr, "RGBA"))
        else:
            imgs.append(Image.fromarray(arr).convert("RGB"))

    duration_ms = max(1, int(1000 / max(fps, 1)))
    imgs[0].save(
        out,
        save_all=True,
        append_images=imgs[1:],
        duration=duration_ms,
        loop=loop,
        optimize=optimize,
    )
    return {
        "output_path": str(out),
        "frames": len(imgs),
        "fps": fps,
        "codec": "gif",
        "bytes": out.stat().st_size,
        "engine": "pillow",
    }
