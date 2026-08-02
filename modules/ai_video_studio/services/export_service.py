"""Export Service — multi-format video export (blueprint Volume 10, export pillar).

Takes a rendered video and produces distribution-ready files: MP4 (H.264/AAC),
WebM (VP9/Opus), MOV, and an animated GIF preview. Reuses the render engine's
FFmpeg pipeline so every export is a real transcode, not a stub.
"""
from __future__ import annotations
import asyncio
import logging
import os
import tempfile
from typing import Any

from modules.ai_video_studio.core.exceptions import ExportFormatError
from modules.ai_video_studio.render_engine import RenderEngine

logger = logging.getLogger(__name__)

# Format catalog: container/codecs used by RenderEngine.transcode; GIF uses a
# dedicated two-pass palette pipeline instead of the generic transcode path.
EXPORT_FORMATS: dict[str, dict[str, Any]] = {
    "mp4": {
        "container": "mp4",
        "video_codec": "libx264",
        "audio_codec": "aac",
        "extension": ".mp4",
        "description": "H.264/AAC — universal compatibility (recommended)",
    },
    "webm": {
        "container": "webm",
        "video_codec": "libvpx-vp9",
        "audio_codec": "libopus",
        "extension": ".webm",
        "description": "VP9/Opus — efficient web streaming",
    },
    "mov": {
        "container": "mov",
        "video_codec": "libx264",
        "audio_codec": "aac",
        "extension": ".mov",
        "description": "QuickTime MOV — editing interchange",
    },
    "gif": {
        "container": "gif",
        "video_codec": None,
        "audio_codec": None,
        "extension": ".gif",
        "palette": True,
        "description": "Animated GIF preview (no audio)",
    },
}


class ExportService:
    """Exports rendered videos into multiple distribution formats."""

    def __init__(self, output_dir: str | None = None) -> None:
        self.output_dir = output_dir or os.path.join(tempfile.gettempdir(), "avs_export")
        self._engine = RenderEngine()

    def list_formats(self) -> list[dict[str, Any]]:
        return [
            {"id": fmt_id, **meta}
            for fmt_id, meta in EXPORT_FORMATS.items()
        ]

    def _out_path(self, input_path: str, fmt_id: str) -> str:
        stem = os.path.splitext(os.path.basename(input_path))[0]
        return os.path.join(self.output_dir, f"{stem}_{fmt_id}{EXPORT_FORMATS[fmt_id]['extension']}")

    async def export(
        self,
        input_path: str,
        fmt_id: str = "mp4",
        *,
        output_path: str | None = None,
        scale: str | None = None,
    ) -> dict[str, Any]:
        """Export ``input_path`` to the given format.

        Returns ``{"file_path", "format", "container", "file_size_bytes",
        "duration", "success"}``. Raises ``ExportFormatError`` for unknown
        formats and ``RuntimeError`` if the transcode fails.
        """
        fmt_id = fmt_id.lower()
        fmt = EXPORT_FORMATS.get(fmt_id)
        if fmt is None:
            raise ExportFormatError(
                fmt_id, f"unsupported format (available: {', '.join(EXPORT_FORMATS)})"
            )
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input video not found: {input_path}")

        os.makedirs(self.output_dir, exist_ok=True)
        path = output_path or self._out_path(input_path, fmt_id)

        if fmt.get("palette"):
            result = await self._export_gif(input_path, path, scale=scale)
        else:
            result = await self._engine.transcode(
                input_path,
                path,
                video_codec=fmt["video_codec"],
                audio_codec=fmt["audio_codec"],
                scale=scale,
            )

        result.update(
            {
                "format": fmt_id,
                "container": fmt["container"],
                "file_path": path,
            }
        )
        logger.info("Export %s -> %s (%d bytes)", fmt_id, path, result["file_size_bytes"])
        return result

    async def _export_gif(self, input_path: str, output_path: str, scale: str | None = None) -> dict[str, Any]:
        """Two-pass GIF export: palettegen then paletteuse."""
        scale = scale or "480:-1"
        palette_path = output_path + ".palette.png"
        vf = f"fps=10,scale={scale}:flags=lanczos"

        cmd_palette = [
            self._engine.ffmpeg, "-y", "-i", input_path,
            "-vf", f"{vf},palettegen", palette_path,
        ]
        await self._run(cmd_palette, "GIF palette generation")

        cmd_use = [
            self._engine.ffmpeg, "-y", "-i", input_path, "-i", palette_path,
            "-lavfi", f"{vf}[x];[x][1:v]paletteuse", output_path,
        ]
        await self._run(cmd_use, "GIF palette use")
        if os.path.exists(palette_path):
            os.remove(palette_path)

        probe = await self._engine.probe(output_path)
        return {
            "output_path": output_path,
            "file_size_bytes": os.path.getsize(output_path),
            "duration": probe.duration,
            "success": True,
        }

    async def _run(self, cmd: list[str], label: str) -> None:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"{label} failed: {stderr.decode()[:500]}")
