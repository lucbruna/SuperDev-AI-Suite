"""Export engine — core orchestrator for encoding frames to media files.

Uses the media toolkit's ffmpeg-backed encoders and exposes named
presets/profiles. Falls back to GIF when FFmpeg is missing.
"""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any, Callable, Iterable

import numpy as np

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.media.video import stream_frames_to_video, ffmpeg_available
from modules.ai_video_studio.ai_export.export_profiles import ExportProfile, get_profile
from modules.ai_video_studio.ai_export.export_presets import get_preset

logger = logging.getLogger(__name__)

ProgressFn = Callable[[float, int, int], None]


class ExportEngine:
    """Renders a frame sequence into a file for a named preset/profile."""

    def __init__(self, output_dir: str | Path | None = None) -> None:
        self._output_dir = Path(output_dir) if output_dir else Path.cwd() / "downloads"
        self._stats: dict[str, Any] = {}

    # ── Public API ─────────────────────────────────────────────
    def export_frames(
        self,
        frames: list[np.ndarray] | Iterable[np.ndarray],
        *,
        preset: str | None = None,
        profile: str | None = None,
        resolution: tuple[int, int] | None = None,
        fps: int | None = None,
        output_path: str | Path | None = None,
        progress: ProgressFn | None = None,
        codec_override: str | None = None,
    ) -> dict[str, Any]:
        """Export frames to a file. Either ``preset`` or ``profile`` must be given."""
        if preset:
            p = get_preset(preset)
            profile_obj, overrides = p.resolve()
        elif profile:
            profile_obj = get_profile(profile)
            overrides = {}
        else:
            raise ValidationError("export: preset or profile is required")

        if resolution is None:
            resolution = overrides.get("resolution") or profile_obj.max_resolution or (1920, 1080)
        if fps is None:
            fps = overrides.get("fps") or profile_obj.fps

        if output_path is None:
            ext = {
                "gif": "gif",
                "image2": "png",
                "matroska": "mkv",
                "avi": "avi",
                "webm": "webm",
                "mov": "mov",
            }.get(profile_obj.container, "mp4")
            output_path = self._output_dir / f"export_{int(time.time() * 1000)}.{ext}"
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        # Frame normalization + optional resolution resize
        def _norm(frame: np.ndarray) -> np.ndarray:
            arr = np.asarray(frame)
            if arr.dtype != np.uint8:
                arr = np.clip(arr, 0, 1) * 255 if arr.max() <= 1.0 else arr
                arr = arr.astype(np.uint8)
            if resolution and (arr.shape[1] != resolution[0] or arr.shape[0] != resolution[1]):
                arr = self._resize(arr, resolution)
            return arr

        frames_list = [_norm(f) for f in frames]
        if not frames_list:
            raise ValidationError("export: no frames to encode")

        codec = codec_override or profile_obj.video_codec
        started = time.time()
        total = len(frames_list)

        def _progress(done: int) -> None:
            if progress:
                progress(min(1.0, done / max(total, 1)), done, total)

        container = profile_obj.container
        if container == "gif":
            from modules.ai_video_studio.ai_export.gif_export import export_gif

            result = export_gif(frames_list, out, fps=fps, resolution=resolution)
            _progress(total)
        elif container == "image2":
            from modules.ai_video_studio.ai_export.image_sequence import export_image_sequence

            result = export_image_sequence(
                frames_list, out, prefix="frame", zfill=4, progress=progress
            )
        elif ffmpeg_available():
            result = stream_frames_to_video(
                iter(frames_list),
                out,
                fps=fps,
                codec=codec,
                crf=self._crf_for(profile_obj),
                preset=self._preset_for(profile_obj),
                total_frames=total,
            )
            _progress(total)
        else:
            from modules.ai_video_studio.media.video import _encode_gif  # type: ignore[attr-defined]

            result = _encode_gif(frames_list, out, fps=fps)
            if progress:
                progress(1.0, total, total)

        result.update(
            {
                "preset": preset,
                "profile": profile_obj.name,
                "resolution": resolution,
                "fps": fps,
                "container": profile_obj.container,
                "duration_s": round(len(frames_list) / max(fps, 1), 3),
                "elapsed_s": round(time.time() - started, 3),
            }
        )
        self._stats = result
        return result

    def probe(self, path: str | Path) -> dict[str, Any]:
        """Return basic metadata about an exported file (ffprobe-backed)."""
        import json
        import shutil
        import subprocess

        p = Path(path)
        if not p.exists():
            raise ValidationError(f"probe: file not found {p}")
        if shutil.which("ffprobe") is None:
            return {"path": str(p), "size_bytes": p.stat().st_size, "ffprobe": False}
        try:
            cmd = [
                "ffprobe", "-v", "error", "-print_format", "json",
                "-show_format", "-show_streams", str(p),
            ]
            raw = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            data = json.loads(raw.stdout)
            stream = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
            return {
                "path": str(p),
                "size_bytes": p.stat().st_size,
                "ffprobe": True,
                "codec": stream.get("codec_name"),
                "width": stream.get("width"),
                "height": stream.get("height"),
                "fps": stream.get("avg_frame_rate"),
                "duration_s": float(data.get("format", {}).get("duration", 0) or 0),
                "container": data.get("format", {}).get("format_name"),
            }
        except Exception as e:  # noqa: BLE001
            logger.warning("probe failed: %s", e)
            return {"path": str(p), "size_bytes": p.stat().st_size, "ffprobe": False, "error": str(e)}

    def stats(self) -> dict[str, Any]:
        return dict(self._stats)

    # ── Internals ──────────────────────────────────────────────
    @staticmethod
    def _crf_for(profile: ExportProfile) -> int:
        if profile.video_codec == "libx265":
            return 20
        if profile.video_codec in ("prores_ks", "dvvideo"):
            return 0
        return 18

    @staticmethod
    def _preset_for(_profile: ExportProfile) -> str:
        return "medium"

    @staticmethod
    def _resize(arr: np.ndarray, size: tuple[int, int]) -> np.ndarray:
        from PIL import Image

        w, h = size
        img = Image.fromarray(arr)
        img = img.resize((w, h), Image.LANCZOS)
        return np.asarray(img)


export_engine = ExportEngine()
