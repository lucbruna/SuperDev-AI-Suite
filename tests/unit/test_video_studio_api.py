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


async def _async_result(value):
    return value


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
        if progress_callback is not None:
            progress_callback(12, 24)
        from modules.ai_video_studio.media.output_paths import get_subsystem_dir

        out = get_subsystem_dir("videos") / "fake_voiced_0001.mp4"
        out.write_bytes(b"FAKE-MP4-WITH-AUDIO")
        subtitle_info = None
        if job.get("params", {}).get("generate_subtitles"):
            subtitle_path = get_subsystem_dir("subtitles") / "fake_0001.srt"
            subtitle_path.parent.mkdir(parents=True, exist_ok=True)
            subtitle_path.write_text("1\\n00:00:00,000 --> 00:00:02,000\\nLegenda de teste.\\n", encoding="utf-8")
            subtitle_info = {
                "format": "srt",
                "file_path": str(subtitle_path),
                "cue_count": 1,
                "duration": 2.0,
            }
        result = {
            "output_path": str(out),
            "output_bytes": out.stat().st_size,
            "ai_planner": "deterministic",
            "video_duration": 6.0,
            "subtitles": subtitle_info,
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
        assert params["voiceover_mode"] == "per_scene"

    @pytest.mark.asyncio
    async def test_rejects_invalid_voiceover_mode(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={
                "project_id": "p1",
                "prompt": "ocean",
                "voiceover": True,
                "voiceover_mode": "bogus",
            },
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_rejects_empty_prompt(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={"project_id": "p1", "prompt": ""},
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_accepts_duration_up_to_10_minutes(self, client: AsyncClient, fake_engine: _FakeEngine):
        """The API must accept every preset duration up to the 600s cap."""
        for seconds in [10, 30, 60, 120, 180, 300, 600]:
            resp = await client.post(
                "/api/v1/video-studio/videos/generate",
                json={"project_id": "p1", "prompt": "ocean", "duration_seconds": seconds},
            )
            assert resp.status_code == 202, f"duration {seconds}s rejected: {resp.text}"
            assert fake_engine.received is not None
            assert fake_engine.received["params"]["duration"] == seconds

    @pytest.mark.asyncio
    async def test_rejects_duration_above_10_minutes(self, client: AsyncClient):
        resp = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={"project_id": "p1", "prompt": "ocean", "duration_seconds": 601},
        )
        assert resp.status_code == 422


# ── Resolution / aspect-ratio validation ────────────────────────

class TestResolutionValidation:
    """_parse_resolution strictness — standard ratios accepted, 422 otherwise."""

    @pytest.mark.asyncio
    async def test_accepts_standard_resolutions(
        self, client: AsyncClient, fake_engine: _FakeEngine
    ):
        """16:9, 9:16 and 1:1 presets (plus the W:H colon form) must pass."""
        for res in [
            "1280x720", "1920x1080", "3840x2160", "2560x1440",  # 16:9
            "1080x1920", "720x1280",  # 9:16 vertical
            "1080x1080", "640x640",  # 1:1 square
            "2560x1080", "5120x2160",  # 21:9 ultrawide (64:27)
            "3440x1440",  # 21:9 ultrawide (43:18)
            "1280:720",  # colon form
        ]:
            resp = await client.post(
                "/api/v1/video-studio/videos/generate",
                json={"project_id": "p1", "prompt": "ocean", "resolution": res},
            )
            assert resp.status_code == 202, f"{res} rejected: {resp.text}"
            assert fake_engine.received is not None
            assert fake_engine.received["params"]["width"] > 0
            assert fake_engine.received["params"]["height"] > 0

    @pytest.mark.asyncio
    async def test_rejects_non_standard_aspect_ratio(self, client: AsyncClient):
        """Ratios outside 16:9/9:16/1:1/4:3/21:9 must be rejected with 422."""
        for res in ["1920x1088", "1000x700", "1234x567"]:
            resp = await client.post(
                "/api/v1/video-studio/videos/generate",
                json={"project_id": "p1", "prompt": "ocean", "resolution": res},
            )
            assert resp.status_code == 422, f"{res} accepted: {resp.text}"

    @pytest.mark.asyncio
    async def test_rejects_unparseable_and_out_of_range(self, client: AsyncClient):
        """Garbage, bare numbers and out-of-bounds edges must be 422, not
        silently downgraded to 720p."""
        for bad in ["garbage", "", "1080", "1080x", "50x50", "8000x4500", "0x0"]:
            resp = await client.post(
                "/api/v1/video-studio/videos/generate",
                json={"project_id": "p1", "prompt": "ocean", "resolution": bad},
            )
            assert resp.status_code == 422, f"{bad!r} accepted: {resp.text}"

    @pytest.mark.asyncio
    async def test_422_body_explains_aspect_ratio_reason(self, client: AsyncClient):
        """The 422 detail must state the offending ratio and hint supported ones."""
        resp = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={"project_id": "p1", "prompt": "ocean", "resolution": "1920x1088"},
        )
        assert resp.status_code == 422
        msg = resp.json()["detail"][0]["msg"]
        assert "aspect ratio 30:17" in msg
        assert "9:16" in msg  # hints the supported set

    def test_parse_resolution_returns_tuples(self):
        from modules.ai_video_studio.api.routes.video import _parse_resolution

        assert _parse_resolution("1080x1920") == (1080, 1920)
        assert _parse_resolution("1080:1080") == (1080, 1080)
        assert _parse_resolution(" 1920x1080 ") == (1920, 1080)
        assert _parse_resolution("3840x2160") == (3840, 2160)
        assert _parse_resolution("2560x1080") == (2560, 1080)
        assert _parse_resolution("3440x1440") == (3440, 1440)

    def test_parse_resolution_rejects_invalid(self):
        from modules.ai_video_studio.api.routes.video import _parse_resolution

        for bad in ["garbage", "1080", "1920x1088", "50x50", "8000x4500", "0x0"]:
            with pytest.raises(ValueError):
                _parse_resolution(bad)


# ── GET /videos/jobs/{job_id} ─────────────────────────────────────

class TestJobStatus:
    @pytest.mark.asyncio
    async def test_render_progress_is_saved_as_a_job_checkpoint(
        self, client: AsyncClient, fake_engine: _FakeEngine, monkeypatch
    ):
        from modules.ai_video_studio.api.routes import video as video_routes

        saved_steps: list[str] = []
        original_persist = video_routes._persist_job

        def capture_persist(record: dict) -> None:
            saved_steps.append(str(record.get("current_step") or ""))
            original_persist(record)

        monkeypatch.setattr(video_routes, "_persist_job", capture_persist)
        response = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={"project_id": "p1", "prompt": "render progress checkpoint"},
        )
        assert response.status_code == 202
        assert "Rendering frames" in saved_steps

    @pytest.mark.asyncio
    async def test_job_completes_with_output_url_and_voiceover(
        self, client: AsyncClient, fake_engine: _FakeEngine
    ):
        resp = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={"project_id": "p1", "prompt": "jungle", "voiceover": True},
        )
        job_id = resp.json()["job_id"]

        # Background task may not have run yet — poll briefly.
        status: dict = {}
        for _ in range(50):
            r = await client.get(f"/api/v1/video-studio/videos/jobs/{job_id}")
            assert r.status_code == 200
            status = r.json()
            if status["status"] in {"completed", "failed"}:
                break

        assert status["status"] == "completed", status.get("error")
        assert status["output_path"] and Path(status["output_path"]).exists()
        assert status["output_url"] == urls.to_download_url(status["output_path"])
        assert status["file_size_bytes"] > 0
        vo = status["voiceover"]
        assert vo is not None
        assert vo["muxed"] is True
        assert vo["narration_style"] == "per_scene"
        assert len(vo["clips"]) == 2

    @pytest.mark.asyncio
    async def test_job_exposes_real_video_duration_and_resolution(
        self, client: AsyncClient, fake_engine: _FakeEngine, monkeypatch
    ):
        """Completed jobs must expose the real MP4 duration + resolution/fps."""
        from modules.ai_video_studio.api.routes import video as video_routes

        # The fake MP4 is not a real video, so stub the ffprobe probe.
        async def _fake_probe(path: str) -> float:
            return 42.5

        monkeypatch.setattr(video_routes, "_probe_video_duration", _fake_probe)
        resp = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={
                "project_id": "p1", "prompt": "ocean", "voiceover": True,
                "resolution": "1920x1080", "frame_rate": 30,
            },
        )
        job_id = resp.json()["job_id"]
        status: dict = {}
        for _ in range(50):
            r = await client.get(f"/api/v1/video-studio/videos/jobs/{job_id}")
            status = r.json()
            if status["status"] in {"completed", "failed"}:
                break

        assert status["status"] == "completed", status.get("error")
        assert status["video_duration"] == 42.5
        assert status["resolution"] == "1920x1080"
        assert status["frame_rate"] == 30

    @pytest.mark.asyncio
    async def test_job_tracks_frame_render_progress(self, client: AsyncClient, monkeypatch):
        """The progress callback must update the job record live: a failure
        mid-render leaves frames_rendered/total_frames/progress/current_step at
        their last reported values (the failure path preserves them).

        This is deterministic with ASGITransport (background tasks run inline,
        so we cannot poll the job "while it renders" — instead the fake stops
        mid-render and we inspect the frozen record).
        """
        events: list[tuple[int, int]] = []

        async def _fake(self, job: dict, progress_callback=None) -> dict:
            from modules.ai_video_studio.media.output_paths import get_subsystem_dir

            out = get_subsystem_dir("videos") / "fake_voiced_0001.mp4"
            out.write_bytes(b"FAKE-MP4-WITH-AUDIO")
            # Simulate a 60-frame render reporting progress, then die mid-way
            # so the record keeps the last reported progress values.
            for rendered in (1, 15, 30, 45, 60):
                if progress_callback:
                    progress_callback(rendered, 60)
                events.append((rendered, 60))
            raise RuntimeError("renderer crashed")

        monkeypatch.setattr(
            "modules.ai_video_studio.ai_video_generator.text_to_video.text_to_video_engine.TextToVideoEngine",
            lambda *a, **k: type("E", (), {"generate_async": _fake})(),
        )
        resp = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={"project_id": "p1", "prompt": "jungle"},
        )
        job_id = resp.json()["job_id"]

        status: dict = {}
        for _ in range(50):
            r = await client.get(f"/api/v1/video-studio/videos/jobs/{job_id}")
            status = r.json()
            if status["status"] in {"completed", "failed"}:
                break

        # The callback contract fired exactly as the render reported.
        assert events == [(1, 60), (15, 60), (30, 60), (45, 60), (60, 60)]
        # Failed job still exposes the last live progress (frozen mid-render).
        assert status["status"] == "failed"
        assert "renderer crashed" in status["error"]
        assert status["current_step"] == "Rendering frames"
        assert status["total_frames"] == 60
        assert status["frames_rendered"] == 60
        # 10% (planning) + 75% of the completed frame fraction.
        assert abs(status["progress"] - (0.1 + 0.75 * 60 / 60)) < 1e-9

    @pytest.mark.asyncio
    async def test_job_persists_format_and_params(
        self, client: AsyncClient, fake_engine: _FakeEngine
    ):
        """The chosen platform format + every generation param must be stored
        on the job so the dashboard list can label it ("Shorts 9:16") and
        re-run it later."""
        resp = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={
                "project_id": "p1", "prompt": "ocean", "format": "shorts",
                "duration_seconds": 30, "frame_rate": 30, "num_scenes": 2,
                "voiceover": True, "voice_id": "francisca",
                "voiceover_mode": "per_scene",
            },
        )
        assert resp.status_code == 202
        # The 202 response carries the format for instant UI labeling.
        assert resp.json()["format"] == "shorts"

        job_id = resp.json()["job_id"]
        status: dict = {}
        for _ in range(50):
            r = await client.get(f"/api/v1/video-studio/videos/jobs/{job_id}")
            status = r.json()
            if status["status"] in {"completed", "failed"}:
                break

        assert status["status"] == "completed", status.get("error")
        assert status["format"] == "shorts"
        params = status["params"]
        assert params is not None
        assert params["format"] == "shorts"
        assert params["prompt"] == "ocean"  # full snapshot enables re-run
        assert params["duration_seconds"] == 30
        assert params["frame_rate"] == 30
        assert params["num_scenes"] == 2
        assert params["voiceover"] is True
        assert params["voice_id"] == "francisca"
        assert params["voiceover_mode"] == "per_scene"
        assert params["resolution"] == "1280x720"  # default kept in snapshot

    @pytest.mark.asyncio
    async def test_job_format_defaults_to_custom(
        self, client: AsyncClient, fake_engine: _FakeEngine
    ):
        """Without a format field the job records 'custom' (no badge in list)."""
        resp = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={"project_id": "p1", "prompt": "ocean"},
        )
        assert resp.status_code == 202
        assert resp.json()["format"] == "custom"

        job_id = resp.json()["job_id"]
        status: dict = {}
        for _ in range(50):
            r = await client.get(f"/api/v1/video-studio/videos/jobs/{job_id}")
            status = r.json()
            if status["status"] in {"completed", "failed"}:
                break

        assert status["status"] == "completed", status.get("error")
        assert status["format"] == "custom"
        assert status["params"]["format"] == "custom"

    @pytest.mark.asyncio
    async def test_job_keeps_frame_progress_on_completion(
        self, client: AsyncClient, monkeypatch
    ):
        """Completed jobs keep the final frame counters alongside progress=1.0."""
        async def _fake(self, job: dict, progress_callback=None) -> dict:
            from modules.ai_video_studio.media.output_paths import get_subsystem_dir

            out = get_subsystem_dir("videos") / "fake_voiced_0001.mp4"
            out.write_bytes(b"FAKE-MP4-WITH-AUDIO")
            if progress_callback:
                progress_callback(30, 30)
            return {
                "output_path": str(out),
                "output_bytes": out.stat().st_size,
                "ai_planner": "deterministic",
            }

        monkeypatch.setattr(
            "modules.ai_video_studio.ai_video_generator.text_to_video.text_to_video_engine.TextToVideoEngine",
            lambda *a, **k: type("E", (), {"generate_async": _fake})(),
        )
        resp = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={"project_id": "p1", "prompt": "jungle"},
        )
        job_id = resp.json()["job_id"]
        status: dict = {}
        for _ in range(50):
            r = await client.get(f"/api/v1/video-studio/videos/jobs/{job_id}")
            status = r.json()
            if status["status"] in {"completed", "failed"}:
                break

        assert status["status"] == "completed", status.get("error")
        assert status["progress"] == 1.0
        assert status["current_step"] == "Done"
        assert status["total_frames"] == 30
        assert status["frames_rendered"] == 30

    @pytest.mark.asyncio
    async def test_probe_video_duration_calls_ffprobe(self, monkeypatch):
        """The probe helper must return the real ffprobe duration."""
        from modules.ai_video_studio.api.routes import video as video_routes

        def _fake_probe_duration(path: str) -> float:
            return 42.5

        monkeypatch.setattr(
            "modules.ai_video_studio.ai_dubbing.export_dubbing.probe_duration",
            _fake_probe_duration,
        )
        # The helper imports probe_duration lazily inside the function, so the
        # patched module attribute is what gets called via asyncio.to_thread.
        result = await video_routes._probe_video_duration("/tmp/x.mp4")
        assert result == 42.5

    @pytest.mark.asyncio
    async def test_job_voiceover_clips_expose_timeline_offsets(
        self, client: AsyncClient, fake_engine: _FakeEngine
    ):
        """Per-scene voiceover metadata must expose structured clip offsets."""
        resp = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={
                "project_id": "p1", "prompt": "jungle", "voiceover": True,
                "voiceover_mode": "per_scene",
            },
        )
        job_id = resp.json()["job_id"]
        status: dict = {}
        for _ in range(50):
            r = await client.get(f"/api/v1/video-studio/videos/jobs/{job_id}")
            status = r.json()
            if status["status"] in {"completed", "failed"}:
                break

        assert status["status"] == "completed", status.get("error")
        vo = status["voiceover"]
        assert vo is not None
        clips = vo["clips"]
        assert [c["start"] for c in clips] == [0.0, 3.0]  # cumulative offsets
        assert [c["end"] for c in clips] == [3.0, 6.0]
        assert [c["index"] for c in clips] == [0, 1]
        assert clips[0]["audio_path"].endswith(".mp4")
        assert clips[0]["tts_engine"] == "edge-tts"
        assert clips[0]["audio_duration"] == 2.9
        assert vo["total_duration"] == 6.0
        assert vo["voice_id"] == "francisca"
        assert vo["language"] == "pt-BR"

    @pytest.mark.asyncio
    async def test_openapi_documents_voiceover_clip_schema(self, client: AsyncClient):
        """The OpenAPI schema must expose the typed clips/offsets structure."""
        r = await client.get("/api/v1/video-studio/openapi.json")
        assert r.status_code == 200
        schemas = r.json()["components"]["schemas"]

        # Response model now references a typed VoiceoverInfo, not a bare dict.
        # The field is nullable, so the schema wraps it in anyOf[ref, null].
        status_props = schemas["VideoStatusResponse"]["properties"]
        vo_ref = status_props["voiceover"]
        refs = [
            entry.get("$ref", "")
            for entry in vo_ref.get("anyOf", [])
            if "$ref" in entry
        ]
        assert any(ref.endswith("/VoiceoverInfo") for ref in refs), vo_ref

        voiceover_schema = schemas["VoiceoverInfo"]["properties"]
        assert voiceover_schema["narration_style"]["default"] == "single_track"
        assert voiceover_schema["clips"]["type"] == "array"
        assert voiceover_schema["clips"]["items"]["$ref"].endswith("/VoiceoverClip")

        clip_schema = schemas["VoiceoverClip"]["properties"]
        assert clip_schema["start"]["type"] == "number"
        assert clip_schema["end"]["type"] == "number"
        assert clip_schema["index"]["type"] == "integer"
        assert clip_schema["audio_path"]["anyOf"]

        # Request schema exposes voiceover_mode per-scene default.
        req_props = schemas["VideoGenerateRequest"]["properties"]
        assert req_props["voiceover_mode"]["default"] == "per_scene"
        assert "per_scene|single" in req_props["voiceover_mode"].get("pattern", "")

    @pytest.mark.asyncio
    async def test_job_404_for_unknown_id(self, client: AsyncClient):
        resp = await client.get("/api/v1/video-studio/videos/jobs/nope")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_single_track_and_failure_shapes_serialize(
        self, client: AsyncClient, monkeypatch
    ):
        """Partial voiceover dicts (single-track / failed TTS) must serialize
        through the typed model without errors and with sensible defaults."""

        async def _fake(self, job: dict, progress_callback=None) -> dict:
            from modules.ai_video_studio.media.output_paths import get_subsystem_dir

            out = get_subsystem_dir("videos") / "fake_voiced_0001.mp4"
            out.write_bytes(b"FAKE-MP4-WITH-AUDIO")
            return {
                "output_path": str(out),
                "output_bytes": out.stat().st_size,
                "ai_planner": "deterministic",
                # Single-track success: no clips/total_duration/voice_id keys.
                "voiceover": {
                    "muxed": True,
                    "output_path": str(out),
                    "bytes": out.stat().st_size,
                    "tts_engine": "formant",
                    "audio_duration": 5.2,
                    "narration": "A single flat track",
                    "narration_style": "single_track",
                },
            }

        monkeypatch.setattr(
            "modules.ai_video_studio.ai_video_generator.text_to_video.text_to_video_engine.TextToVideoEngine",
            lambda *a, **k: type("E", (), {"generate_async": _fake})(),
        )
        resp = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={"project_id": "p1", "prompt": "jungle", "voiceover": True},
        )
        job_id = resp.json()["job_id"]
        status: dict = {}
        for _ in range(50):
            r = await client.get(f"/api/v1/video-studio/videos/jobs/{job_id}")
            status = r.json()
            if status["status"] in {"completed", "failed"}:
                break

        assert status["status"] == "completed", status.get("error")
        vo = status["voiceover"]
        assert vo is not None
        assert vo["muxed"] is True
        assert vo["narration_style"] == "single_track"
        assert vo["clips"] == []  # default when absent
        assert vo["total_duration"] is None
        assert vo["tts_engine"] == "formant"
        assert vo["audio_duration"] == 5.2

    @pytest.mark.asyncio
    async def test_failed_voiceover_dict_serializes(
        self, client: AsyncClient, monkeypatch
    ):
        """A bare {"muxed": False, "reason": ...} must serialize (TTS down)."""

        async def _fake(self, job: dict, progress_callback=None) -> dict:
            from modules.ai_video_studio.media.output_paths import get_subsystem_dir

            out = get_subsystem_dir("videos") / "fake_voiced_0001.mp4"
            out.write_bytes(b"FAKE-MP4-WITH-AUDIO")
            return {
                "output_path": str(out),
                "output_bytes": out.stat().st_size,
                "ai_planner": "deterministic",
                "voiceover": {"muxed": False, "reason": "tts_failed: no engines"},
            }

        monkeypatch.setattr(
            "modules.ai_video_studio.ai_video_generator.text_to_video.text_to_video_engine.TextToVideoEngine",
            lambda *a, **k: type("E", (), {"generate_async": _fake})(),
        )
        resp = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={"project_id": "p1", "prompt": "jungle", "voiceover": True},
        )
        job_id = resp.json()["job_id"]
        status: dict = {}
        for _ in range(50):
            r = await client.get(f"/api/v1/video-studio/videos/jobs/{job_id}")
            status = r.json()
            if status["status"] in {"completed", "failed"}:
                break

        assert status["status"] == "completed", status.get("error")
        vo = status["voiceover"]
        assert vo is not None
        assert vo["muxed"] is False
        assert vo["reason"] == "tts_failed: no engines"
        assert vo["clips"] == []
        assert vo["audio"] is None

    @pytest.mark.asyncio
    async def test_job_failure_is_surfaced(self, client: AsyncClient, monkeypatch):
        async def _boom(self, job: dict, progress_callback=None) -> dict:
            raise RuntimeError("engine exploded")

        monkeypatch.setattr(
            "modules.ai_video_studio.ai_video_generator.text_to_video.text_to_video_engine.TextToVideoEngine",
            lambda *a, **k: type("E", (), {"generate_async": _boom})(),
        )
        resp = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={"project_id": "p1", "prompt": "jungle"},
        )
        job_id = resp.json()["job_id"]
        status: dict = {}
        for _ in range(50):
            r = await client.get(f"/api/v1/video-studio/videos/jobs/{job_id}")
            status = r.json()
            if status["status"] in {"completed", "failed"}:
                break
        assert status["status"] == "failed"
        assert "engine exploded" in status["error"]


# ── GET /downloads/{kind}/{filename} ──────────────────────────────

class TestDownloads:
    @pytest.mark.asyncio
    async def test_downloads_serves_generated_mp4(self, client: AsyncClient, fake_engine: _FakeEngine):
        await client.post(
            "/api/v1/video-studio/videos/generate",
            json={"project_id": "p1", "prompt": "jungle", "voiceover": True},
        )
        assert fake_engine.result is not None
        out_path = fake_engine.result["output_path"]
        filename = Path(out_path).name

        resp = await client.get(f"/api/v1/video-studio/downloads/videos/{filename}")
        assert resp.status_code == 200
        assert resp.content == b"FAKE-MP4-WITH-AUDIO"
        assert resp.headers["content-type"].startswith("video/")

    @pytest.mark.asyncio
    async def test_download_rejects_path_traversal(self, client: AsyncClient):
        for bad in ["..%2F..%2F..%2Fetc%2Fpasswd", "..\\..\\secrets.txt", "x/../../y"]:
            resp = await client.get(f"/api/v1/video-studio/downloads/videos/{bad}")
            # Either 404 (safe) or 422 (rejected by FastAPI) — never a file leak.
            assert resp.status_code in {404, 422}

    @pytest.mark.asyncio
    async def test_download_404_for_missing_file(self, client: AsyncClient):
        resp = await client.get("/api/v1/video-studio/downloads/videos/does_not_exist.mp4")
        assert resp.status_code == 404


# ── URL helper ────────────────────────────────────────────────────

class TestToDownloadUrl:
    def test_maps_downloads_tree(self):
        url = urls.to_download_url("C:/x/modules/downloads/videos/abc.mp4")
        assert url == "/api/v1/video-studio/downloads/videos/abc.mp4"

    def test_returns_none_outside_tree(self):
        assert urls.to_download_url("C:/other/output.mp4") is None
        assert urls.to_download_url("") is None


class TestDarkstudioProfileSelection:
    @pytest.mark.asyncio
    async def test_selected_studio_profile_reaches_render_engine(
        self, client: AsyncClient, fake_engine: _FakeEngine
    ):
        resp = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={
                "project_id": "p1",
                "prompt": "Uma cidade histórica ao amanhecer",
                "studio_id": "historical_documentary",
            },
        )
        assert resp.status_code == 202
        assert fake_engine.received is not None
        assert fake_engine.received["params"]["studio_id"] == "historical_documentary"

    @pytest.mark.asyncio
    async def test_unknown_studio_profile_is_rejected(
        self, client: AsyncClient
    ):
        resp = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={
                "project_id": "p1",
                "prompt": "Uma cena de teste",
                "studio_id": "unknown",
            },
        )
        assert resp.status_code == 422


class TestSubtitleDownload:
    @pytest.mark.asyncio
    async def test_generated_srt_is_exposed_as_downloadable_file(
        self, client: AsyncClient, fake_engine: _FakeEngine
    ):
        resp = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={
                "project_id": "p1",
                "prompt": "Cena com legenda.",
                "generate_subtitles": True,
            },
        )
        assert resp.status_code == 202
        job_id = resp.json()["job_id"]
        status = (await client.get(f"/api/v1/video-studio/videos/jobs/{job_id}")).json()
        subtitle = status["subtitles"]
        assert subtitle["format"] == "srt"
        assert subtitle["cue_count"] == 1
        assert subtitle["download_url"].endswith("/downloads/subtitles/fake_0001.srt")
        downloaded = await client.get(subtitle["download_url"])
        assert downloaded.status_code == 200
        assert "Legenda de teste." in downloaded.text


class TestCharacterSelection:
    @pytest.mark.asyncio
    async def test_selected_characters_are_forwarded_to_generation_engine(
        self, client: AsyncClient, fake_engine: _FakeEngine
    ):
        response = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={
                "project_id": "p1",
                "prompt": "Mia e Leo explicam uma descoberta.",
                "studio_id": "whymentary",
                "character_ids": ["mia", "leo"],
            },
        )
        assert response.status_code == 202
        assert fake_engine.received is not None
        assert fake_engine.received["params"]["character_ids"] == ["mia", "leo"]

    @pytest.mark.asyncio
    async def test_duplicate_character_selection_is_rejected(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={
                "project_id": "p1",
                "prompt": "Teste",
                "character_ids": ["mia", "mia"],
            },
        )
        assert response.status_code == 422


class TestSceneObjectSelection:
    @pytest.mark.asyncio
    async def test_selected_objects_are_forwarded_to_generation_engine(
        self, client: AsyncClient, fake_engine: _FakeEngine
    ):
        response = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={
                "project_id": "p1",
                "prompt": "Mia mostra um copo de água.",
                "studio_id": "whymentary",
                "object_ids": ["water_glass", "thermometer"],
            },
        )
        assert response.status_code == 202
        assert fake_engine.received is not None
        assert fake_engine.received["params"]["object_ids"] == ["water_glass", "thermometer"]

    @pytest.mark.asyncio
    async def test_more_than_six_objects_are_rejected(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={
                "project_id": "p1",
                "prompt": "Teste",
                "object_ids": ["a", "b", "c", "d", "e", "f", "g"],
            },
        )
        assert response.status_code == 422


    @pytest.mark.asyncio
    async def test_duplicate_object_selection_is_rejected(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={
                "project_id": "p1",
                "prompt": "Teste",
                "object_ids": ["water_glass", "water_glass"],
            },
        )
        assert response.status_code == 422


class TestSceneVisualDirection:
    @pytest.mark.asyncio
    async def test_returns_scene_direction_without_exposing_internal_paths(
        self, client: AsyncClient, monkeypatch,
    ):
        from modules.ai_video_studio.api.routes import video

        monkeypatch.setitem(video._jobs, "visual_job", {
            "job_id": "visual_job",
            "status": "completed",
            "params": {"studio_id": "historical_documentary"},
            "_source_scenes": [
                {
                    "narration": "A descoberta revelou uma evidência importante.",
                    "visual_prompt": "",
                    "visual_prompt_suggestion": "Representar a evidência em primeiro plano.",
                    "visual_direction": "isole o documento; luz atmosférica.",
                    "narrative_beat": "revelation",
                    "shot_type": "detail",
                    "storyboard_scene_id": "scene-003-abc123",
                    "visual_prompt_full": "Prompt cinematográfico completo.",
                    "negative_prompt": "sem texto, sem marca d'água",
                    "continuity": {"characters": ["historical_narrator"], "objects": ["parchment_map"]},
                    "storyboard_status": "ready",
                    "background_image_path": "/private/path/scene.png",
                    "_source_scene_index": 2,
                },
            ],
            "scene_assets": [{
                "scene_index": 2,
                "image_url": "/downloads/images/scene.png",
                "status": "generated",
            }],
        })
        response = await client.get(
            "/api/v1/video-studio/videos/jobs/visual_job/visual-direction"
        )
        assert response.status_code == 200
        body = response.json()
        assert body["studio_id"] == "historical_documentary"
        assert body["scene_count"] == 1
        scene = body["scenes"][0]
        assert scene["scene_index"] == 2
        assert scene["narrative_beat"] == "revelation"
        assert scene["shot_type"] == "detail"
        assert scene["visual_prompt_suggestion"] == "Representar a evidência em primeiro plano."
        assert scene["storyboard_scene_id"] == "scene-003-abc123"
        assert scene["visual_prompt_full"] == "Prompt cinematográfico completo."
        assert scene["negative_prompt"] == "sem texto, sem marca d'água"
        assert scene["continuity"]["characters"] == ["historical_narrator"]
        assert scene["storyboard_status"] == "ready"
        assert scene["image_url"] == "/downloads/images/scene.png"
        assert "background_image_path" not in scene
        assert "/private/path" not in response.text

    @pytest.mark.asyncio
    async def test_rejects_visual_direction_before_job_completion(self, client: AsyncClient, monkeypatch):
        from modules.ai_video_studio.api.routes import video

        monkeypatch.setitem(video._jobs, "processing_visual_job", {
            "job_id": "processing_visual_job",
            "status": "processing",
            "params": {},
            "_source_scenes": [],
        })
        response = await client.get(
            "/api/v1/video-studio/videos/jobs/processing_visual_job/visual-direction"
        )
        assert response.status_code == 409

class TestBatchSceneImageRegeneration:
    @pytest.mark.asyncio
    async def test_regenerates_selected_scenes_sequentially_and_reports_partial_failures(
        self, client: AsyncClient, monkeypatch,
    ):
        from modules.ai_video_studio.api.routes import video

        monkeypatch.setitem(video._jobs, "batch_job", {
            "job_id": "batch_job", "status": "completed",
            "_source_scenes": [{"narration": "Cena 1"}, {"narration": "Cena 2"}],
        })
        calls: list[int] = []

        async def fake_edit(job_id, scene_index, req):
            calls.append(scene_index)
            if scene_index == 1:
                raise video.HTTPException(status_code=503, detail="image provider offline")
            return {
                "job_id": job_id, "scene_index": scene_index,
                "image_url": f"/images/{scene_index}.png", "status": "edited",
            }

        monkeypatch.setattr(video, "edit_video_job_scene_image", fake_edit)
        response = await client.post(
            "/api/v1/video-studio/videos/jobs/batch_job/scenes/regenerate",
            json={"scenes": [
                {"scene_index": 0, "prompt": "Plano geral da cena um"},
                {"scene_index": 1, "prompt": "Detalhe da cena dois"},
            ]},
        )

        assert response.status_code == 200
        body = response.json()
        assert calls == [0, 1]
        assert body["status"] == "partial"
        assert body["requested"] == 2
        assert body["succeeded"] == 1
        assert body["failed"] == 1
        assert body["results"][1]["error"] == "image provider offline"
        assert video._jobs["batch_job"].get("_scene_batch_running") is None

    @pytest.mark.asyncio
    async def test_rejects_duplicate_scene_indices_in_batch(self, client: AsyncClient, monkeypatch):
        from modules.ai_video_studio.api.routes import video

        monkeypatch.setitem(video._jobs, "duplicate_batch_job", {
            "job_id": "duplicate_batch_job", "status": "completed",
            "_source_scenes": [{"narration": "Cena 1"}],
        })
        response = await client.post(
            "/api/v1/video-studio/videos/jobs/duplicate_batch_job/scenes/regenerate",
            json={"scenes": [
                {"scene_index": 0, "prompt": "Primeira versão"},
                {"scene_index": 0, "prompt": "Segunda versão"},
            ]},
        )
        assert response.status_code == 422


class TestSceneImageCandidateApproval:
    @pytest.mark.asyncio
    async def test_candidate_is_only_applied_after_explicit_approval(self, client: AsyncClient, monkeypatch, tmp_path):
        from modules.ai_video_studio.api.routes import video
        from modules.ai_video_studio.media import output_paths

        image_root = tmp_path / "images"
        image_root.mkdir()
        candidate_path = image_root / "candidate.png"
        candidate_path.write_bytes(b"test-image-bytes")
        monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: image_root if name == "images" else tmp_path / name)
        monkeypatch.setitem(video._jobs, "approval_job", {
            "job_id": "approval_job", "status": "completed",
            "_source_scenes": [{"_source_scene_index": 0, "background_image_path": str(image_root / "old.png")}],
            "scene_image_candidates": {"0": [{"candidate_id": "candidate-123", "scene_index": 0,
                "image_path": str(candidate_path), "provider": "mock", "operation": "image_to_image",
                "prompt": "Uma floresta ao amanhecer", "negative_prompt": "texto, marca d'água",
                "status": "pending_approval"}]},
        })
        response = await client.post("/api/v1/video-studio/videos/jobs/approval_job/scenes/0/image-candidates/candidate-123/approve")
        assert response.status_code == 200
        assert response.json()["status"] == "approved"
        assert response.json()["render_required"] is True
        assert video._jobs["approval_job"]["_edited_scenes"][0]["background_image_path"] == str(candidate_path)
        assert video._jobs["approval_job"]["scene_image_candidates"] == {}

    @pytest.mark.asyncio
    async def test_unknown_candidate_cannot_replace_scene_image(self, client: AsyncClient, monkeypatch):
        from modules.ai_video_studio.api.routes import video
        monkeypatch.setitem(video._jobs, "missing_candidate_job", {
            "job_id": "missing_candidate_job", "status": "completed",
            "_source_scenes": [{"background_image_path": "/old.png"}],
            "scene_image_candidates": {"0": []},
        })
        response = await client.post("/api/v1/video-studio/videos/jobs/missing_candidate_job/scenes/0/image-candidates/not-found/approve")
        assert response.status_code == 404
        assert video._jobs["missing_candidate_job"]["_source_scenes"][0]["background_image_path"] == "/old.png"


class TestSceneImageSimilarityAnalysis:
    @pytest.mark.asyncio
    async def test_detects_pixel_identical_scene_images(self, client: AsyncClient, monkeypatch, tmp_path):
        from PIL import Image
        from modules.ai_video_studio.api.routes import video
        from modules.ai_video_studio.media import output_paths
        image_root = tmp_path / "images"
        image_root.mkdir()
        first, second = image_root / "scene-1.png", image_root / "scene-2.png"
        Image.new("RGB", (48, 48), (30, 100, 180)).save(first)
        Image.new("RGB", (48, 48), (30, 100, 180)).save(second)
        monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: image_root if name == "images" else tmp_path / name)
        monkeypatch.setitem(video._jobs, "similarity_job", {"job_id": "similarity_job", "status": "completed", "_source_scenes": [
            {"_source_scene_index": 0, "background_image_path": str(first)},
            {"_source_scene_index": 1, "background_image_path": str(second)},
        ]})
        response = await client.post("/api/v1/video-studio/videos/jobs/similarity_job/image-similarity-analysis")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "duplicates_found"
        assert body["duplicate_pairs"][0]["match_type"] == "exact"
        assert body["duplicate_pairs"][0]["scene_indices"] == [0, 1]

    @pytest.mark.asyncio
    async def test_rejects_scene_image_paths_outside_asset_directory(self, client: AsyncClient, monkeypatch, tmp_path):
        from modules.ai_video_studio.api.routes import video
        from modules.ai_video_studio.media import output_paths
        image_root = tmp_path / "images"
        image_root.mkdir()
        outside = tmp_path / "outside.png"
        outside.write_bytes(b"not-used")
        monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: image_root if name == "images" else tmp_path / name)
        monkeypatch.setitem(video._jobs, "unsafe_similarity_job", {"job_id": "unsafe_similarity_job", "status": "completed", "_source_scenes": [
            {"_source_scene_index": 4, "background_image_path": str(outside)},
        ]})
        response = await client.post("/api/v1/video-studio/videos/jobs/unsafe_similarity_job/image-similarity-analysis")
        assert response.status_code == 200
        assert response.json()["skipped_images"][0]["reason"] == "image_path_outside_asset_directory"


class TestSceneImageCandidateDiscard:
    @pytest.mark.asyncio
    async def test_discard_keeps_active_scene_image_unchanged(self, client: AsyncClient, monkeypatch):
        from modules.ai_video_studio.api.routes import video
        monkeypatch.setitem(video._jobs, "discard_candidate_job", {
            "job_id": "discard_candidate_job", "status": "completed",
            "_source_scenes": [{"background_image_path": "/active/current.png"}],
            "scene_image_candidates": {"0": [{"candidate_id": "discard-me", "image_path": "/candidate/new.png"}]},
        })
        response = await client.post("/api/v1/video-studio/videos/jobs/discard_candidate_job/scenes/0/image-candidates/discard-me/discard")
        assert response.status_code == 200
        assert response.json()["active_image_unchanged"] is True
        assert video._jobs["discard_candidate_job"]["_source_scenes"][0]["background_image_path"] == "/active/current.png"
        assert video._jobs["discard_candidate_job"]["scene_image_candidates"] == {}


# ── POST /videos/preflight ────────────────────────────────────────

class TestVideoPreflight:
    @pytest.mark.asyncio
    async def test_vidgrid_preflight_reports_exact_ten_second_clips(
        self, client: AsyncClient, monkeypatch
    ):
        monkeypatch.setattr(
            "modules.ai_video_studio.api.routes.video.shutil.which",
            lambda name: f"/usr/bin/{name}",
        )
        resp = await client.post(
            "/api/v1/video-studio/videos/preflight",
            json={
                "project_id": "preflight-project",
                "prompt": "documentary about ancient Egypt",
                "num_scenes": 42,
                "vidgrid_compatible": True,
                "frame_rate": 30,
            },
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["can_queue"] is True
        assert body["scene_count"] == 42
        assert body["duration_seconds"] == 420
        assert body["clip_duration_seconds"] == 10
        assert body["total_frames"] == 12600
        assert body["vidgrid_compatible"] is True
        assert any(item["id"] == "ffmpeg" and item["status"] == "ready" for item in body["checks"])

    @pytest.mark.asyncio
    async def test_preflight_blocks_mp4_generation_without_ffmpeg(
        self, client: AsyncClient, monkeypatch
    ):
        monkeypatch.setattr(
            "modules.ai_video_studio.api.routes.video.shutil.which",
            lambda name: None,
        )
        resp = await client.post(
            "/api/v1/video-studio/videos/preflight",
            json={"project_id": "preflight-project", "prompt": "a short film"},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["status"] == "blocked"
        assert body["can_queue"] is False
        assert any(item["id"] == "ffmpeg" for item in body["blockers"])


# ── Completed MP4 output validation ───────────────────────────────

class TestCompletedOutputValidation:
    @pytest.mark.asyncio
    async def test_validates_video_and_audio_streams_with_ffprobe(
        self, tmp_path, monkeypatch
    ):
        from types import SimpleNamespace
        from modules.ai_video_studio.api.routes import video as video_routes
        from modules.ai_video_studio.media import output_paths

        video_root = tmp_path / "videos"
        video_root.mkdir()
        output = video_root / "final.mp4"
        output.write_bytes(b"test-mp4")
        monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda _name: video_root)
        monkeypatch.setattr(video_routes.shutil, "which", lambda name: f"/usr/bin/{name}")
        monkeypatch.setattr(
            video_routes.subprocess, "run",
            lambda *args, **kwargs: SimpleNamespace(
                returncode=0, stderr="", stdout='{"format":{"duration":"30","format_name":"mov,mp4"},"streams":[{"codec_type":"video","codec_name":"h264","width":1280,"height":720,"avg_frame_rate":"24/1","r_frame_rate":"24/1","pix_fmt":"yuv420p"},{"codec_type":"audio","codec_name":"aac","sample_rate":"48000","channels":2}]}',
            ),
        )
        monkeypatch.setattr(video_routes, "_persist_job", lambda _record: None)
        video_routes._jobs["validate-job"] = {
            "job_id": "validate-job", "project_id": "p1", "status": "completed",
            "output_path": str(output), "video_duration": 30,
        }

        report = await video_routes.validate_video_job_output("validate-job")
        assert report["valid"] is True
        assert report["duration_seconds"] == 30
        assert report["video_streams"] == 1
        assert report["audio_streams"] == 1
        assert report["resolution"] == "1280x720"
        assert report["fps"] == "24/1"
        assert report["video_codec"] == "h264"
        assert report["audio"]["codec_name"] == "aac"
        assert report["integrity"] == "passed"
        assert video_routes._jobs["validate-job"]["output_validation"]["valid"] is True

    def test_job_status_response_exposes_persisted_output_validation(self):
        from modules.ai_video_studio.api.routes.video import VideoStatusResponse

        report = {
            "job_id": "persisted-job", "path_exists": True, "file_size_bytes": 4096,
            "ffprobe_available": True, "valid": True, "duration_seconds": 10.0,
            "video_streams": 1, "audio_streams": 1, "errors": [], "warnings": [],
        }
        response = VideoStatusResponse(
            job_id="persisted-job", status="completed", progress=1.0,
            output_validation=report,
        )
        assert response.model_dump()["output_validation"] == report
        scene_progress = [{"scene_index": 0, "status": "completed", "stage": "exported"}]
        response_with_scenes = VideoStatusResponse(
            job_id="persisted-job", status="completed", progress=1.0,
            scene_progress=scene_progress,
        )
        assert response_with_scenes.model_dump()["scene_progress"] == scene_progress

    @pytest.mark.asyncio
    async def test_rejects_output_path_outside_video_directory(self, tmp_path, monkeypatch):
        from modules.ai_video_studio.api.routes import video as video_routes
        from modules.ai_video_studio.media import output_paths
        from fastapi import HTTPException

        video_root = tmp_path / "videos"
        video_root.mkdir()
        outside = tmp_path / "outside.mp4"
        outside.write_bytes(b"not-allowed")
        monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda _name: video_root)
        video_routes._jobs["unsafe-validate-job"] = {
            "job_id": "unsafe-validate-job", "project_id": "p1",
            "status": "completed", "output_path": str(outside),
        }

        with pytest.raises(HTTPException) as error:
            await video_routes.validate_video_job_output("unsafe-validate-job")
        assert error.value.status_code == 422


class TestSceneAssetRenderLock:
    @pytest.mark.asyncio
    async def test_scene_image_edit_is_blocked_while_final_render_runs(self):
        from fastapi import HTTPException
        from modules.ai_video_studio.api.routes import video

        video._jobs["locked-scene-job"] = {
            "job_id": "locked-scene-job", "status": "completed",
            "_rendering_edits": True,
            "_source_scenes": [{"description": "scene", "background_image_path": None}],
        }
        with pytest.raises(HTTPException) as error:
            await video.edit_video_job_scene_image(
                "locked-scene-job", 0,
                video.SceneImageEditRequest(prompt="new visual"),
            )
        assert error.value.status_code == 409
        assert "rendering" in str(error.value.detail).lower()

    @pytest.mark.asyncio
    async def test_candidate_approval_is_blocked_while_batch_regeneration_runs(self):
        from fastapi import HTTPException
        from modules.ai_video_studio.api.routes import video

        video._scene_batch_jobs.add("locked-candidate-job")
        video._jobs["locked-candidate-job"] = {
            "job_id": "locked-candidate-job", "status": "completed",
            "scene_image_candidates": {"0": [{"candidate_id": "candidate-1"}]},
        }
        try:
            with pytest.raises(HTTPException) as error:
                await video.approve_video_job_scene_image(
                    "locked-candidate-job", 0, "candidate-1"
                )
            assert error.value.status_code == 409
        finally:
            video._scene_batch_jobs.discard("locked-candidate-job")

    @pytest.mark.asyncio
    async def test_final_render_waits_for_scene_batch(self):
        from fastapi import HTTPException
        from modules.ai_video_studio.api.routes import video

        video._scene_batch_jobs.add("batch-render-job")
        video._jobs["batch-render-job"] = {
            "job_id": "batch-render-job", "status": "completed",
            "_edited_scenes": [{"description": "scene"}],
        }
        try:
            with pytest.raises(HTTPException) as error:
                await video.render_video_job_edits("batch-render-job")
            assert error.value.status_code == 409
            assert "regeneration" in str(error.value.detail).lower()
        finally:
            video._scene_batch_jobs.discard("batch-render-job")



    @pytest.mark.asyncio
    async def test_final_export_rejects_stale_vidgrid_clips(self):
        from fastapi import HTTPException
        from modules.ai_video_studio.api.routes import video

        video._jobs["stale-final-export-job"] = {
            "job_id": "stale-final-export-job", "status": "completed",
            "vidgrid_compatible": True, "resolution": "1280x720", "frame_rate": 30,
            "params": {"resolution": "1280x720", "frame_rate": 30},
            "_edited_scenes": [{"_source_scene_index": 0, "duration": 10}],
            "scene_clips": [{"scene_index": 0, "status": "stale", "output_path": "old.mp4"}],
        }
        with pytest.raises(HTTPException) as error:
            await video.render_video_job_edits("stale-final-export-job")
        assert error.value.status_code == 409
        assert "stale" in str(error.value.detail).lower()

    @pytest.mark.asyncio
    async def test_recovery_plan_detects_changed_per_scene_narration(self, tmp_path, monkeypatch):
        from modules.ai_video_studio.api.routes import video
        from modules.ai_video_studio.media import output_paths

        roots = {name: tmp_path / name for name in ("images", "videos", "voice")}
        for root in roots.values():
            root.mkdir()
        image = roots["images"] / "scene.png"
        image.write_bytes(b"approved-image")
        clip = roots["videos"] / "scene.mp4"
        clip.write_bytes(b"scene-video")
        narration = roots["voice"] / "scene.wav"
        narration.write_bytes(b"new-narration")
        monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: roots[name])
        video._jobs["recovery-narration-changed"] = {
            "job_id": "recovery-narration-changed", "status": "completed",
            "vidgrid_compatible": True, "resolution": "1280x720", "frame_rate": 30,
            "params": {},
            "_edited_scenes": [{
                "_source_scene_index": 0, "background_image_path": str(image),
            }],
            "voiceover": {
                "narration_style": "per_scene",
                "clips": [{"index": 0, "audio_path": str(narration)}],
            },
            "scene_clips": [{
                "scene_index": 0, "status": "updated", "output_path": str(clip),
                "width": 1280, "height": 720, "fps": 30,
                "source_image_fingerprint": video._asset_sha256(image),
                "source_narration_fingerprint": "previous-narration-hash",
            }],
        }

        plan = await video.get_video_job_recovery_plan("recovery-narration-changed")

        assert plan["repair_scene_indices"] == [0]
        assert "source_narration_changed" in plan["scenes"][0]["reasons"]
        assert plan["scenes"][0]["source_narration_fingerprint"] == video._asset_sha256(narration)

    @pytest.mark.asyncio
    async def test_recovery_plan_detects_missing_clip_and_changed_image(self, tmp_path, monkeypatch):
        from modules.ai_video_studio.api.routes import video
        from modules.ai_video_studio.media import output_paths
        image_root, video_root = tmp_path / "images", tmp_path / "videos"
        image_root.mkdir()
        video_root.mkdir()
        image = image_root / "scene.png"
        image.write_bytes(b"new-approved-image")
        old_clip = video_root / "old.mp4"
        old_clip.write_bytes(b"existing-mp4")
        monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: image_root if name == "images" else video_root)
        video._jobs["recovery-plan-job"] = {
            "job_id": "recovery-plan-job", "status": "completed", "vidgrid_compatible": True,
            "resolution": "1280x720", "frame_rate": 30, "params": {},
            "_edited_scenes": [
                {"_source_scene_index": 0, "background_image_path": str(image)},
                {"_source_scene_index": 1, "background_image_path": str(image)},
            ],
            "scene_clips": [
                {"scene_index": 0, "status": "updated", "output_path": str(old_clip),
                 "width": 1280, "height": 720, "fps": 30, "source_image_fingerprint": "old-image-hash"},
            ],
        }
        plan = await video.get_video_job_recovery_plan("recovery-plan-job")
        assert plan["repair_scene_indices"] == [0, 1]
        assert plan["repairable_count"] == 2
        assert "source_image_changed" in plan["scenes"][0]["reasons"]
        assert "clip_missing" in plan["scenes"][1]["reasons"]

class TestSelectiveVidGridClipRebuild:
    @pytest.mark.asyncio
    async def test_rebuilds_only_stale_clip_and_reuses_approved_image(self, tmp_path, monkeypatch):
        from modules.ai_video_studio.api.routes import video
        from modules.ai_video_studio.media import output_paths, render

        image_root, video_root = tmp_path / "images", tmp_path / "videos"
        image_root.mkdir()
        (video_root / "vidgrid_clips").mkdir(parents=True)
        approved_image = image_root / "approved.png"
        approved_image.write_bytes(b"image")
        monkeypatch.setattr(output_paths, "get_subsystem_dir",
                            lambda name: image_root if name == "images" else video_root)

        def fake_unique(directory, prefix, extension):
            Path(directory).mkdir(parents=True, exist_ok=True)
            return Path(directory) / f"{prefix}.{extension}"

        monkeypatch.setattr(output_paths, "unique_filename", fake_unique)
        calls = []

        def fake_render(scene, output_path, **kwargs):
            calls.append(scene["description"])
            Path(output_path).write_bytes(b"rebuilt-mp4")
            return {"output_path": str(output_path), "engine": "test"}

        monkeypatch.setattr(render, "render_single_scene_clip", fake_render)
        current_clip = video_root / "current-1.mp4"
        current_clip.write_bytes(b"existing-mp4")
        monkeypatch.setattr(video, "_persist_job", lambda _record: None)
        video._jobs["selective-vidgrid-job"] = {
            "job_id": "selective-vidgrid-job", "status": "completed",
            "vidgrid_compatible": True, "resolution": "1280x720", "frame_rate": 30,
            "params": {"studio_id": "whymentary"},
            "_edited_scenes": [
                {"_source_scene_index": 0, "description": "scene zero",
                 "background_image_path": str(approved_image), "duration": 10},
                {"_source_scene_index": 1, "description": "scene one",
                 "background_image_path": str(approved_image), "duration": 10},
            ],
            "scene_clips": [
                {"scene_index": 0, "status": "stale", "output_path": "old-0.mp4"},
                {"scene_index": 1, "status": "updated", "output_path": str(current_clip)},
            ],
            "voiceover": {"narration_style": "none", "clips": []},
        }
        result = await video.rebuild_stale_video_job_scene_clips("selective-vidgrid-job")
        assert result["status"] == "completed"
        assert result["rebuilt"] == 1
        assert calls == ["scene zero"]
        clips = video._jobs["selective-vidgrid-job"]["scene_clips"]
        assert next(x for x in clips if x["scene_index"] == 1)["output_path"] == str(current_clip)
        rebuilt_clip = next(x for x in clips if x["scene_index"] == 0)
        assert rebuilt_clip["status"] == "updated"
        assert len(rebuilt_clip["source_image_fingerprint"]) == 64
        assert result["full_mp4_render_required"] is True

    @pytest.mark.asyncio
    async def test_rebuild_rejects_while_another_render_is_active(self):
        from fastapi import HTTPException
        from modules.ai_video_studio.api.routes import video

        video._jobs["busy-vidgrid-job"] = {
            "job_id": "busy-vidgrid-job", "status": "completed",
            "vidgrid_compatible": True, "_rendering_edits": True,
        }
        with pytest.raises(HTTPException) as error:
            await video.rebuild_stale_video_job_scene_clips("busy-vidgrid-job")
        assert error.value.status_code == 409

    @pytest.mark.asyncio
    async def test_batch_image_regeneration_rejects_during_stale_clip_rebuild(self):
        from fastapi import HTTPException
        from modules.ai_video_studio.api.routes import video

        video._jobs["batch-lock-vidgrid-job"] = {
            "job_id": "batch-lock-vidgrid-job", "status": "completed",
            "_rebuilding_scene_clips": True,
        }
        request = video.SceneImageBatchEditRequest(
            scenes=[{"scene_index": 0, "prompt": "A distinct educational background"}],
        )
        with pytest.raises(HTTPException) as error:
            await video.regenerate_video_job_scene_images("batch-lock-vidgrid-job", request)
        assert error.value.status_code == 409



class TestSelectedVidGridRecoveryQueue:
    @pytest.mark.asyncio
    async def test_rejects_selected_scene_that_does_not_need_rebuild(self, tmp_path, monkeypatch):
        from fastapi import HTTPException
        from modules.ai_video_studio.api.routes import video
        from modules.ai_video_studio.media import output_paths

        image_root, video_root = tmp_path / "images", tmp_path / "videos"
        image_root.mkdir()
        video_root.mkdir()
        image = image_root / "approved.png"
        image.write_bytes(b"approved-image")
        stale_clip = video_root / "stale.mp4"
        stale_clip.write_bytes(b"old-clip")
        ready_clip = video_root / "ready.mp4"
        ready_clip.write_bytes(b"ready-clip")
        monkeypatch.setattr(
            output_paths, "get_subsystem_dir",
            lambda name: image_root if name == "images" else video_root,
        )
        monkeypatch.setattr(video, "_persist_job", lambda _record: None)
        video._jobs["selected-recovery-job"] = {
            "job_id": "selected-recovery-job", "status": "completed",
            "vidgrid_compatible": True, "resolution": "1280x720", "frame_rate": 30,
            "params": {},
            "_edited_scenes": [
                {"_source_scene_index": 0, "background_image_path": str(image)},
                {"_source_scene_index": 1, "background_image_path": str(image)},
            ],
            "scene_clips": [
                {"scene_index": 0, "status": "stale", "output_path": str(stale_clip)},
                {"scene_index": 1, "status": "updated", "output_path": str(ready_clip)},
            ],
        }
        request = video.SceneClipRebuildRequest(scene_indices=[1])
        with pytest.raises(HTTPException) as error:
            await video.rebuild_stale_video_job_scene_clips("selected-recovery-job", request)
        assert error.value.status_code == 422
        assert error.value.detail["invalid_scene_indices"] == [1]


class TestDarkstudioAssetHealth:
    @pytest.mark.asyncio
    async def test_reports_missing_clip_and_available_scene_image(self, tmp_path, monkeypatch):
        from modules.ai_video_studio.api.routes import video
        monkeypatch.setattr(video.shutil, "which", lambda _name: None)
        from modules.ai_video_studio.media import output_paths

        roots = {name: tmp_path / name for name in ("images", "videos", "voice", "music", "effects")}
        for root in roots.values():
            root.mkdir()
        image = roots["images"] / "scene.png"
        image.write_bytes(b"image-bytes")
        clip = roots["videos"] / "scene.mp4"
        clip.write_bytes(b"video-bytes")
        monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: roots[name])
        video._jobs["asset-health-job"] = {
            "job_id": "asset-health-job", "status": "completed",
            "_edited_scenes": [
                {"_source_scene_index": 0, "background_image_path": str(image)},
                {"_source_scene_index": 1, "background_image_path": str(image)},
            ],
            "scene_clips": [{"scene_index": 0, "output_path": str(clip)}],
            "voiceover": {"narration_style": "single_track"},
        }

        report = await video.get_video_job_asset_health("asset-health-job")

        assert report["summary"]["total_assets"] == 4
        assert report["summary"]["available"] == 3
        assert report["summary"]["missing"] == 1
        assert report["scenes"][0]["status"] == "healthy"
        assert report["scenes"][1]["status"] == "needs_attention"
        assert report["status"] == "needs_attention"

    @pytest.mark.asyncio
    async def test_reports_stale_scene_image_when_clip_fingerprint_differs(self, tmp_path, monkeypatch):
        from modules.ai_video_studio.api.routes import video
        from modules.ai_video_studio.media import output_paths

        roots = {name: tmp_path / name for name in ("images", "videos", "voice", "music", "effects")}
        for root in roots.values():
            root.mkdir()
        image = roots["images"] / "approved.png"
        image.write_bytes(b"current-image")
        clip = roots["videos"] / "scene.mp4"
        clip.write_bytes(b"video-bytes")
        monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: roots[name])
        monkeypatch.setattr(video.shutil, "which", lambda _name: None)
        video._jobs["asset-health-stale-image"] = {
            "job_id": "asset-health-stale-image",
            "_edited_scenes": [{"_source_scene_index": 0, "background_image_path": str(image)}],
            "scene_clips": [{
                "scene_index": 0, "output_path": str(clip),
                "source_image_fingerprint": "previous-image-fingerprint",
            }],
        }

        report = await video.get_video_job_asset_health("asset-health-stale-image")
        image_asset = report["scenes"][0]["assets"][0]

        assert image_asset["status"] == "stale"
        assert image_asset["reason"] == "source_image_changed"
        assert report["status"] == "needs_attention"
        assert report["summary"]["stale"] == 1

    @pytest.mark.asyncio
    async def test_rejects_unknown_job(self):
        from fastapi import HTTPException
        from modules.ai_video_studio.api.routes import video

        with pytest.raises(HTTPException) as error:
            await video.get_video_job_asset_health("does-not-exist")
        assert error.value.status_code == 404


class TestMediaAssetProbe:
    def test_reports_unverified_when_ffprobe_is_unavailable(self, tmp_path, monkeypatch):
        from modules.ai_video_studio.api.routes import video

        monkeypatch.setattr(video.shutil, "which", lambda _name: None)
        result = video._probe_media_asset(tmp_path / "clip.mp4", "scene_clip")
        assert result["probe_status"] == "not_verified"

    def test_marks_media_corrupt_when_ffprobe_rejects_it(self, tmp_path, monkeypatch):
        from types import SimpleNamespace
        from modules.ai_video_studio.api.routes import video

        monkeypatch.setattr(video.shutil, "which", lambda _name: "/usr/bin/ffprobe")
        monkeypatch.setattr(
            video.subprocess, "run",
            lambda *args, **kwargs: SimpleNamespace(returncode=1, stderr="invalid data", stdout=""),
        )
        result = video._probe_media_asset(tmp_path / "broken.mp4", "scene_clip")
        assert result["status"] == "corrupt"
        assert result["reason"] == "ffprobe_rejected_media"


class TestAudioTimelineFingerprints:
    @pytest.mark.asyncio
    async def test_save_audio_timeline_persists_asset_fingerprint(self, tmp_path, monkeypatch):
        from modules.ai_video_studio.api.routes import video

        audio_file = tmp_path / "music.wav"
        audio_file.write_bytes(b"audio")
        monkeypatch.setattr(
            "modules.ai_video_studio.media.audio_timeline.validate_audio_asset",
            lambda _value: audio_file,
        )
        monkeypatch.setattr(video, "_asset_sha256", lambda _path: "saved-audio-sha256")
        monkeypatch.setattr(
            "modules.ai_video_studio.media.timeline.build_edit_timeline",
            lambda *args, **kwargs: {"duration_seconds": 10.0, "tracks": []},
        )
        monkeypatch.setattr(video, "_persist_job", lambda _record: None)
        record = {
            "job_id": "audio-fingerprint-save",
            "status": "completed",
            "_edited_scenes": [{"duration": 10.0}],
            "params": {"frame_rate": 24, "resolution": "1280x720"},
        }
        video._jobs["audio-fingerprint-save"] = record
        request = video.AudioTimelineEditRequest(
            music_clips=[{"asset": "music/music.wav", "end": 5.0}],
        )

        await video.update_video_job_audio("audio-fingerprint-save", request)

        assert record["_audio_clips"]["music"][0]["asset_fingerprint"] == "saved-audio-sha256"
        assert record["_audio_clips"]["sfx"] == []


class TestDependencyRebuildExecution:
    @pytest.mark.asyncio
    async def test_requires_explicit_confirmation(self):
        from fastapi import HTTPException
        from modules.ai_video_studio.api.routes import video

        video._jobs["dependency-execution-confirm"] = {"job_id": "dependency-execution-confirm", "status": "completed"}
        request = video.DependencyExecutionRequest(changed_asset_ids=["audio:music:0"], confirmed=False)
        with pytest.raises(HTTPException) as error:
            await video.execute_video_job_dependency_rebuild("dependency-execution-confirm", request)
        assert error.value.status_code == 409

    @pytest.mark.asyncio
    async def test_scene_change_rebuilds_only_affected_scene_before_final_render(self, monkeypatch):
        from modules.ai_video_studio.api.routes import video

        record = {
            "job_id": "dependency-execution-scene", "status": "completed",
            "vidgrid_compatible": True,
        }
        video._jobs["dependency-execution-scene"] = record
        impact = {
            "job_id": "dependency-execution-scene",
            "changed_asset_ids": ["scene:3:image"],
            "affected_nodes": [{"id": "scene:3:clip", "type": "video_clip", "status": "stale"}],
            "affected_node_ids": ["scene:3:clip", "final:export"],
            "rebuild_scene_indices": [3], "final_export_required": True,
        }
        calls = []
        monkeypatch.setattr(video, "preview_video_job_dependency_impact", lambda *_args: _async_result(impact))
        async def rebuild(_job_id, request):
            calls.append(("rebuild", request.scene_indices))
            return {"requested": 1, "rebuilt": 1, "failed": 0, "status": "completed"}
        async def render(_job_id):
            calls.append(("render", None))
            return {"output_url": "/downloads/rebuilt.mp4"}
        monkeypatch.setattr(video, "rebuild_stale_video_job_scene_clips", rebuild)
        monkeypatch.setattr(video, "render_video_job_edits", render)
        monkeypatch.setattr(video, "_persist_job", lambda _record: None)

        request = video.DependencyExecutionRequest(changed_asset_ids=["scene:3:image"], confirmed=True)
        result = await video.execute_video_job_dependency_rebuild("dependency-execution-scene", request)

        assert calls == [("rebuild", [3]), ("render", None)]
        assert result["status"] == "completed"
        assert result["render"]["output_url"] == "/downloads/rebuilt.mp4"

    @pytest.mark.asyncio
    async def test_partial_scene_rebuild_skips_final_render(self, monkeypatch):
        from modules.ai_video_studio.api.routes import video

        record = {
            "job_id": "dependency-execution-partial", "status": "completed",
            "vidgrid_compatible": True,
        }
        video._jobs["dependency-execution-partial"] = record
        impact = {
            "job_id": "dependency-execution-partial",
            "changed_asset_ids": ["scene:1:image"],
            "affected_nodes": [{"id": "scene:1:clip", "type": "video_clip", "status": "stale"}],
            "affected_node_ids": ["scene:1:clip", "final:export"],
            "rebuild_scene_indices": [1], "final_export_required": True,
        }
        monkeypatch.setattr(video, "preview_video_job_dependency_impact", lambda *_args: _async_result(impact))
        async def rebuild(*_args):
            return {"requested": 1, "rebuilt": 0, "failed": 1, "status": "failed"}
        async def fail_render(*_args):
            raise AssertionError("final render must not run after a partial scene rebuild")
        monkeypatch.setattr(video, "rebuild_stale_video_job_scene_clips", rebuild)
        monkeypatch.setattr(video, "render_video_job_edits", fail_render)
        monkeypatch.setattr(video, "_persist_job", lambda _record: None)

        request = video.DependencyExecutionRequest(changed_asset_ids=["scene:1:image"], confirmed=True)
        result = await video.execute_video_job_dependency_rebuild("dependency-execution-partial", request)

        assert result["status"] == "partial"
        assert result["render"] is None
        assert record["dependency_rebuild_execution"]["final_export_skipped"] is True


    @pytest.mark.asyncio
    async def test_audio_only_change_skips_scene_rebuild_and_renders_final(self, monkeypatch):
        from modules.ai_video_studio.api.routes import video

        record = {"job_id": "dependency-execution-audio", "status": "completed"}
        video._jobs["dependency-execution-audio"] = record
        impact = {
            "job_id": "dependency-execution-audio",
            "changed_asset_ids": ["audio:music:0"],
            "affected_nodes": [{"id": "final:export", "type": "final_export", "status": "available"}],
            "affected_node_ids": ["final:export"],
            "rebuild_scene_indices": [], "final_export_required": True,
        }
        monkeypatch.setattr(video, "preview_video_job_dependency_impact", lambda *_args: _async_result(impact))
        async def fail_rebuild(*_args):
            raise AssertionError("audio-only changes must not rebuild scene clips")
        async def render(*_args):
            return {"output_url": "/downloads/final.mp4", "message": "rendered"}
        monkeypatch.setattr(video, "rebuild_stale_video_job_scene_clips", fail_rebuild)
        monkeypatch.setattr(video, "render_video_job_edits", render)
        monkeypatch.setattr(video, "_persist_job", lambda _record: None)

        request = video.DependencyExecutionRequest(changed_asset_ids=["audio:music:0"], confirmed=True)
        result = await video.execute_video_job_dependency_rebuild("dependency-execution-audio", request)

        assert result["status"] == "completed"
        assert result["rebuild"] is None
        assert result["render"]["output_url"] == "/downloads/final.mp4"
        assert record["dependency_rebuild_execution"]["status"] == "completed"


class TestDarkstudioDependencyGraph:
    @pytest.mark.asyncio
    async def test_maps_scene_inputs_to_clip_and_final_export(self, tmp_path, monkeypatch):
        from modules.ai_video_studio.api.routes import video
        from modules.ai_video_studio.media import output_paths

        monkeypatch.setattr(video.shutil, "which", lambda _name: None)
        roots = {name: tmp_path / name for name in ("images", "videos", "voice", "music", "effects")}
        for root in roots.values():
            root.mkdir()
        image = roots["images"] / "scene.png"
        image.write_bytes(b"image")
        clip = roots["videos"] / "scene.mp4"
        clip.write_bytes(b"clip")
        final = roots["videos"] / "final.mp4"
        final.write_bytes(b"final")
        monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: roots[name])
        video._jobs["dependency-graph-job"] = {
            "job_id": "dependency-graph-job",
            "_edited_scenes": [{"_source_scene_index": 0, "background_image_path": str(image)}],
            "scene_clips": [{"scene_index": 0, "output_path": str(clip)}],
            "voiceover": {"narration_style": "per_scene", "clips": []},
            "output_path": str(final),
        }

        graph = await video.get_video_job_dependency_graph("dependency-graph-job")

        node_ids = {node["id"] for node in graph["nodes"]}
        assert {"scene:0:image", "scene:0:clip", "scene:0:narration", "final:export"} <= node_ids
        assert {"from": "scene:0:image", "to": "scene:0:clip", "relationship": "input_for"} in graph["edges"]
        assert {"from": "scene:0:clip", "to": "final:export", "relationship": "assembly_input"} in graph["edges"]
        assert graph["summary"]["dependencies"] == 3

    @pytest.mark.asyncio
    async def test_reads_canonical_audio_clips_and_includes_fingerprints(self, tmp_path, monkeypatch):
        from modules.ai_video_studio.api.routes import video
        from modules.ai_video_studio.media import output_paths

        roots = {name: tmp_path / name for name in ("images", "videos", "voice", "music", "effects")}
        for root in roots.values():
            root.mkdir()
        monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: roots[name])
        monkeypatch.setattr(
            video, "_audio_asset_health",
            lambda kind, value, root: {
                "kind": kind, "status": "available", "sha256": f"fingerprint-{Path(value).name}",
            },
        )
        video._jobs["dependency-graph-audio"] = {
            "job_id": "dependency-graph-audio",
            "_edited_scenes": [],
            "_audio_clips": {
                "music": [{"asset": "music/track.wav"}],
                "sfx": [{"asset": "effects/hit.wav"}],
            },
            "audio_settings": {"normalization_enabled": True},
        }

        graph = await video.get_video_job_dependency_graph("dependency-graph-audio")
        audio_nodes = {node["id"]: node for node in graph["nodes"] if node["type"] in {"music", "sound_effect"}}

        assert set(audio_nodes) == {"audio:music:0", "audio:sfx:0"}
        assert audio_nodes["audio:music:0"]["sha256"] == "fingerprint-track.wav"
        assert audio_nodes["audio:sfx:0"]["sha256"] == "fingerprint-hit.wav"
        assert graph["summary"]["dependencies"] == 2

    @pytest.mark.asyncio
    async def test_changed_scene_image_marks_source_node_stale(self, tmp_path, monkeypatch):
        from modules.ai_video_studio.api.routes import video
        from modules.ai_video_studio.media import output_paths

        roots = {name: tmp_path / name for name in ("images", "videos", "voice", "music", "effects")}
        for root in roots.values():
            root.mkdir()
        image = roots["images"] / "scene.png"
        image.write_bytes(b"new-approved-image")
        monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: roots[name])
        video._jobs["dependency-graph-image-stale"] = {
            "job_id": "dependency-graph-image-stale",
            "_edited_scenes": [{"_source_scene_index": 4, "background_image_path": str(image)}],
            "scene_clips": [{
                "scene_index": 4, "output_path": str(roots["videos"] / "clip.mp4"),
                "source_image_fingerprint": "old-image-fingerprint",
            }],
        }

        graph = await video.get_video_job_dependency_graph("dependency-graph-image-stale")
        image_node = next(node for node in graph["nodes"] if node["id"] == "scene:4:image")

        assert image_node["status"] == "stale"
        assert image_node["reason"] == "source_image_changed"

    @pytest.mark.asyncio
    async def test_dependency_graph_marks_changed_scene_narration_stale(self, tmp_path, monkeypatch):
        from modules.ai_video_studio.api.routes import video
        from modules.ai_video_studio.media import output_paths

        roots = {name: tmp_path / name for name in ("images", "videos", "voice", "music", "effects")}
        for root in roots.values():
            root.mkdir()
        image = roots["images"] / "scene.png"
        image.write_bytes(b"image")
        clip = roots["videos"] / "scene.mp4"
        clip.write_bytes(b"clip")
        narration = roots["voice"] / "scene.wav"
        narration.write_bytes(b"new-audio")
        monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: roots[name])
        video._jobs["dependency-graph-narration-stale"] = {
            "job_id": "dependency-graph-narration-stale",
            "_edited_scenes": [{"_source_scene_index": 2, "background_image_path": str(image)}],
            "voiceover": {
                "narration_style": "per_scene",
                "clips": [{"index": 2, "audio_path": str(narration)}],
            },
            "scene_clips": [{
                "scene_index": 2, "output_path": str(clip),
                "source_image_fingerprint": video._asset_sha256(image),
                "source_narration_fingerprint": "old-audio-hash",
            }],
        }

        graph = await video.get_video_job_dependency_graph("dependency-graph-narration-stale")
        narration_node = next(node for node in graph["nodes"] if node["id"] == "scene:2:narration")

        assert narration_node["status"] == "stale"
        assert narration_node["reason"] == "source_narration_changed"

    @pytest.mark.asyncio
    async def test_audio_fingerprint_mismatch_marks_dependency_stale(self, tmp_path, monkeypatch):
        from modules.ai_video_studio.api.routes import video
        from modules.ai_video_studio.media import output_paths

        roots = {name: tmp_path / name for name in ("images", "videos", "voice", "music", "effects")}
        for root in roots.values():
            root.mkdir()
        monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: roots[name])
        monkeypatch.setattr(
            video, "_audio_asset_health",
            lambda kind, value, root: {
                "kind": kind, "status": "available", "sha256": "current-fingerprint",
            },
        )
        video._jobs["dependency-graph-audio-stale"] = {
            "job_id": "dependency-graph-audio-stale",
            "_edited_scenes": [],
            "_audio_clips": {
                "music": [{"asset": "music/track.wav", "asset_fingerprint": "saved-fingerprint"}],
                "sfx": [],
            },
        }

        graph = await video.get_video_job_dependency_graph("dependency-graph-audio-stale")
        music = next(node for node in graph["nodes"] if node["id"] == "audio:music:0")

        assert music["status"] == "stale"
        assert music["reason"] == "asset_changed_since_timeline_save"
        assert music["sha256"] == "current-fingerprint"

    @pytest.mark.asyncio
    async def test_malformed_persisted_metadata_does_not_break_graph(self, tmp_path, monkeypatch):
        from modules.ai_video_studio.api.routes import video
        from modules.ai_video_studio.media import output_paths

        roots = {name: tmp_path / name for name in ("images", "videos", "voice", "music", "effects")}
        for root in roots.values():
            root.mkdir()
        monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: roots[name])
        video._jobs["dependency-graph-malformed"] = {
            "job_id": "dependency-graph-malformed",
            "_edited_scenes": [None, {"_source_scene_index": "not-an-index"}],
            "scene_clips": [{"scene_index": None}, None],
            "voiceover": {"narration_style": "per_scene", "clips": [{"index": None}, "bad-entry"]},
            "audio_settings": {
                "music_clips": [None, {"asset": None}],
                "sfx_clips": ["bad-entry"],
            },
        }

        graph = await video.get_video_job_dependency_graph("dependency-graph-malformed")

        assert graph["summary"]["nodes"] >= 3
        assert graph["summary"]["dependencies"] >= 1
        assert any(node["status"] == "missing" for node in graph["nodes"])

    @pytest.mark.asyncio
    async def test_dependency_impact_maps_image_to_scene_and_final_export(self, monkeypatch):
        from modules.ai_video_studio.api.routes import video

        async def fake_graph(_job_id):
            return {
                "nodes": [
                    {"id": "scene:2:image", "type": "image", "scene_index": 2},
                    {"id": "scene:2:clip", "type": "video_clip", "scene_index": 2},
                    {"id": "final:export", "type": "final_export", "scene_index": None},
                ],
                "edges": [
                    {"from": "scene:2:image", "to": "scene:2:clip"},
                    {"from": "scene:2:clip", "to": "final:export"},
                ],
            }

        monkeypatch.setattr(video, "get_video_job_dependency_graph", fake_graph)
        result = await video.preview_video_job_dependency_impact(
            "impact-job", video.DependencyImpactRequest(changed_asset_ids=["scene:2:image"])
        )

        assert result["rebuild_scene_indices"] == [2]
        assert result["final_export_required"] is True
        assert result["executed"] is False
        assert result["requires_user_confirmation"] is True

    @pytest.mark.asyncio
    async def test_dependency_impact_for_music_only_requires_final_export(self, monkeypatch):
        from modules.ai_video_studio.api.routes import video

        async def fake_graph(_job_id):
            return {
                "nodes": [
                    {"id": "audio:music_clips:0", "type": "music"},
                    {"id": "final:export", "type": "final_export"},
                ],
                "edges": [{"from": "audio:music_clips:0", "to": "final:export"}],
            }

        monkeypatch.setattr(video, "get_video_job_dependency_graph", fake_graph)
        result = await video.preview_video_job_dependency_impact(
            "impact-music-job",
            video.DependencyImpactRequest(changed_asset_ids=["audio:music_clips:0"]),
        )

        assert result["rebuild_scene_indices"] == []
        assert result["final_export_required"] is True
        assert [step["operation"] for step in result["rebuild_steps"]] == ["render_final_export"]

    @pytest.mark.asyncio
    async def test_dependency_impact_rejects_unknown_asset(self, monkeypatch):
        from fastapi import HTTPException
        from modules.ai_video_studio.api.routes import video

        async def fake_graph(_job_id):
            return {"nodes": [{"id": "final:export", "type": "final_export"}], "edges": []}

        monkeypatch.setattr(video, "get_video_job_dependency_graph", fake_graph)
        with pytest.raises(HTTPException) as error:
            await video.preview_video_job_dependency_impact(
                "impact-job", video.DependencyImpactRequest(changed_asset_ids=["missing"])
            )
        assert error.value.status_code == 422

    @pytest.mark.asyncio
    async def test_rejects_unknown_job(self):
        from fastapi import HTTPException
        from modules.ai_video_studio.api.routes import video

        with pytest.raises(HTTPException) as error:
            await video.get_video_job_dependency_graph("missing-dependency-job")
        assert error.value.status_code == 404
