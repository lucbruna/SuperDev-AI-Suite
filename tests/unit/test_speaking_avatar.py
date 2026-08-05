"""Tests for the Speaking Avatar pipeline (avatar × voice studio × lip-sync).

All audio is pre-synthesized locally (numpy → WAV), so the suite is fully
hermetic — no TTS engines, no network, no ffmpeg requirement.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

from modules.ai_video_studio.ai_avatar_engine.speaking import (
    compose_facial,
    get_speaking_engine,
)
from modules.ai_video_studio.media import dsp


def _write_narration_wav(path: Path, seconds: float = 1.2, freq: float = 220.0) -> Path:
    """Synthesize a short tone WAV to stand in for real narration audio."""
    n = int(dsp.SAMPLE_RATE * seconds)
    t = np.arange(n) / dsp.SAMPLE_RATE
    samples = (0.4 * np.sin(2 * np.pi * freq * t)).astype(np.float32)
    samples = dsp.fade_io(samples, fade_in=0.05, fade_out=0.1)
    return dsp.write_audio(path, samples, sample_rate=dsp.SAMPLE_RATE)


# ── Pure mapping ─────────────────────────────────────────────────
def test_compose_facial_maps_viseme_to_mouth_open():
    frame = {"time": 0.25, "open": 0.8, "round": 0.4, "wide": 0.2, "_blink": 1.0}
    inputs = compose_facial(frame)
    assert inputs["t"] == 0.25
    assert inputs["mouth_open"] == pytest.approx(0.8)
    assert inputs["forced_blink"] == 0.0  # open eyes


def test_compose_facial_forces_blink_on_closed_frame():
    frame = {"time": 1.0, "open": 0.0, "_blink": 0.0}  # 0 = eyes closed
    assert compose_facial(frame)["forced_blink"] == 1.0


def test_compose_facial_applies_emotion_base():
    frame = {"time": 0.0, "open": 0.3, "_blink": 1.0}
    inputs = compose_facial(frame, emotion_facial={"smile": 0.8, "brow_raise": 0.3})
    assert inputs["smile"] == pytest.approx(0.8)
    assert inputs["brow_raise"] == pytest.approx(0.3)
    assert inputs["mouth_open"] == pytest.approx(0.3)


# ── Engine (hermetic, audio provided) ────────────────────────────
async def test_generate_with_audio_path_produces_video(tmp_path):
    audio = _write_narration_wav(tmp_path / "narration.wav", seconds=1.2)
    out = tmp_path / "output.mp4"

    result = await get_speaking_engine().generate(
        "biz_maya", "Hello world, this is a synchronized narration test.",
        audio_path=str(audio),
        output_path=str(out),
        fps=10, width=320, height=240,
    )

    assert result["status"] == "ok"
    assert result["duration"] == pytest.approx(1.2, abs=0.05)
    assert result["frames"] > 5
    assert result["phonemes"] > 0
    assert Path(result["output_path"]).exists()
    assert result["output_bytes"] > 0
    assert Path(result["timeline_path"]).exists()
    assert result["tts_engine"] is None  # no TTS ran
    assert isinstance(result["muxed"], bool)
    # The exact requested output path is honored when muxing is possible.
    from modules.ai_video_studio.media.video import ffmpeg_available

    if ffmpeg_available():
        assert result["output_path"] == str(out)
    # Colors were resolved from the digital-human descriptor.
    assert result["colors"]["skin"].startswith("#")


async def test_generate_unknown_profile_raises(tmp_path):
    audio = _write_narration_wav(tmp_path / "narration.wav", seconds=0.6)
    with pytest.raises(KeyError):
        await get_speaking_engine().generate(
            "no_such_profile_xyz", "hello", audio_path=str(audio), fps=6,
        )


async def test_generate_render_video_false_is_metadata_only(tmp_path):
    audio = _write_narration_wav(tmp_path / "narration.wav", seconds=0.6)
    result = await get_speaking_engine().generate(
        "biz_maya", "metadata only", audio_path=str(audio),
        render_video=False, fps=6,
    )
    assert result["output_path"] is None
    assert result["frames"] > 0
    assert Path(result["timeline_path"]).exists()


# ── API ──────────────────────────────────────────────────────────
def test_speak_api_endpoint(tmp_path):
    audio = _write_narration_wav(tmp_path / "narration.wav", seconds=0.8)
    client = TestClient(_create_app())

    resp = client.post(
        "/api/v1/video-studio/avatar-engine/speak",
        json={
            "profile_id": "biz_maya",
            "text": "Welcome to the AI studio.",
            "audio_path": str(audio),
            "fps": 8,
            "width": 320,
            "height": 240,
        },
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()["data"]
    assert data["status"] == "ok"
    assert Path(data["output_path"]).exists()
    assert data["emotion"] is None


def test_speak_api_endpoint_with_emotion(tmp_path):
    audio = _write_narration_wav(tmp_path / "narration.wav", seconds=0.8)
    client = TestClient(_create_app())

    resp = client.post(
        "/api/v1/video-studio/avatar-engine/speak",
        json={
            "profile_id": "biz_maya",
            "text": "I am so happy to be here today.",
            "audio_path": str(audio),
            "emotion": "happy",
            "fps": 8,
            "width": 320,
            "height": 240,
        },
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["data"]["emotion"] == "happy"


def test_speak_api_unknown_profile_returns_404(tmp_path):
    audio = _write_narration_wav(tmp_path / "narration.wav", seconds=0.5)
    client = TestClient(_create_app())

    resp = client.post(
        "/api/v1/video-studio/avatar-engine/speak",
        json={"profile_id": "nope", "text": "x", "audio_path": str(audio)},
    )
    assert resp.status_code == 404


def test_speaking_voices_endpoint():
    client = TestClient(_create_app())
    resp = client.get("/api/v1/video-studio/avatar-engine/speaking/voices")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["count"] >= 0
    assert isinstance(data["voices"], list)


def _create_app():
    from modules.ai_video_studio.api.main import create_app

    return create_app()
