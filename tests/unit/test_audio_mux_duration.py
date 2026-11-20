"""FFmpeg muxing must retain video duration when narration is shorter."""
from __future__ import annotations

import json
import shutil
import subprocess

import numpy as np
import pytest

from modules.ai_video_studio.media.audio import extract_audio_track, mux_audio_into_video, write_wav


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


@pytest.mark.skipif(
    not shutil.which("ffmpeg") or not shutil.which("ffprobe"),
    reason="FFmpeg and ffprobe are required for real narration extraction",
)
def test_extract_audio_track_recovers_narration_from_voiced_mp4(tmp_path) -> None:
    source = tmp_path / "voiced-source.mp4"
    extracted = tmp_path / "recovered-narration.wav"

    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-f", "lavfi", "-i", "color=c=navy:s=64x36:r=24:d=2",
            "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=44100:duration=2",
            "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k", str(source),
        ],
        check=True,
        capture_output=True,
    )

    result = extract_audio_track(source, extracted)

    assert result["extracted"] is True
    assert extracted.is_file() and extracted.stat().st_size > 44
    probe = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration:stream=codec_type,sample_rate,channels",
            "-of", "json", str(extracted),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    metadata = json.loads(probe.stdout)
    audio_streams = [
        stream for stream in metadata["streams"]
        if stream.get("codec_type") == "audio"
    ]
    assert len(audio_streams) == 1
    assert audio_streams[0]["sample_rate"] == "44100"
    assert int(audio_streams[0]["channels"]) == 2
    assert float(metadata["format"]["duration"]) == pytest.approx(2.0, abs=0.12)
