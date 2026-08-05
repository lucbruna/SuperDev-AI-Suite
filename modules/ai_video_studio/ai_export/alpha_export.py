"""Alpha export — outputs that preserve transparency (RGBA).

Videos with alpha require a codec that supports it (e.g. FFV1 in MOV, or
VP9 with alpha in WebM). Falls back to a PNG image sequence so the
information is never lost.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from modules.ai_video_studio.ai_export.image_sequence import export_image_sequence


def export_with_alpha(
    frames: list[np.ndarray],
    output_path: str | Path,
    *,
    fps: int = 30,
    codec: str = "ffv1",
) -> dict[str, Any]:
    """Export RGBA frames preserving the alpha channel.

    ``codec='ffv1'`` → lossless MOV with alpha. Any other value triggers
    the PNG sequence fallback (guaranteed alpha preservation).
    """
    import shutil

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    if codec == "ffv1" and shutil.which("ffmpeg"):
        import subprocess

        it = iter(frames)
        first = np.asarray(next(it), dtype=np.uint8)
        h, w = first.shape[:2]
        cmd = [
            "ffmpeg", "-y",
            "-f", "rawvideo", "-pix_fmt", "rgba",
            "-s", f"{w}x{h}", "-r", str(fps),
            "-i", "pipe:0",
            "-c:v", "ffv1", "-pix_fmt", "rgba",
            str(out),
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert proc.stdin is not None
        proc.stdin.write(first.tobytes())
        for frame in it:
            proc.stdin.write(np.asarray(frame, dtype=np.uint8).tobytes())
        proc.stdin.close()
        _, stderr = proc.communicate(timeout=600)
        if proc.returncode != 0:
            raise RuntimeError(f"alpha ffmpeg failed: {stderr.decode()[-800:]}")
        return {"output_path": str(out), "codec": "ffv1", "alpha": True, "engine": "ffmpeg"}

    # Fallback: PNG sequence with alpha
    seq_dir = out.with_suffix("")
    return {
        **export_image_sequence(frames, seq_dir, prefix="alpha", zfill=4),
        "alpha": True,
        "engine": "pillow",
    }
