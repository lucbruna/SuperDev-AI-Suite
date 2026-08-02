"""FFmpeg render engine — runs actual FFmpeg commands for video processing.

This is the core rendering backend. All pipeline output ultimately flows
through here for encoding, muxing, and post-processing.
"""
from __future__ import annotations
import asyncio
import json
import logging
import os
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class RenderConfig:
    input_path: str
    output_path: str
    video_codec: str = "libx264"
    audio_codec: str = "aac"
    container: str = "mp4"
    resolution: str = "1920x1080"
    frame_rate: int = 30
    bitrate: str | None = None
    crf: int = 23
    preset: str = "medium"
    pixel_format: str = "yuv420p"
    audio_bitrate: str = "192k"
    audio_sample_rate: int = 44100
    audio_channels: int = 2
    two_pass: bool = False
    hardware_accel: str | None = None
    extra_flags: list[str] = field(default_factory=list)
    filters: list[str] = field(default_factory=list)
    concat_inputs: list[str] | None = None


@dataclass
class ProbeResult:
    duration: float = 0.0
    width: int = 0
    height: int = 0
    frame_rate: float = 0.0
    video_codec: str = ""
    audio_codec: str = ""
    bitrate: int = 0
    format_name: str = ""
    size: int = 0
    raw: dict = field(default_factory=dict)


class RenderEngine:
    """FFmpeg-based render engine with async subprocess execution."""

    def __init__(self, ffmpeg_path: str = "ffmpeg", ffprobe_path: str = "ffprobe"):
        self.ffmpeg = ffmpeg_path
        self.ffprobe = ffprobe_path
        self._verify_ffmpeg()

    def _verify_ffmpeg(self) -> None:
        ffmpeg_found = shutil.which(self.ffmpeg) is not None
        ffprobe_found = shutil.which(self.ffprobe) is not None
        if not ffmpeg_found:
            logger.warning(f"FFmpeg not found at '{self.ffmpeg}' — rendering will fail")
        if not ffprobe_found:
            logger.warning(f"FFprobe not found at '{self.ffprobe}' — probing will fail")

    async def probe(self, input_path: str) -> ProbeResult:
        """Probe a media file and return its metadata."""
        cmd = [
            self.ffprobe, "-v", "quiet",
            "-print_format", "json",
            "-show_format", "-show_streams",
            input_path,
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"ffprobe failed: {stderr.decode()}")
        data = json.loads(stdout.decode())
        fmt = data.get("format", {})
        streams = data.get("streams", [])
        video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
        audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})

        frame_rate_str = video_stream.get("r_frame_rate", "0/1")
        try:
            num, den = frame_rate_str.split("/")
            fps = float(num) / float(den) if float(den) != 0 else 0.0
        except (ValueError, ZeroDivisionError):
            fps = 0.0

        return ProbeResult(
            duration=float(fmt.get("duration", 0)),
            width=int(video_stream.get("width", 0)),
            height=int(video_stream.get("height", 0)),
            frame_rate=fps,
            video_codec=video_stream.get("codec_name", ""),
            audio_codec=audio_stream.get("codec_name", ""),
            bitrate=int(fmt.get("bit_rate", 0)),
            format_name=fmt.get("format_name", ""),
            size=int(fmt.get("size", 0)),
            raw=data,
        )

    async def render(self, config: RenderConfig) -> dict[str, Any]:
        """Execute a render pass using FFmpeg."""
        os.makedirs(os.path.dirname(config.output_path) or ".", exist_ok=True)

        cmd = self._build_command(config)
        logger.info(f"Render command: {' '.join(cmd)}")

        if config.two_pass:
            return await self._two_pass_render(config, cmd)
        return await self._single_pass_render(cmd, config.output_path)

    def _build_command(self, c: RenderConfig) -> list[str]:
        cmd = [self.ffmpeg, "-y"]
        if c.hardware_accel:
            cmd.extend(["-hwaccel", c.hardware_accel, "-hwaccel_output_format", "cuda"])

        if c.concat_inputs:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as concat_file:
                for inp in c.concat_inputs:
                    concat_file.write(f"file '{inp}'\n")
                concat_name = concat_file.name
            cmd.extend(["-f", "concat", "-safe", "0", "-i", concat_name])
        else:
            cmd.extend(["-i", c.input_path])

        cmd.extend(["-c:v", c.video_codec])
        cmd.extend(["-c:a", c.audio_codec])
        cmd.extend(["-vf", f"scale={c.resolution.replace('x', ':')},format={c.pixel_format}"])
        cmd.extend(["-r", str(c.frame_rate)])
        cmd.extend(["-b:a", c.audio_bitrate])
        cmd.extend(["-ar", str(c.audio_sample_rate)])
        cmd.extend(["-ac", str(c.audio_channels)])

        if c.video_codec in ("libx264", "libx265"):
            cmd.extend(["-crf", str(c.crf), "-preset", c.preset])
        elif c.bitrate:
            cmd.extend(["-b:v", c.bitrate])

        if c.filters:
            cmd.extend(["-vf", ",".join(c.filters)])
        cmd.extend(c.extra_flags)
        cmd.extend(["-movflags", "+faststart", c.output_path])
        return cmd

    async def _single_pass_render(self, cmd: list[str], output: str) -> dict[str, Any]:
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"FFmpeg render failed (code {proc.returncode}): {stderr.decode()[:1000]}")
        file_size = os.path.getsize(output) if os.path.exists(output) else 0
        probe = await self.probe(output)
        return {"output_path": output, "file_size_bytes": file_size, "duration": probe.duration, "success": True}

    async def _two_pass_render(self, config: RenderConfig, base_cmd: list[str]) -> dict[str, Any]:
        pass1 = list(base_cmd)
        pass1[-1] = config.output_path + ".pass1"
        pass1.insert(-1, "-pass")
        pass1.insert(-1, "1")
        proc1 = await asyncio.create_subprocess_exec(
            *pass1, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        await proc1.communicate()
        if proc1.returncode != 0:
            raise RuntimeError("FFmpeg pass 1 failed")

        pass2 = list(base_cmd)
        pass2.insert(-1, "-pass")
        pass2.insert(-1, "2")
        proc2 = await asyncio.create_subprocess_exec(
            *pass2, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc2.communicate()
        if proc2.returncode != 0:
            raise RuntimeError(f"FFmpeg pass 2 failed: {stderr.decode()[:500]}")

        pass1_file = config.output_path + ".pass1"
        if os.path.exists(pass1_file):
            os.remove(pass1_file)
        return await self._single_pass_render([], config.output_path)

    async def generate_thumbnail(
        self, input_path: str, output_path: str, timestamp: float = 1.0,
        width: int = 320, height: int = 180,
    ) -> str:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        cmd = [
            self.ffmpeg, "-y", "-ss", str(timestamp), "-i", input_path,
            "-vframes", "1", "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
            output_path,
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError("Thumbnail generation failed")
        return output_path

    async def extract_audio(self, input_path: str, output_path: str, codec: str = "aac") -> str:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        cmd = [self.ffmpeg, "-y", "-i", input_path, "-vn", "-c:a", codec, output_path]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError("Audio extraction failed")
        return output_path

    async def concat_videos(self, input_paths: list[str], output_path: str) -> dict[str, Any]:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as concat_file:
            for p in input_paths:
                concat_file.write(f"file '{p}'\n")
            concat_name = concat_file.name
        cmd = [
            self.ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", concat_name,
            "-c", "copy", output_path,
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()
        os.unlink(concat_file.name)
        if proc.returncode != 0:
            raise RuntimeError("Video concatenation failed")
        return {"output_path": output_path, "success": True}

    async def mux_audio(
        self, video_path: str, audio_path: str, output_path: str,
        volume: float = 1.0,
    ) -> dict[str, Any]:
        """Mix an audio track onto a video, replacing its original audio."""
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        cmd = [
            self.ffmpeg, "-y",
            "-i", video_path,
            "-i", audio_path,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "192k",
        ]
        if volume != 1.0:
            cmd.extend(["-af", f"volume={volume}"])
        cmd.extend(["-shortest", output_path])
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"Audio muxing failed: {stderr.decode()[:500]}")
        return {"output_path": output_path, "success": True}

    async def transcode(
        self,
        input_path: str,
        output_path: str,
        *,
        video_codec: str = "libx264",
        audio_codec: str | None = "aac",
        preset: str = "medium",
        crf: int = 23,
        scale: str | None = None,
        extra_flags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Transcode a media file to a different container/codec.

        Returns ``{"output_path", "file_size_bytes", "duration", "success"}``.
        """
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        cmd = [self.ffmpeg, "-y", "-i", input_path]
        cmd.extend(["-c:v", video_codec])
        if audio_codec:
            cmd.extend(["-c:a", audio_codec])
        else:
            cmd.extend(["-an"])
        if video_codec in ("libx264", "libx265", "libvpx-vp9"):
            cmd.extend(["-crf", str(crf), "-preset", preset])
        if scale:
            cmd.extend(["-vf", f"scale={scale}"])
        if extra_flags:
            cmd.extend(extra_flags)
        if output_path.endswith((".mp4", ".mov")):
            cmd.extend(["-movflags", "+faststart"])
        cmd.append(output_path)

        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError(f"Transcode failed: {stderr.decode()[:500]}")
        probe = await self.probe(output_path)
        return {
            "output_path": output_path,
            "file_size_bytes": os.path.getsize(output_path),
            "duration": probe.duration,
            "success": True,
        }

    async def add_subtitles(
        self, input_path: str, subtitle_path: str, output_path: str,
        style: str = "burn",
    ) -> str:
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        if style == "burn":
            # FFmpeg filter filenames need `\`, `:` and `'` escaped (Windows paths).
            escaped = (
                subtitle_path.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
            )
            cmd = [self.ffmpeg, "-y", "-i", input_path, "-vf", f"subtitles={escaped}", "-c:a", "copy", output_path]
        else:
            cmd = [self.ffmpeg, "-y", "-i", input_path, "-i", subtitle_path, "-c", "copy", "-c:s", "mov_text", output_path]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        await proc.communicate()
        if proc.returncode != 0:
            raise RuntimeError("Subtitle overlay failed")
        return output_path
