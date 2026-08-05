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
