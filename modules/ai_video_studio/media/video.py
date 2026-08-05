"""Video assembly — turn rendered frames into real video files.

Uses FFmpeg (already installed in the environment) to encode a frame
sequence into MP4/WebM. If FFmpeg is not available, falls back to writing an
animated GIF with Pillow so pipelines never fail.
"""
from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def frames_to_video(
    frames: list[np.ndarray] | list[Any],
    output_path: str | Path,
    *,
    fps: int = 24,
    codec: str = "libx264",
    crf: int = 23,
    preset: str = "medium",
    progress: bool = False,
) -> dict[str, Any]:
    """Encode a list of numpy frames into a real video file.

    For large frame counts use :func:`stream_frames_to_video`, which keeps
    memory constant instead of holding every frame. Returns
    ``{"output_path", "frames", "fps", "codec", "bytes", "engine"}``.
    """
    if not frames:
        raise ValueError("No frames to encode")
    if fps <= 0:
        raise ValueError("fps must be positive")

    if not ffmpeg_available():
        return _encode_gif(frames, output_path, fps=fps)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    def _iter() -> Any:
        for frame in frames:
            yield np.asarray(frame, dtype=np.uint8)

    return stream_frames_to_video(
        _iter(), output_path, fps=fps, codec=codec, crf=crf, preset=preset, total_frames=len(frames),
    )


def stream_frames_to_video(
    frame_iter: Any,
    output_path: str | Path,
    *,
    fps: int = 24,
    codec: str = "libx264",
    crf: int = 23,
    preset: str = "medium",
    total_frames: int | None = None,
    encode_timeout: float = 1800.0,
) -> dict[str, Any]:
    """Encode frames from an iterator, streaming raw RGB24 to FFmpeg stdin.

    Memory stays O(1) in the frame count — safe for long videos (e.g. 10
    minutes at 24 fps). Only the first frame is buffered (to learn the
    dimensions); every subsequent frame is written straight to FFmpeg.
    ``total_frames`` is optional and only used to report the count back; when
    omitted the real encoded count is returned. ``encode_timeout`` bounds how
    long FFmpeg may take (default 30 min — long 10-min encodes on CPU need it).
    """
    if fps <= 0:
        raise ValueError("fps must be positive")
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    if not ffmpeg_available():
        # GIF fallback needs all frames materialized (short videos only).
        return _encode_gif(list(frame_iter), output_path, fps=fps)

    # Buffer the first frame to learn the dimensions, then stream the rest.
    it = iter(frame_iter)
    try:
        first = np.asarray(next(it), dtype=np.uint8)
    except StopIteration:
        raise ValueError("No frames to encode") from None
    height, width = first.shape[:2]

    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{width}x{height}",
        "-r", str(fps),
        "-i", "pipe:0",
        "-c:v", codec,
        "-crf", str(crf),
        "-preset", preset,
        "-pix_fmt", "yuv420p",
        str(out),
    ]
    process = subprocess.Popen(
        cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    encoded = 0
    try:
        assert process.stdin is not None
        process.stdin.write(first.tobytes())
        encoded += 1
        for frame in it:
            arr = np.asarray(frame, dtype=np.uint8)
            if arr.shape[:2] != (height, width):
                raise ValueError(
                    f"All frames must share the same dimensions; got {(height, width)} and {arr.shape[:2]}"
                )
            process.stdin.write(arr.tobytes())
            encoded += 1
        process.stdin.close()
        _, stderr = process.communicate(timeout=encode_timeout)
        if process.returncode != 0:
            raise RuntimeError(f"FFmpeg encode failed: {stderr.decode()[-1000:]}")
    finally:
        # On any failure (generator error, mismatched frame, timeout) close
        # stdin and reap the child so we never leak a pipe or a zombie.
        if process.stdin is not None:
            try:
                process.stdin.close()
            except OSError:
                pass
        if process.poll() is None:
            process.kill()
            process.wait()

    return {
        "output_path": str(out),
        "frames": total_frames if total_frames is not None else encoded,
        "fps": fps,
        "codec": codec,
        "bytes": out.stat().st_size,
        "engine": "ffmpeg",
    }


def _encode_gif(frames: list[np.ndarray], output_path: str | Path, *, fps: int) -> dict[str, Any]:
    """Pillow-based animated GIF fallback (short videos only)."""
    if not frames:
        raise ValueError("No frames to encode")
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    gif_path = out.with_suffix(".gif")
    _write_gif(frames, gif_path, fps=fps)
    return {
        "output_path": str(gif_path),
        "frames": len(frames),
        "fps": fps,
        "codec": "gif",
        "bytes": gif_path.stat().st_size,
        "engine": "pillow-gif",
    }


def _write_gif(frames: list[np.ndarray], path: Path, *, fps: int) -> None:
    """Pillow-based animated GIF fallback."""
    from PIL import Image

    images = [Image.fromarray(np.asarray(f, dtype=np.uint8)) for f in frames]
    images[0].save(
        path,
        save_all=True,
        append_images=images[1:],
        duration=max(1, int(1000 / fps)),
        loop=0,
        optimize=False,
    )
