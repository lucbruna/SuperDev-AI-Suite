"""FFmpeg muxing must retain video duration when narration is shorter."""
from __future__ import annotations

import json
import shutil
import subprocess

import numpy as np
import pytest

from modules.ai_video_studio.media.audio import mux_audio_into_video, write_wav


@pytest.mark.skipif(
    not shutil.which("ffmpeg") or not shutil.which("ffprobe"),
    reason="FFmpeg and ffprobe are required for the real mux regression",
)
def test_short_narration_does_not_truncate_video(tmp_path) -> None:
    video = tmp_path / "source.mp4"
    audio = tmp_path / "short.wav"
    output = tmp_path / "voiced.mp4"

    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-f", "lavfi", "-i", "color=c=navy:s=64x36:r=24:d=3",
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            str(video),
        ],
        check=True,
        capture_output=True,
    )
    write_wav(audio, np.sin(np.arange(44100, dtype=np.float32) * 2 * np.pi * 440 / 44100) * 0.2)

    result = mux_audio_into_video(video, audio, output)
    assert result["muxed"] is True
    assert output.is_file() and output.stat().st_size > 0

    probe = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration:stream=codec_type,duration",
            "-of", "json", str(output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    metadata = json.loads(probe.stdout)
    duration = float(metadata["format"]["duration"])
    stream_types = {stream["codec_type"] for stream in metadata["streams"]}

    assert duration == pytest.approx(3.0, abs=0.15)
    assert {"video", "audio"}.issubset(stream_types)
