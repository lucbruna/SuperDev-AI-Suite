"""Image sequence export — write frames as PNG files to a directory."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np


def export_image_sequence(
    frames: list[np.ndarray],
    output_dir: str | Path,
    *,
    prefix: str = "frame",
    zfill: int = 4,
    fmt: str = "png",
    resolution: tuple[int, int] | None = None,
    progress=None,
) -> dict[str, Any]:
    """Write each frame as an image file: ``<output_dir>/<prefix>_0001.png``."""
    if not frames:
        raise ValueError("export_image_sequence: no frames provided")
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    from PIL import Image

    written: list[str] = []
    total = len(frames)
    for i, frame in enumerate(frames):
        arr = np.asarray(frame, dtype=np.uint8)
        if resolution and (arr.shape[1] != resolution[0] or arr.shape[0] != resolution[1]):
            arr = np.asarray(Image.fromarray(arr).resize(resolution, Image.LANCZOS))
        img = Image.fromarray(arr)
        path = out_dir / f"{prefix}_{str(i + 1).zfill(zfill)}.{fmt}"
        img.save(path, format=fmt.upper())
        written.append(str(path))
        if progress:
            progress(min(1.0, (i + 1) / total), i + 1, total)

    return {
        "output_dir": str(out_dir),
        "frames": len(written),
        "files": written,
        "format": fmt,
        "engine": "pillow",
    }
