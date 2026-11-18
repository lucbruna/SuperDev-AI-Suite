"""Tests for the AI Video Studio API routes — /videos/generate with voiceover.

Covers the connection between the FastAPI layer and ``TextToVideoEngine``:
request schema (voiceover, voice_id, voice_pitch, voiceover_mode), job
lifecycle, ``output_url``/``output_path`` propagation, the downloads
endpoint (with path-traversal blocking), and that the engine receives the
voiceover params it needs to produce the MP4 with audio.

All engines are mocked and downloads are redirected to a per-test ``tmp_path``
— no network, no FFmpeg, no pollution of the real downloads tree.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from modules.ai_video_studio.api.main import create_app
from modules.ai_video_studio.api import urls


# ── Fixtures ──────────────────────────────────────────────────────

@pytest.fixture
def app() -> FastAPI:
    return create_app()


@pytest.fixture
async def client(app: FastAPI):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


class _FakeEngine:
    """In-memory stand-in for TextToVideoEngine.generate_async."""

    def __init__(self) -> None:
        self.received: dict | None = None  # the job dict (input)
        self.result: dict | None = None  # the engine result (output)

    async def generate_async(self, job: dict, progress_callback=None) -> dict:
        self.received = job
        from modules.ai_video_studio.media.output_paths import get_subsystem_dir

        out = get_subsystem_dir("videos") / "fake_voiced_0001.mp4"
        out.write_bytes(b"FAKE-MP4-WITH-AUDIO")
        result = {
            "output_path": str(out),
            "output_bytes": out.stat().st_size,
            "ai_planner": "deterministic",
            "video_duration": 6.0,
            "voiceover": {
                "muxed": True,
                "output_path": str(out),
                "bytes": out.stat().st_size,
                "clips": [
                    {
                        "index": 0, "start": 0.0, "end": 3.0, "text": "Intro",
                        "audio_path": str(out), "tts_engine": "edge-tts",
                        "audio_duration": 2.9,
                    },
                    {
                        "index": 1, "start": 3.0, "end": 6.0, "text": "Outro",
                        "audio_path": str(out), "tts_engine": "edge-tts",
                        "audio_duration": 2.8,
                    },
                ],
                "total_duration": 6.0,
                "voice_id": "francisca",
                "language": "pt-BR",
                "narration_style": "per_scene",
                "narration": "Intro Outro",
            },
        }
        self.result = result
        return result


@pytest.fixture
def fake_engine(monkeypatch, tmp_path) -> _FakeEngine:
    """Patch the engine and redirect downloads to a per-test temp tree."""
    engine = _FakeEngine()

    # Redirect BOTH the shared output-paths root and the download route's
    # copy so the fake MP4 is written/served under tmp_path only.
    fake_root = tmp_path / "downloads"
    monkeypatch.setattr(
        "modules.ai_video_studio.media.output_paths.DOWNLOADS_DIR", fake_root
    )
    monkeypatch.setattr(
        "modules.ai_video_studio.api.routes.generation.DOWNLOADS_DIR", fake_root
    )

    # The route imports TextToVideoEngine inside the background closure, so
    # patch it at its source module.
    monkeypatch.setattr(
        "modules.ai_video_studio.ai_video_generator.text_to_video.text_to_video_engine.TextToVideoEngine",
        lambda *a, **k: engine,
    )
    return engine


# ── POST /videos/generate ─────────────────────────────────────────

class TestGenerateVoiceover:
    @pytest.mark.asyncio
    async def test_accepts_voiceover_fields(self, client: AsyncClient, fake_engine: _FakeEngine):
        resp = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={
                "project_id": "p1",
                "prompt": "a sunset over the ocean",
                "voiceover": True,
                "voice_id": "francisca",
                "voice_language": "pt-BR",
                "voice_speed": 1.1,
                "voice_pitch": 1.05,
                "voiceover_mode": "per_scene",
                "generate_subtitles": True,
            },
        )
        assert resp.status_code == 202
        body = resp.json()
        assert body["status"] == "queued"
        assert body["job_id"]

        # The engine must have received every voiceover param.
        assert fake_engine.received is not None
        params = fake_engine.received["params"]
        assert params["voiceover"] is True
        assert params["voice_id"] == "francisca"
        assert params["voice_language"] == "pt-BR"
        assert params["voice_speed"] == 1.1
        assert params["voice_pitch"] == 1.05
        assert params["voiceover_mode"] == "per_scene"
        assert params["generate_subtitles"] is True

    @pytest.mark.asyncio
    async def test_defaults_voiceover_off(self, client: AsyncClient, fake_engine: _FakeEngine):
        resp = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={"project_id": "p1", "prompt": "city at night"},
        )
        assert resp.status_code == 202
        assert fake_engine.received is not None
        params = fake_engine.received["params"]
        assert params["voiceover"] is False
        assert params["voice_id"] == "default"
        assert params["voice_language"] == "pt-BR"
        assert params["generate_subtitles"] is False
