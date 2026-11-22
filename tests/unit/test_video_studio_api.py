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

    async def generate_async(self, job: dict, progress_callback=None, scene_callback=None) -> dict:
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
    # Mirror the real modules/downloads tree so to_download_url accepts fixture assets.
    fake_root = tmp_path / "modules" / "downloads"
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

class TestVidGridFinalExportRecovery:
    def test_ordered_clip_paths_reject_missing_and_unsafe_files(self, tmp_path, monkeypatch):
        from fastapi import HTTPException
        from modules.ai_video_studio.api.routes import video
        from modules.ai_video_studio.media import output_paths

        video_root = tmp_path / "videos"
        video_root.mkdir()
        monkeypatch.setattr(output_paths, "DOWNLOADS_DIR", tmp_path)
        monkeypatch.setattr(output_paths, "_SUBDIRS", {**output_paths._SUBDIRS, "videos": "videos"})
        outside = tmp_path / "outside.mp4"
        outside.write_bytes(b"not allowed")
        record = {"scene_clips": [
            {"scene_index": 0, "status": "ready", "output_path": str(outside)}
        ]}
        with pytest.raises(HTTPException) as exc:
            video._ordered_vidgrid_clip_paths(record, [{"_source_scene_index": 0}])
        assert exc.value.status_code == 409

    def test_per_scene_narration_missing_or_unmuxed_blocks_vidgrid_clip(self, tmp_path, monkeypatch):
        from fastapi import HTTPException
        from modules.ai_video_studio.api.routes import video
        from modules.ai_video_studio.media import output_paths

        video_root = tmp_path / "videos"
        voice_root = tmp_path / "voice"
        video_root.mkdir()
        voice_root.mkdir()
        clip_path = video_root / "scene.mp4"
        clip_path.write_bytes(b"fake-mp4")
        monkeypatch.setattr(output_paths, "DOWNLOADS_DIR", tmp_path)
        monkeypatch.setattr(output_paths, "_SUBDIRS", {
            **output_paths._SUBDIRS, "videos": "videos", "voice": "voice",
        })
        monkeypatch.setattr(video, "_probe_media_asset", lambda *_: {
            "probe_status": "not_verified",
        })
        base = {
            "scene_clips": [{
                "scene_index": 0, "status": "ready",
                "output_path": str(clip_path), "duration": 10.0,
                "audio_status": "silent_or_tts_unavailable",
            }],
            "voiceover": {
                "narration_style": "per_scene",
                "clips": [{"index": 0, "audio_path": None}],
            },
        }
        with pytest.raises(HTTPException) as missing:
            video._ordered_vidgrid_clip_paths(base, [{"_source_scene_index": 0}])
        assert missing.value.status_code == 409

        narration_path = voice_root / "scene.wav"
        narration_path.write_bytes(b"audio")
        base["voiceover"]["clips"][0]["audio_path"] = str(narration_path)
        with pytest.raises(HTTPException) as unmuxed:
            video._ordered_vidgrid_clip_paths(base, [{"_source_scene_index": 0}])
        assert unmuxed.value.status_code == 409

    def test_single_track_narration_cannot_mark_individual_vidgrid_clips_ready(self, tmp_path, monkeypatch):
        from fastapi import HTTPException
        from modules.ai_video_studio.api.routes import video
        from modules.ai_video_studio.media import output_paths

        video_root = tmp_path / "videos"
        video_root.mkdir()
        clip_path = video_root / "scene.mp4"
        clip_path.write_bytes(b"fake-mp4")
        master_audio = tmp_path / "master.wav"
        master_audio.write_bytes(b"audio")
        monkeypatch.setattr(output_paths, "DOWNLOADS_DIR", tmp_path)
        monkeypatch.setattr(output_paths, "_SUBDIRS", {**output_paths._SUBDIRS, "videos": "videos"})
        monkeypatch.setattr(video, "_probe_media_asset", lambda *_: {"probe_status": "not_verified"})
        record = {
            "scene_clips": [{
                "scene_index": 0, "status": "ready",
                "output_path": str(clip_path), "duration": 10.0,
            }],
            "voiceover": {
                "narration_style": "single_track",
                "output_path": str(master_audio), "muxed": True,
            },
        }
        with pytest.raises(HTTPException) as exc:
            video._ordered_vidgrid_clip_paths(record, [{"_source_scene_index": 0}])
        assert exc.value.status_code == 409

    def test_ordered_clip_paths_preserve_scene_order(self, tmp_path, monkeypatch):
        from modules.ai_video_studio.api.routes import video
        from modules.ai_video_studio.media import output_paths

        # These fixtures are placeholder bytes, not valid MP4 containers.
        # Keep this unit test focused on path safety and scene ordering.
        monkeypatch.setattr(video, "_probe_media_asset", lambda *_: {"probe_status": "not_verified"})
        video_root = tmp_path / "videos"
        video_root.mkdir()
        monkeypatch.setattr(output_paths, "DOWNLOADS_DIR", tmp_path)
        monkeypatch.setattr(output_paths, "_SUBDIRS", {**output_paths._SUBDIRS, "videos": "videos"})
        first, second = video_root / "first.mp4", video_root / "second.mp4"
        first.write_bytes(b"clip-1")
        second.write_bytes(b"clip-2")
        record = {"scene_clips": [
            {"scene_index": 1, "status": "ready", "output_path": str(second)},
            {"scene_index": 0, "status": "updated", "output_path": str(first)},
        ]}
        assert video._ordered_vidgrid_clip_paths(
            record, [{"_source_scene_index": 0}, {"_source_scene_index": 1}]
        ) == [str(first.resolve()), str(second.resolve())]


class TestFailedVidGridRecovery:
    def test_recovery_plan_allows_procedural_scene_without_image(self, tmp_path, monkeypatch):
        from modules.ai_video_studio.api.routes.video import _scene_clip_recovery_plan
        from modules.ai_video_studio.media import output_paths

        monkeypatch.setattr(output_paths, "DOWNLOADS_DIR", tmp_path / "downloads")
        record = {
            "status": "failed", "vidgrid_compatible": True,
            "resolution": "1280x720", "frame_rate": 24,
            "params": {"scene_image_mode": "procedural"},
            "_edited_scenes": [
                {"_source_scene_index": 0, "description": "Cena procedural", "duration": 10.0}
            ],
            "scene_clips": [], "scene_assets": [],
        }
        plan = _scene_clip_recovery_plan(record)
        assert plan["repair_scene_indices"] == [0]
        assert plan["blocked_count"] == 0
        assert "procedural_scene_without_image_asset" in plan["scenes"][0]["warnings"]

    def test_failed_vidgrid_job_keeps_mode_metadata_at_creation(self):
        from modules.ai_video_studio.api.routes.video import VideoGenerateRequest

        request = VideoGenerateRequest(
            project_id="p1", prompt="A test scene", vidgrid_compatible=True,
            scene_image_mode="procedural",
        )
        assert request.vidgrid_compatible is True
        assert request.scene_image_mode == "procedural"
        assert request.studio_id == "custom"


class TestSceneCheckpointPersistence:
    def test_scene_snapshot_and_assets_are_merged_without_overwriting_other_scenes(self, monkeypatch, tmp_path):
        from modules.ai_video_studio.api.routes.video import _merge_scene_checkpoint
        from modules.ai_video_studio.media import output_paths

        downloads_root = tmp_path / "downloads"
        video_root = downloads_root / "videos"
        video_root.mkdir(parents=True)
        clip_path = video_root / "scene-2.mp4"
        clip_path.write_bytes(b"test-clip")
        monkeypatch.setattr(output_paths, "DOWNLOADS_DIR", downloads_root)
        record = {
            "_source_scenes": [{"title": "Cena 1", "_source_scene_index": 0}],
            "_edited_scenes": [{"title": "Cena 1", "_source_scene_index": 0}],
            "scene_assets": [],
            "scene_clips": [],
        }
        _merge_scene_checkpoint(record, {
            "scene_index": 1,
            "scene_snapshot": {"title": "Cena 2", "visual_prompt": "Uma cidade ao amanhecer"},
            "image_path": str(tmp_path / "scene-2.png"),
            "image_provider": "local_diffusion",
            "image_seed": 123,
            "clip_path": str(clip_path),
            "clip_bytes": 456,
        })

        assert record["_source_scenes"][0]["title"] == "Cena 1"
        assert record["_source_scenes"][1]["title"] == "Cena 2"
        assert record["_edited_scenes"][1]["visual_prompt"] == "Uma cidade ao amanhecer"
        assert record["scene_assets"][0]["scene_index"] == 1
        assert record["scene_assets"][0]["provider"] == "local_diffusion"
        assert record["scene_assets"][0]["seed"] == 123
        assert record["scene_clips"][0]["output_path"] == str(clip_path.resolve())
        assert record["scene_clips"][0]["bytes"] == 456

    def test_invalid_scene_checkpoint_is_ignored(self):
        from modules.ai_video_studio.api.routes.video import _merge_scene_checkpoint

        record = {"_source_scenes": []}
        _merge_scene_checkpoint(record, {"scene_index": "invalid", "scene_snapshot": {"title": "x"}})
        _merge_scene_checkpoint(record, {"scene_index": -1, "scene_snapshot": {"title": "x"}})
        assert record["_source_scenes"] == []


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

        async def _fake(self, job: dict, progress_callback=None, scene_callback=None) -> dict:
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
        assert status["project_id"] == "p1"
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
        async def _fake(self, job: dict, progress_callback=None, scene_callback=None) -> dict:
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

        async def _fake(self, job: dict, progress_callback=None, scene_callback=None) -> dict:
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

        async def _fake(self, job: dict, progress_callback=None, scene_callback=None) -> dict:
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
        async def _boom(self, job: dict, progress_callback=None, scene_callback=None) -> dict:
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
        assert resp.headers["content-disposition"].startswith("inline;")

        download = await client.get(
            f"/api/v1/video-studio/downloads/videos/{filename}?download=true"
        )
        assert download.status_code == 200
        assert download.headers["content-disposition"].startswith("attachment;")

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

    @pytest.mark.asyncio
    async def test_download_rejects_parent_directory_as_kind(self, tmp_path, monkeypatch):
        from fastapi import HTTPException
        from modules.ai_video_studio.api.routes import generation

        downloads = tmp_path / "downloads"
        downloads.mkdir()
        secret = tmp_path / "secret.txt"
        secret.write_text("must not be served", encoding="utf-8")
        monkeypatch.setattr(generation, "DOWNLOADS_DIR", downloads)

        with pytest.raises(HTTPException) as exc:
            await generation.download_media("..", "secret.txt")
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_download_rejects_symlink_outside_download_root(self, tmp_path, monkeypatch):
        from fastapi import HTTPException
        from modules.ai_video_studio.api.routes import generation

        downloads = tmp_path / "downloads"
        video_dir = downloads / "videos"
        video_dir.mkdir(parents=True)
        outside = tmp_path / "private.mp4"
        outside.write_bytes(b"private")
        link = video_dir / "linked.mp4"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            pytest.skip("Symlinks are not available in this environment")
        monkeypatch.setattr(generation, "DOWNLOADS_DIR", downloads)

        with pytest.raises(HTTPException) as exc:
            await generation.download_media("videos", "linked.mp4")
        assert exc.value.status_code == 404


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
    async def test_felt_clay_studio_profile_reaches_render_engine(
        self, client: AsyncClient, fake_engine: _FakeEngine
    ):
        resp = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={
                "project_id": "p1",
                "prompt": "Mia e Leo explicam um tema de saúde em feltro",
                "studio_id": "felt_clay",
            },
        )
        assert resp.status_code == 202
        assert fake_engine.received is not None
        assert fake_engine.received["params"]["studio_id"] == "felt_clay"

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_omitted_studio_uses_universal_custom_profile(
        self, client: AsyncClient, fake_engine: _FakeEngine
    ):
        response = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={"project_id": "p1", "prompt": "A documentary about ocean exploration."},
        )
        assert response.status_code == 202
        assert fake_engine.received is not None
        assert fake_engine.received["params"]["studio_id"] == "custom"

    async def test_custom_prompt_studio_is_accepted_and_forwarded(
        self, client: AsyncClient, fake_engine: _FakeEngine
    ):
        resp = await client.post(
            "/api/v1/video-studio/videos/generate",
            json={
                "project_id": "p1",
                "prompt": "Um anúncio futurista com estética de aquarela e neon.",
                "studio_id": "custom",
                "style": "Aquarela digital, neon ciano e magenta, atmosfera futurista",
            },
        )
        assert resp.status_code == 202
        assert fake_engine.received is not None
        assert fake_engine.received["params"]["studio_id"] == "custom"
        assert fake_engine.received["params"]["style"] == "Aquarela digital, neon ciano e magenta, atmosfera futurista"

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
            "job_id": "batch_job", "project_id": "batch_project", "status": "completed",
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
            "job_id": "approval_job", "project_id": "approval_project", "status": "completed",
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
        monkeypatch.setitem(video._jobs, "similarity_job", {"job_id": "similarity_job", "project_id": "similarity_project", "status": "completed", "_source_scenes": [
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
        monkeypatch.setitem(video._jobs, "unsafe_similarity_job", {"job_id": "unsafe_similarity_job", "project_id": "unsafe_similarity_project", "status": "completed", "_source_scenes": [
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
            "job_id": "discard_candidate_job", "project_id": "discard_candidate_project", "status": "completed",
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
        monkeypatch.setattr(
            "modules.ai_video_studio.api.routes.video._probe_image_api",
            lambda _url: (True, None),
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
        monkeypatch.setattr(
            "modules.ai_video_studio.api.routes.video._probe_image_api",
            lambda _url: (False, "API offline"),
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

    @pytest.mark.asyncio
    async def test_ai_image_mode_blocks_when_local_provider_is_unavailable(
        self, client: AsyncClient, monkeypatch
    ):
        monkeypatch.setattr(
            "modules.ai_video_studio.api.routes.video.shutil.which",
            lambda name: f"/usr/bin/{name}",
        )
        monkeypatch.setattr(
            "modules.ai_video_studio.api.routes.video._probe_image_api",
            lambda _url: (False, "API offline"),
        )
        response = await client.post(
            "/api/v1/video-studio/videos/preflight",
            json={"project_id": "ai-provider-offline", "prompt": "A cinematic forest", "scene_image_mode": "ai"},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["can_queue"] is False
        assert any(item["id"] == "image_provider" and item["status"] == "blocked" for item in body["blockers"])

    @pytest.mark.asyncio
    async def test_auto_image_mode_warns_and_keeps_procedural_fallback(
        self, client: AsyncClient, monkeypatch
    ):
        monkeypatch.setattr(
            "modules.ai_video_studio.api.routes.video.shutil.which",
            lambda name: f"/usr/bin/{name}",
        )
        monkeypatch.setattr(
            "modules.ai_video_studio.api.routes.video._probe_image_api",
            lambda _url: (False, "API offline"),
        )
        response = await client.post(
            "/api/v1/video-studio/videos/preflight",
            json={"project_id": "auto-provider-offline", "prompt": "A cinematic forest", "scene_image_mode": "auto"},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["can_queue"] is True
        check = next(item for item in body["checks"] if item["id"] == "image_provider")
        assert check["status"] == "warning"
        assert "procedurais" in check["message"]


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

    @pytest.mark.asyncio
    async def test_validation_rejects_resolution_and_fps_mismatch(self, tmp_path, monkeypatch):
        from types import SimpleNamespace
        from modules.ai_video_studio.api.routes import video as video_routes
        from modules.ai_video_studio.media import output_paths

        root = tmp_path / "videos"
        root.mkdir()
        output = root / "wrong-profile.mp4"
        output.write_bytes(b"mp4")
        monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda _name: root)
        monkeypatch.setattr(video_routes.shutil, "which", lambda name: f"/usr/bin/{name}")
        monkeypatch.setattr(
            video_routes.subprocess, "run",
            lambda *args, **kwargs: SimpleNamespace(
                returncode=0, stderr="",
                stdout='{"format":{"duration":"12","format_name":"mov,mp4"},"streams":[{"codec_type":"video","codec_name":"h264","width":640,"height":360,"avg_frame_rate":"30/1"}]}',
            ),
        )
        monkeypatch.setattr(video_routes, "_persist_job", lambda _record: None)
        video_routes._jobs["wrong-profile-validation"] = {
            "job_id": "wrong-profile-validation", "status": "completed",
            "output_path": str(output), "resolution": "1280x720", "frame_rate": 24,
            "params": {"resolution": "1280x720", "frame_rate": 24},
        }

        report = await video_routes.validate_video_job_output("wrong-profile-validation")

        assert report["valid"] is False
        assert any("Resolução final 640x360" in error for error in report["errors"])
        assert any("FPS final 30.000" in error for error in report["errors"])


    @pytest.mark.asyncio
    async def test_edited_vidgrid_validation_uses_final_timeline_duration(self, tmp_path, monkeypatch):
        from types import SimpleNamespace
        from modules.ai_video_studio.api.routes import video as video_routes
        from modules.ai_video_studio.media import output_paths

        root = tmp_path / "videos"
        root.mkdir()
        output = root / "edited.mp4"
        output.write_bytes(b"mp4")
        monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda _name: root)
        monkeypatch.setattr(video_routes.shutil, "which", lambda name: f"/usr/bin/{name}")
        monkeypatch.setattr(
            video_routes.subprocess, "run",
            lambda *args, **kwargs: SimpleNamespace(
                returncode=0, stderr="",
                stdout='{"format":{"duration":"20"},"streams":[{"codec_type":"video","codec_name":"h264","width":1280,"height":720,"avg_frame_rate":"24/1"}]}',
            ),
        )
        monkeypatch.setattr(video_routes, "_persist_job", lambda _record: None)
        video_routes._jobs["edited-vidgrid-duration"] = {
            "job_id": "edited-vidgrid-duration", "project_id": "p1",
            "status": "completed", "vidgrid_compatible": True,
            "edited_output_path": str(output), "edited_video_duration": 20,
            "clip_duration_seconds": 10,
            "scene_clips": [{"scene_index": index} for index in range(4)],
            "edit_export_manifest": {"video_frames": 480, "target_fps": 24},
            "edit_render_audio": "silent",
        }

        report = await video_routes.validate_video_job_output("edited-vidgrid-duration")

        assert report["expected_duration_seconds"] == 20
        assert not any("Duração medida" in warning for warning in report["warnings"])
        assert report["valid"] is True

    @pytest.mark.asyncio
    async def test_requested_voiceover_without_audio_stream_is_invalid(self, tmp_path, monkeypatch):
        from types import SimpleNamespace
        from modules.ai_video_studio.api.routes import video as video_routes
        from modules.ai_video_studio.media import output_paths

        root = tmp_path / "videos"
        root.mkdir()
        output = root / "silent.mp4"
        output.write_bytes(b"mp4")
        monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda _name: root)
        monkeypatch.setattr(video_routes.shutil, "which", lambda name: f"/usr/bin/{name}")
        monkeypatch.setattr(
            video_routes.subprocess, "run",
            lambda *args, **kwargs: SimpleNamespace(
                returncode=0, stderr="",
                stdout='{"format":{"duration":"12"},"streams":[{"codec_type":"video","codec_name":"h264","width":1280,"height":720}]}',
            ),
        )
        monkeypatch.setattr(video_routes, "_persist_job", lambda _record: None)
        video_routes._jobs["missing-audio-job"] = {
            "job_id": "missing-audio-job", "project_id": "p1",
            "status": "completed", "output_path": str(output),
            "params": {"voiceover": True},
        }

        report = await video_routes.validate_video_job_output("missing-audio-job")
        assert report["audio_expected"] is True
        assert report["audio_streams"] == 0
        assert report["valid"] is False

    @pytest.mark.asyncio
    async def test_music_only_edited_export_without_audio_stream_is_invalid(self, tmp_path, monkeypatch):
        from types import SimpleNamespace
        from modules.ai_video_studio.api.routes import video as video_routes
        from modules.ai_video_studio.media import output_paths

        root = tmp_path / "videos"
        root.mkdir()
        output = root / "music-missing.mp4"
        output.write_bytes(b"mp4")
        monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda _name: root)
        monkeypatch.setattr(video_routes.shutil, "which", lambda name: f"/usr/bin/{name}")
        monkeypatch.setattr(
            video_routes.subprocess, "run",
            lambda *args, **kwargs: SimpleNamespace(
                returncode=0, stderr="",
                stdout='{"format":{"duration":"12"},"streams":[{"codec_type":"video","codec_name":"h264","width":1280,"height":720}]}',
            ),
        )
        monkeypatch.setattr(video_routes, "_persist_job", lambda _record: None)
        video_routes._jobs["music-missing-audio-job"] = {
            "job_id": "music-missing-audio-job", "project_id": "p1",
            "status": "completed", "edited_output_path": str(output),
            "params": {"voiceover": False},
            "edit_render_audio": "mixed_audio",
        }

        report = await video_routes.validate_video_job_output("music-missing-audio-job")

        assert report["audio_expected"] is True
        assert report["audio_streams"] == 0
        assert report["valid"] is False
        assert any("não contém áudio" in item for item in report["errors"])

    @pytest.mark.asyncio
    async def test_intentionally_silent_edit_can_validate_without_audio(self, tmp_path, monkeypatch):
        from types import SimpleNamespace
        from modules.ai_video_studio.api.routes import video as video_routes
        from modules.ai_video_studio.media import output_paths

        root = tmp_path / "videos"
        root.mkdir()
        output = root / "silent-edit.mp4"
        output.write_bytes(b"mp4")
        monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda _name: root)
        monkeypatch.setattr(video_routes.shutil, "which", lambda name: f"/usr/bin/{name}")
        monkeypatch.setattr(
            video_routes.subprocess, "run",
            lambda *args, **kwargs: SimpleNamespace(
                returncode=0, stderr="",
                stdout='{"format":{"duration":"12"},"streams":[{"codec_type":"video","codec_name":"h264","width":1280,"height":720}]}',
            ),
        )
        monkeypatch.setattr(video_routes, "_persist_job", lambda _record: None)
        video_routes._jobs["intentional-silence-job"] = {
            "job_id": "intentional-silence-job", "project_id": "p1",
            "status": "completed", "output_path": str(output),
            "params": {"voiceover": True}, "edit_render_audio": "silent",
        }

        report = await video_routes.validate_video_job_output("intentional-silence-job")
        assert report["audio_expected"] is False
        assert report["valid"] is True

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
        recovery = {"kind": "server_restart", "can_retry_export": True, "scene_assets_preserved": True}
        response_with_recovery = VideoStatusResponse(
            job_id="persisted-job", status="completed", progress=1.0,
            edit_render_status="interrupted", edit_render_recovery=recovery,
        )
        assert response_with_recovery.model_dump()["edit_render_recovery"] == recovery
        scene_progress = [{"scene_index": 0, "status": "completed", "stage": "exported"}]
        response_with_scenes = VideoStatusResponse(
            job_id="persisted-job", status="completed", progress=1.0,
            scene_progress=scene_progress,
        )
        assert response_with_scenes.model_dump()["scene_progress"] == scene_progress

    def test_interrupted_job_records_last_completed_and_active_scene(self, monkeypatch):
        from modules.ai_video_studio.media import job_store

        saved = []
        monkeypatch.setattr(job_store, "save_job", lambda record: saved.append(dict(record)))
        jobs = {
            "restart-job": {
                "job_id": "restart-job", "project_id": "p1", "status": "processing",
                "current_step": "Cena 3: rendering frames",
                "scene_progress": [
                    {"scene_index": 0, "status": "completed", "stage": "exported"},
                    {"scene_index": 1, "status": "completed", "stage": "exported"},
                    {"scene_index": 2, "status": "processing", "stage": "rendering"},
                ],
            }
        }

        recovered = job_store.mark_interrupted_jobs(jobs)
        failure = jobs["restart-job"]["failure_info"]

        assert recovered == ["restart-job"]
        assert jobs["restart-job"]["status"] == "failed"
        assert failure["kind"] == "server_restart"
        assert failure["failed_stage"] == "Cena 3: rendering frames"
        assert failure["failed_scene_index"] == 2
        assert failure["last_completed_scene_index"] == 1
        assert failure["completed_scene_indices"] == [0, 1]
        assert failure["automatic_resume_supported"] is False
        assert saved[0]["failure_info"] == failure

    def test_interrupted_vidgrid_export_is_not_retryable_without_source_clips(self, monkeypatch, tmp_path):
        from modules.ai_video_studio.media import job_store, output_paths
        video_root = tmp_path / "videos"
        video_root.mkdir()
        monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda _name: video_root)
        monkeypatch.setattr(job_store, "save_job", lambda _record: None)
        jobs = {"vidgrid": {"job_id": "vidgrid", "project_id": "p1", "vidgrid_compatible": True, "edit_render_status": "rendering", "_edited_scenes": [{"_source_scene_index": 0}], "scene_clips": [{"scene_index": 0, "output_path": str(video_root / "missing.mp4")}]}}
        job_store.mark_interrupted_edit_renders(jobs)
        recovery = jobs["vidgrid"]["edit_render_recovery"]
        assert recovery["can_retry_export"] is False
        assert recovery["scene_records_preserved"] is True
        assert recovery["scene_assets_preserved"] is False

    def test_interrupted_edit_export_is_recoverable_without_rebuilding_scenes(self, monkeypatch):
        from modules.ai_video_studio.media import job_store

        saved = []
        monkeypatch.setattr(job_store, "save_job", lambda record: saved.append(dict(record)))
        jobs = {
            "edit-restart": {
                "job_id": "edit-restart", "project_id": "p1", "status": "completed",
                "edit_render_status": "rendering",
                "_rendering_edits": True,
                "_edited_scenes": [{"description": "scene", "image_path": "scene.png"}],
                "scene_clips": [{"scene_index": 0, "status": "completed", "clip_path": "clip.mp4"}],
            },
            "already-done": {
                "job_id": "already-done", "project_id": "p1", "status": "completed",
                "edit_render_status": "completed",
            },
        }

        recovered = job_store.mark_interrupted_edit_renders(jobs)

        assert recovered == ["edit-restart"]
        record = jobs["edit-restart"]
        assert record["edit_render_status"] == "interrupted"
        assert record["_rendering_edits"] is False
        assert saved[0]["_rendering_edits"] is False
        assert record["edit_render_recovery"]["kind"] == "server_restart"
        assert record["edit_render_recovery"]["can_retry_export"] is True
        assert record["edit_render_recovery"]["scene_assets_preserved"] is False
        assert record["edit_render_recovery"]["scene_records_preserved"] is True
        assert record["edit_render_recovery"]["automatic_resume_supported"] is False
        assert record["_edited_scenes"] == [{"description": "scene", "image_path": "scene.png"}]
        assert record["scene_clips"][0]["status"] == "completed"
        assert jobs["already-done"]["edit_render_status"] == "completed"
        assert saved[0]["edit_render_status"] == "interrupted"

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
        assert "render" in str(error.value.detail).lower()

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
    async def test_failed_final_export_persists_render_lock_release(self, tmp_path, monkeypatch):
        from fastapi import HTTPException
        from modules.ai_video_studio.api.routes import video
        from modules.ai_video_studio.media import output_paths, render

        video_root = tmp_path / "videos"
        video_root.mkdir()
        monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda _name: video_root)
        monkeypatch.setattr(output_paths, "unique_filename", lambda *_args: video_root / "failed.mp4")
        snapshots = []
        monkeypatch.setattr(video, "_persist_job", lambda record: snapshots.append(record["_rendering_edits"]))

        def fail_render(*_args, **_kwargs):
            raise RuntimeError("synthetic encoder failure")

        monkeypatch.setattr(render, "render_multi_scene_video", fail_render)
        job_id = "failed-export-lock-release"
        video._jobs[job_id] = {
            "job_id": job_id, "status": "completed",
            "params": {"resolution": "320x180", "frame_rate": 24},
            "_edited_scenes": [{"description": "test scene", "duration": 2}],
        }

        with pytest.raises(HTTPException) as error:
            await video.render_video_job_edits(job_id)

        assert error.value.status_code == 500
        assert video._jobs[job_id]["edit_render_status"] == "failed"
        assert video._jobs[job_id]["_rendering_edits"] is False
        assert snapshots[-1] is False

    @pytest.mark.asyncio
    async def test_audio_mux_failure_does_not_mark_final_export_completed(self, tmp_path, monkeypatch):
        from fastapi import HTTPException
        from modules.ai_video_studio.api.routes import video
        from modules.ai_video_studio.media import output_paths, render, audio, audio_timeline

        video_root = tmp_path / "videos"
        mix_root = tmp_path / "mix"
        video_root.mkdir()
        mix_root.mkdir()
        rendered = video_root / "rendered.mp4"
        rendered.write_bytes(b"video-only")
        mixed_audio = mix_root / "mixed.wav"
        mixed_audio.write_bytes(b"audio")
        monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: mix_root if name == "mix" else video_root)
        monkeypatch.setattr(output_paths, "unique_filename", lambda directory, *_args: Path(directory) / "out.mp4")
        monkeypatch.setattr(render, "render_mixed_scene_video", lambda *_args, **_kwargs: {
            "output_path": str(rendered), "frames": 48, "bytes": rendered.stat().st_size,
            "engine": "test", "transition_policy": "frame_accurate", "transitions_applied": [],
        })
        monkeypatch.setattr(audio_timeline, "mix_audio_timeline", lambda *_args, **_kwargs: {
            "output_path": str(mixed_audio), "quality": {"export_allowed": True},
        })
        monkeypatch.setattr(audio, "mux_audio_into_video", lambda *_args, **_kwargs: {
            "muxed": False, "error": "synthetic ffmpeg mux failure",
        })
        monkeypatch.setattr(video, "_persist_job", lambda _record: None)

        job_id = "audio-mux-failed-export"
        video._jobs[job_id] = {
            "job_id": job_id, "status": "completed",
            "params": {"resolution": "320x180", "frame_rate": 24},
            "_edited_scenes": [{
                "_source_scene_index": 0, "duration": 2,
                "generative_video_path": str(rendered),
            }],
            "_audio_clips": {"music": [{"audio_path": str(mixed_audio), "start": 0, "end": 2}], "sfx": []},
        }

        with pytest.raises(HTTPException) as error:
            await video.render_video_job_edits(job_id)

        assert error.value.status_code == 500
        assert video._jobs[job_id]["edit_render_status"] == "failed"
        assert video._jobs[job_id]["edit_render_audio"] == "audio_mux_failed"
        assert video._jobs[job_id]["_rendering_edits"] is False

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
    async def test_recovery_plan_repairs_clip_when_scene_narration_was_not_muxed(self, tmp_path, monkeypatch):
        from modules.ai_video_studio.api.routes import video
        from modules.ai_video_studio.media import output_paths

        roots = {name: tmp_path / name for name in ("images", "videos", "voice")}
        for root in roots.values():
            root.mkdir()
        image = roots["images"] / "scene.png"
        image.write_bytes(b"approved-image")
        clip = roots["videos"] / "scene.mp4"
        clip.write_bytes(b"silent-visual-intermediate")
        narration = roots["voice"] / "scene.wav"
        narration.write_bytes(b"valid-narration")
        monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: roots[name])
        video._jobs["recovery-unmuxed-narration"] = {
            "job_id": "recovery-unmuxed-narration", "status": "failed",
            "vidgrid_compatible": True, "resolution": "1280x720", "frame_rate": 30,
            "params": {},
            "_edited_scenes": [{"_source_scene_index": 0, "background_image_path": str(image)}],
            "voiceover": {"narration_style": "per_scene",
                          "clips": [{"index": 0, "audio_path": str(narration)}]},
            "scene_clips": [{
                "scene_index": 0, "status": "ready", "output_path": str(clip),
                "width": 1280, "height": 720, "fps": 30,
                "source_image_fingerprint": video._asset_sha256(image),
            }],
        }

        plan = await video.get_video_job_recovery_plan("recovery-unmuxed-narration")

        assert plan["repair_scene_indices"] == [0]
        assert "scene_narration_not_muxed" in plan["scenes"][0]["reasons"]

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
        # This test checks selective rebuild selection, not MP4 decoding. The fixture bytes are placeholders.
        monkeypatch.setattr(video, "_probe_media_asset", lambda *_args, **_kwargs: {"probe_status": "not_verified"})
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



class TestAsyncVidGridRebuildQueue:
    @pytest.mark.asyncio
    async def test_queue_returns_immediately_and_persists_requested_scenes(self, monkeypatch):
        from fastapi import BackgroundTasks
        from modules.ai_video_studio.api.routes import video

        record = {"job_id": "async-queue-job", "status": "completed", "vidgrid_compatible": True}
        video._jobs["async-queue-job"] = record
        monkeypatch.setattr(video, "_scene_clip_recovery_plan", lambda _record: {"repair_scene_indices": [1, 4]})
        monkeypatch.setattr(video, "_persist_job", lambda _record: None)
        enqueued = []
        def fake_enqueue(task_id, task_type, job_id, payload):
            enqueued.append((task_id, task_type, job_id, payload))
            return True
        monkeypatch.setattr(
            "modules.ai_video_studio.media.job_store.enqueue_unique_task_for_job",
            fake_enqueue,
        )
        tasks = BackgroundTasks()

        result = await video.queue_scene_clip_rebuild(
            "async-queue-job", tasks, video.SceneClipRebuildRequest(scene_indices=[4])
        )

        assert result["status"] == "queued"
        assert result["requested"] == 1
        assert record["_scene_clip_rebuild_scheduled"] is True
        assert record["scene_clip_rebuild_queue"]["requested_scene_indices"] == [4]
        assert result["task_id"] == enqueued[0][0]
        assert enqueued[0][1] == "scene_clip_rebuild"
        assert enqueued[0][2] == "async-queue-job"
        assert enqueued[0][3]["scene_indices"] == [4]
        assert tasks.tasks == []

    @pytest.mark.asyncio
    async def test_durable_scene_worker_honors_cancel_before_render(self, monkeypatch):
        from modules.ai_video_studio.api.routes import video

        job_id = "durable-scene-cancel"
        record = {
            "job_id": job_id,
            "scene_clip_rebuild_queue": {
                "queue_id": "queue-cancel", "status": "queued",
                "cancel_requested": True, "results": [],
            },
        }
        video._jobs[job_id] = record
        monkeypatch.setattr(video, "_persist_job", lambda _record: None)

        async def fail_if_called(*_args, **_kwargs):
            raise AssertionError("cancelled durable task must not render")

        monkeypatch.setattr(video, "rebuild_stale_video_job_scene_clips", fail_if_called)
        await video._process_durable_scene_clip_rebuild({
            "job_id": job_id, "queue_id": "queue-cancel", "scene_indices": [0],
        })

        assert record["scene_clip_rebuild_queue"]["status"] == "cancelled"
        assert record["scene_clip_rebuild_status"] == "cancelled"

    @pytest.mark.asyncio
    async def test_durable_scene_worker_recalculates_repairable_scenes(self, monkeypatch):
        from modules.ai_video_studio.api.routes import video

        job_id = "durable-scene-recovery"
        record = {
            "job_id": job_id,
            "vidgrid_compatible": True,
            "scene_clip_rebuild_queue": {
                "queue_id": "queue-recovery", "status": "interrupted",
                "cancel_requested": False, "results": [],
            },
        }
        video._jobs[job_id] = record
        monkeypatch.setattr(video, "_scene_clip_recovery_plan", lambda _record: {"repair_scene_indices": [2]})
        monkeypatch.setattr(video, "_persist_job", lambda _record: None)
        calls = []

        async def fake_rebuild(_job_id, request):
            calls.append(request.scene_indices)
            record["scene_clip_rebuild_queue"].update({
                "status": "completed", "completed": 1, "failed": 0,
                "results": [{"scene_index": 2, "status": "completed"}],
            })
            return {"status": "completed", "rebuilt": 1, "failed": 0}

        monkeypatch.setattr(video, "rebuild_stale_video_job_scene_clips", fake_rebuild)
        await video._process_durable_scene_clip_rebuild({
            "job_id": job_id, "queue_id": "queue-recovery", "scene_indices": [1, 2],
        })

        assert calls == [[2]]
        assert record["_scene_clip_rebuild_worker"] is False
        assert record["_scene_clip_rebuild_scheduled"] is False

    @pytest.mark.asyncio
    async def test_resume_only_accepts_incomplete_queue_states(self, monkeypatch):
        from fastapi import BackgroundTasks, HTTPException
        from modules.ai_video_studio.api.routes import video

        record = {
            "job_id": "async-resume-job",
            "scene_clip_rebuild_queue": {"status": "interrupted"},
        }
        video._jobs["async-resume-job"] = record
        called = []
        async def fake_queue(job_id, background_tasks, request):
            called.append((job_id, request))
            return {"status": "queued", "queued": True, "requested": 2}
        monkeypatch.setattr(video, "queue_scene_clip_rebuild", fake_queue)

        result = await video.resume_scene_clip_rebuild_queue("async-resume-job", BackgroundTasks())

        assert result["queued"] is True
        assert called == [("async-resume-job", None)]

        record["scene_clip_rebuild_queue"]["status"] = "completed"
        with pytest.raises(HTTPException) as error:
            await video.resume_scene_clip_rebuild_queue("async-resume-job", BackgroundTasks())
        assert error.value.status_code == 409


    @pytest.mark.asyncio
    async def test_second_queue_is_rejected_while_first_is_scheduled(self, monkeypatch):
        from fastapi import BackgroundTasks, HTTPException
        from modules.ai_video_studio.api.routes import video

        record = {
            "job_id": "async-double-queue-job", "status": "completed",
            "vidgrid_compatible": True, "_scene_clip_rebuild_scheduled": True,
        }
        video._jobs["async-double-queue-job"] = record
        tasks = BackgroundTasks()
        with pytest.raises(HTTPException) as error:
            await video.queue_scene_clip_rebuild("async-double-queue-job", tasks)
        assert error.value.status_code == 409
        assert not tasks.tasks

    @pytest.mark.asyncio
    async def test_cancel_marks_active_queue_for_cooperative_stop(self, monkeypatch):
        from modules.ai_video_studio.api.routes import video

        record = {
            "job_id": "async-cancel-job",
            "scene_clip_rebuild_queue": {"status": "processing", "cancel_requested": False},
        }
        video._jobs["async-cancel-job"] = record
        monkeypatch.setattr(video, "_persist_job", lambda _record: None)

        result = await video.cancel_scene_clip_rebuild_queue("async-cancel-job")

        assert result["cancel_requested"] is True
        assert record["scene_clip_rebuild_queue"]["cancel_requested"] is True

    @pytest.mark.asyncio
    async def test_background_worker_honors_cancel_before_start(self, monkeypatch):
        from modules.ai_video_studio.api.routes import video

        record = {
            "job_id": "async-pre-cancel-job",
            "scene_clip_rebuild_queue": {
                "status": "queued", "cancel_requested": True, "results": [],
            },
        }
        video._jobs["async-pre-cancel-job"] = record
        async def fail_rebuild(*_args):
            raise AssertionError("cancelled queued work must not start")
        monkeypatch.setattr(video, "rebuild_stale_video_job_scene_clips", fail_rebuild)
        monkeypatch.setattr(video, "_persist_job", lambda _record: None)

        await video._run_scene_clip_rebuild_background("async-pre-cancel-job", [0])

        assert record["scene_clip_rebuild_queue"]["status"] == "cancelled"
        assert record["scene_clip_rebuild_status"] == "cancelled"
        assert record["_scene_clip_rebuild_worker"] is False

    @pytest.mark.asyncio
    async def test_background_worker_clears_scheduling_lock(self, monkeypatch):
        from modules.ai_video_studio.api.routes import video

        record = {
            "job_id": "async-worker-job",
            "scene_clip_rebuild_queue": {"status": "queued", "results": []},
        }
        video._jobs["async-worker-job"] = record
        calls = []
        async def fake_rebuild(job_id, request):
            calls.append((job_id, request.scene_indices))
            return {"status": "completed", "rebuilt": 1}
        monkeypatch.setattr(video, "rebuild_stale_video_job_scene_clips", fake_rebuild)
        monkeypatch.setattr(video, "_persist_job", lambda _record: None)

        await video._run_scene_clip_rebuild_background("async-worker-job", [2])

        assert calls == [("async-worker-job", [2])]
        assert record["_scene_clip_rebuild_worker"] is False
        assert record["_scene_clip_rebuild_scheduled"] is False


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
        # These fixture clips are placeholder bytes, not real MP4 containers.
        # This test covers selected-scene eligibility; real MP4 integrity is
        # exercised by the dedicated media-probe and render smoke tests.
        monkeypatch.setattr(video, "_probe_media_asset", lambda *_: {
            "probe_status": "not_verified",
        })
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
    async def test_selected_stale_video_clip_is_included_in_rebuild_scene_indices(self, monkeypatch):
        from modules.ai_video_studio.api.routes import video

        graph = {
            "nodes": [
                {"id": "scene:5:clip", "type": "video_clip", "scene_index": 5, "status": "stale"},
                {"id": "final:export", "type": "final_export", "status": "available"},
            ],
            "edges": [{"from": "scene:5:clip", "to": "final:export"}],
        }
        async def get_graph(_job_id):
            return graph
        monkeypatch.setattr(video, "get_video_job_dependency_graph", get_graph)

        impact = await video.preview_video_job_dependency_impact(
            "dependency-impact-selected-clip",
            video.DependencyImpactRequest(changed_asset_ids=["scene:5:clip"]),
        )

        assert impact["rebuild_scene_indices"] == [5]
        assert impact["final_export_required"] is True

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
    async def test_scene_change_is_persisted_to_durable_queue(self, monkeypatch):
        from modules.ai_video_studio.api.routes import video

        job_id = "dependency-execution-scene"
        record = {
            "job_id": job_id, "status": "completed",
            "vidgrid_compatible": True,
        }
        video._jobs[job_id] = record
        impact = {
            "job_id": job_id,
            "changed_asset_ids": ["scene:3:image"],
            "affected_nodes": [{"id": "scene:3:clip", "type": "video_clip", "status": "stale"}],
            "affected_node_ids": ["scene:3:clip", "final:export"],
            "rebuild_scene_indices": [3], "final_export_required": True,
        }
        monkeypatch.setattr(video, "preview_video_job_dependency_impact", lambda *_args: _async_result(impact))
        monkeypatch.setattr(video, "get_video_job_dependency_graph", lambda *_args: _async_result({"nodes": []}))
        monkeypatch.setattr(video, "_persist_job", lambda _record: None)
        enqueued = []
        monkeypatch.setattr(
            "modules.ai_video_studio.media.job_store.enqueue_task",
            lambda task_id, task_type, payload: enqueued.append((task_id, task_type, payload)),
        )

        request = video.DependencyExecutionRequest(changed_asset_ids=["scene:3:image"], confirmed=True)
        result = await video.execute_video_job_dependency_rebuild(job_id, request)

        assert result["status"] == "queued"
        assert result["queued"] is True
        assert result["executed"] is False
        assert record["dependency_rebuild_execution"]["status"] == "queued"
        assert record["dependency_rebuild_execution"]["scene_indices"] == [3]
        assert result["task_id"] == enqueued[0][0]
        assert enqueued[0][1] == "dependency_rebuild"
        assert enqueued[0][2]["job_id"] == job_id
        assert enqueued[0][2]["changed_asset_ids"] == ["scene:3:image"]

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
        monkeypatch.setattr(video, "_persist_job", lambda _record: None)
        enqueued = []
        monkeypatch.setattr(
            "modules.ai_video_studio.media.job_store.enqueue_task",
            lambda task_id, task_type, payload: enqueued.append((task_id, task_type, payload)),
        )

        request = video.DependencyExecutionRequest(changed_asset_ids=["scene:1:image"], confirmed=True)
        result = await video.execute_video_job_dependency_rebuild("dependency-execution-partial", request)

        # Dependency rebuilds are persisted for the worker; scene rendering and
        # final export must not run synchronously in the API request.
        assert result["status"] == "queued"
        assert result["queued"] is True
        assert result["executed"] is False
        assert result["impact"]["rebuild_scene_indices"] == [1]
        assert result["task_id"] == enqueued[0][0]
        assert enqueued[0][1] == "dependency_rebuild"
        assert enqueued[0][2]["job_id"] == "dependency-execution-partial"
        assert record["dependency_rebuild_execution"]["status"] == "queued"
        assert record["dependency_rebuild_execution"]["final_export_required"] is True


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
        monkeypatch.setattr(video, "_persist_job", lambda _record: None)
        enqueued = []
        monkeypatch.setattr(
            "modules.ai_video_studio.media.job_store.enqueue_task",
            lambda task_id, task_type, payload: enqueued.append((task_id, task_type, payload)),
        )

        request = video.DependencyExecutionRequest(changed_asset_ids=["audio:music:0"], confirmed=True)
        result = await video.execute_video_job_dependency_rebuild("dependency-execution-audio", request)

        # Audio-only edits queue only the final export; they do not rebuild scene clips.
        assert result["status"] == "queued"
        assert result["queued"] is True
        assert result["executed"] is False
        assert result["impact"]["rebuild_scene_indices"] == []
        assert result["task_id"] == enqueued[0][0]
        assert enqueued[0][1] == "dependency_rebuild"
        assert enqueued[0][2]["changed_asset_ids"] == ["audio:music:0"]
        assert record["dependency_rebuild_execution"]["status"] == "queued"
        assert record["dependency_rebuild_execution"]["scene_indices"] == []


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
        # These are placeholder bytes; this test isolates fingerprint-based staleness.
        monkeypatch.setattr(video, "_probe_media_asset", lambda *_: {"probe_status": "not_verified"})
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



@pytest.mark.asyncio
async def test_dependency_rebuild_returns_accepted_and_persists_queue_state(monkeypatch):
    from fastapi import BackgroundTasks
    from modules.ai_video_studio.api.routes import video

    job_id = "dependency-async-queue"
    record = {"job_id": job_id, "status": "completed", "vidgrid_compatible": True}
    video._jobs[job_id] = record
    impact = {
        "job_id": job_id,
        "changed_asset_ids": ["scene:2:image"],
        "affected_nodes": [{"id": "scene:2:clip", "type": "video_clip", "status": "stale"}],
        "affected_node_ids": ["scene:2:clip", "final:export"],
        "rebuild_scene_indices": [2],
        "final_export_required": True,
    }
    monkeypatch.setattr(video, "preview_video_job_dependency_impact", lambda *_args: _async_result(impact))
    monkeypatch.setattr(video, "get_video_job_dependency_graph", lambda *_args: _async_result({"nodes": []}))
    monkeypatch.setattr(video, "_persist_job", lambda _record: None)
    enqueued = []
    monkeypatch.setattr("modules.ai_video_studio.media.job_store.enqueue_task", lambda task_id, task_type, payload: enqueued.append((task_id, task_type, payload)))

    tasks = BackgroundTasks()
    request = video.DependencyExecutionRequest(changed_asset_ids=["scene:2:image"], confirmed=True)
    result = await video.execute_video_job_dependency_rebuild(job_id, request, tasks)

    assert result["status"] == "queued"
    assert result["queued"] is True
    assert record["dependency_rebuild_execution"]["status"] == "queued"
    assert result["task_id"] == enqueued[0][0]
    assert enqueued[0][1] == "dependency_rebuild"
    assert enqueued[0][2]["job_id"] == job_id
    assert tasks.tasks == []


@pytest.mark.asyncio
async def test_dependency_rebuild_status_endpoint_returns_persisted_state():
    from modules.ai_video_studio.api.routes import video

    job_id = "dependency-async-status"
    video._jobs[job_id] = {
        "job_id": job_id,
        "dependency_rebuild_execution": {"status": "processing", "scene_indices": [1, 4]},
    }
    result = await video.get_video_job_dependency_rebuild_status(job_id)

    assert result["status"] == "processing"
    assert result["scene_indices"] == [1, 4]


@pytest.mark.asyncio
async def test_cancel_dependency_rebuild_sets_cooperative_cancel_flag():
    from modules.ai_video_studio.api.routes import video

    job_id = "dependency-cancel-request"
    record = {
        "job_id": job_id,
        "dependency_rebuild_execution": {"status": "processing", "cancel_requested": False},
    }
    video._jobs[job_id] = record
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(video, "_persist_job", lambda _record: None)
    try:
        result = await video.cancel_video_job_dependency_rebuild(job_id)
    finally:
        monkeypatch.undo()

    assert result["cancel_requested"] is True
    assert record["dependency_rebuild_execution"]["cancel_requested"] is True


@pytest.mark.asyncio
async def test_dependency_rebuild_worker_honors_cancel_before_start(monkeypatch):
    from modules.ai_video_studio.api.routes import video

    job_id = "dependency-cancel-before-start"
    record = {
        "job_id": job_id,
        "dependency_rebuild_execution": {"status": "queued", "cancel_requested": True},
    }
    video._jobs[job_id] = record
    monkeypatch.setattr(video, "_persist_job", lambda _record: None)

    async def fail_if_called(*_args, **_kwargs):
        raise AssertionError("cancelled queue must not rebuild or render")

    monkeypatch.setattr(video, "rebuild_stale_video_job_scene_clips", fail_if_called)
    monkeypatch.setattr(video, "render_video_job_edits", fail_if_called)
    await video._run_dependency_rebuild_background(job_id, ["scene:0:image"], {"rebuild_scene_indices": [0]})

    assert record["dependency_rebuild_execution"]["status"] == "cancelled"


@pytest.mark.asyncio
async def test_resume_dependency_rebuild_queues_only_scenes_still_repairable(monkeypatch):
    from fastapi import BackgroundTasks
    from modules.ai_video_studio.api.routes import video

    job_id = "dependency-resume-selective"
    record = {
        "job_id": job_id, "status": "completed", "vidgrid_compatible": True,
        "dependency_rebuild_execution": {
            "status": "interrupted", "changed_asset_ids": ["scene:1:image"],
            "scene_indices": [1, 2], "queued_at": 100, "attempt": 1,
        },
    }
    video._jobs[job_id] = record
    impact = {
        "job_id": job_id, "changed_asset_ids": ["scene:1:image"],
        "affected_nodes": [{"id": "scene:1:clip", "type": "video_clip", "status": "stale"}],
        "rebuild_scene_indices": [1, 2], "final_export_required": True,
        "rebuild_steps": [{"operation": "rebuild_scene_clips", "scene_indices": [1, 2]}],
    }
    monkeypatch.setattr(video, "preview_video_job_dependency_impact", lambda *_args: _async_result(dict(impact)))
    monkeypatch.setattr(video, "_scene_clip_recovery_plan", lambda _record: {"repair_scene_indices": [2]})
    monkeypatch.setattr(video, "get_video_job_dependency_graph", lambda *_args: _async_result({"nodes": []}))
    monkeypatch.setattr(video, "_persist_job", lambda _record: None)
    enqueued = []
    monkeypatch.setattr("modules.ai_video_studio.media.job_store.enqueue_task", lambda task_id, task_type, payload: enqueued.append((task_id, task_type, payload)))

    tasks = BackgroundTasks()
    result = await video.resume_video_job_dependency_rebuild(job_id, tasks)

    assert result["status"] == "queued"
    assert result["scene_indices"] == [2]
    assert result["previously_completed_scene_indices"] == [1]
    assert record["dependency_rebuild_execution"]["attempt"] == 2
    assert result["task_id"] == enqueued[0][0]
    assert enqueued[0][2]["job_id"] == job_id
    assert tasks.tasks == []


def test_restart_keeps_scene_clip_queue_when_durable_task_exists():
    from modules.ai_video_studio.api.routes.video import _reconcile_scene_clip_queue_after_restart

    record = {
        "scene_clip_rebuild_queue": {
            "status": "processing", "current_scene_index": 4,
        },
        "_scene_clip_rebuild_worker": True,
    }
    _reconcile_scene_clip_queue_after_restart(record, durable_task_active=True)

    assert record["scene_clip_rebuild_queue"]["status"] == "queued"
    assert record["scene_clip_rebuild_queue"]["current_scene_index"] is None
    assert record["_scene_clip_rebuild_scheduled"] is True
    assert record["_scene_clip_rebuild_worker"] is False
    assert "worker retomará" in record["scene_clip_rebuild_queue"]["recovery_note"]


def test_restart_marks_scene_clip_queue_interrupted_without_durable_task():
    from modules.ai_video_studio.api.routes.video import _reconcile_scene_clip_queue_after_restart

    record = {
        "scene_clip_rebuild_queue": {
            "status": "processing", "current_scene_index": 2,
        },
        "_scene_clip_rebuild_scheduled": True,
    }
    _reconcile_scene_clip_queue_after_restart(record, durable_task_active=False)

    assert record["scene_clip_rebuild_queue"]["status"] == "interrupted"
    assert record["_scene_clip_rebuild_scheduled"] is False
    assert record["_scene_clip_rebuild_worker"] is False
    assert "recovery-plan" in record["scene_clip_rebuild_queue"]["recovery_note"]


def test_scene_checkpoint_persists_fingerprint_of_muxed_narration(tmp_path, monkeypatch):
    from modules.ai_video_studio.api.routes import video
    from modules.ai_video_studio.media import output_paths

    voice_root = tmp_path / "voice"
    video_root = tmp_path / "videos"
    voice_root.mkdir()
    video_root.mkdir()
    narration = voice_root / "scene.wav"
    narration.write_bytes(b"the exact narration used for mux")
    clip = video_root / "scene.mp4"
    clip.write_bytes(b"muxed scene video")
    monkeypatch.setattr(
        output_paths, "get_subsystem_dir",
        lambda name: voice_root if name == "voice" else video_root,
    )

    record = {"scene_clips": []}
    video._merge_scene_checkpoint(record, {
        "scene_index": 0, "clip_path": str(clip),
        "clip_narration_path": str(narration),
        "clip_audio_status": "per_scene_narration_muxed",
        "clip_duration": 10.0, "clip_bytes": clip.stat().st_size,
    })

    saved = record["scene_clips"][0]
    assert saved["audio_status"] == "per_scene_narration_muxed"
    assert saved["source_narration_fingerprint"] == video._asset_sha256(narration)


def test_resolve_scene_narration_asset_requires_nonempty_file_inside_voice_root(tmp_path, monkeypatch):
    from modules.ai_video_studio.api.routes import video
    from modules.ai_video_studio.media import output_paths

    voice_root = tmp_path / "voice"
    outside_root = tmp_path / "outside"
    voice_root.mkdir()
    outside_root.mkdir()
    monkeypatch.setattr(
        output_paths, "get_subsystem_dir",
        lambda name: voice_root if name == "voice" else tmp_path / name,
    )

    valid = voice_root / "scene.wav"
    valid.write_bytes(b"valid narration")
    assert video._resolve_scene_narration_asset(valid) == valid.resolve()

    empty = voice_root / "empty.wav"
    empty.touch()
    with pytest.raises(ValueError, match="empty"):
        video._resolve_scene_narration_asset(empty)

    outside = outside_root / "untrusted.wav"
    outside.write_bytes(b"not an approved asset")
    with pytest.raises(ValueError, match="outside"):
        video._resolve_scene_narration_asset(outside)


def test_scene_checkpoint_rejects_narration_fingerprint_outside_voice_root(tmp_path, monkeypatch):
    from modules.ai_video_studio.api.routes import video
    from modules.ai_video_studio.media import output_paths

    voice_root = tmp_path / "voice"
    outside_root = tmp_path / "outside"
    video_root = tmp_path / "videos"
    voice_root.mkdir()
    outside_root.mkdir()
    video_root.mkdir()
    narration = outside_root / "scene.wav"
    narration.write_bytes(b"untrusted path")
    clip = video_root / "scene.mp4"
    clip.write_bytes(b"muxed scene video")
    monkeypatch.setattr(
        output_paths, "get_subsystem_dir",
        lambda name: voice_root if name == "voice" else video_root,
    )

    record = {"scene_clips": []}
    video._merge_scene_checkpoint(record, {
        "scene_index": 0, "clip_path": str(clip),
        "clip_narration_path": str(narration),
        "clip_audio_status": "per_scene_narration_muxed",
    })

    assert "source_narration_fingerprint" not in record["scene_clips"][0]


@pytest.mark.asyncio
async def test_recovery_plan_marks_non_ten_second_vidgrid_clip_stale(tmp_path, monkeypatch):
    from modules.ai_video_studio.api.routes import video
    from modules.ai_video_studio.media import job_store, output_paths

    roots = {name: tmp_path / name for name in ("images", "videos", "voice")}
    for root in roots.values():
        root.mkdir()
    image = roots["images"] / "scene.png"
    image.write_bytes(b"approved-image")
    clip = roots["videos"] / "scene.mp4"
    clip.write_bytes(b"video")
    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: roots[name])
    record = {
        "job_id": "recovery-wrong-duration", "status": "completed",
        "vidgrid_compatible": True, "resolution": "1280x720", "frame_rate": 30,
        "params": {},
        "_edited_scenes": [{"_source_scene_index": 0, "background_image_path": str(image)}],
        "scene_clips": [{
            "scene_index": 0, "status": "ready", "output_path": str(clip),
            "duration": 8.0, "width": 1280, "height": 720, "fps": 30,
            "source_image_fingerprint": video._asset_sha256(image),
        }],
    }
    video._jobs["recovery-wrong-duration"] = record

    plan = await video.get_video_job_recovery_plan("recovery-wrong-duration")

    assert plan["repair_scene_indices"] == [0]
    assert "vidgrid_clip_duration_not_10_seconds" in plan["scenes"][0]["reasons"]


def test_vidgrid_export_rejects_clip_with_wrong_duration_metadata(tmp_path, monkeypatch):
    from fastapi import HTTPException
    from modules.ai_video_studio.api.routes import video
    from modules.ai_video_studio.media import output_paths

    video_root = tmp_path / "videos"
    video_root.mkdir()
    clip = video_root / "short.mp4"
    clip.write_bytes(b"not-a-real-mp4-but-nonempty")
    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda _name: video_root)
    record = {"scene_clips": [{
        "scene_index": 0, "status": "ready", "output_path": str(clip), "duration": 9.5,
    }]}

    with pytest.raises(HTTPException) as error:
        video._ordered_vidgrid_clip_paths(record, [{"_source_scene_index": 0}])

    assert error.value.status_code == 409
    assert "scenes [0]" in str(error.value.detail)


def test_vidgrid_export_checks_measured_mp4_duration_not_only_metadata(tmp_path, monkeypatch):
    from fastapi import HTTPException
    from modules.ai_video_studio.api.routes import video
    from modules.ai_video_studio.media import output_paths

    video_root = tmp_path / "videos"
    video_root.mkdir()
    clip = video_root / "misleading.mp4"
    clip.write_bytes(b"nonempty")
    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda _name: video_root)
    monkeypatch.setattr(video, "_probe_media_asset", lambda *_args: {
        "probe_status": "passed", "duration_seconds": 8.0,
    })
    record = {"scene_clips": [{
        "scene_index": 0, "status": "ready", "output_path": str(clip), "duration": 10.0,
    }]}

    with pytest.raises(HTTPException) as error:
        video._ordered_vidgrid_clip_paths(record, [{"_source_scene_index": 0}])

    assert error.value.status_code == 409
    assert "scenes [0]" in str(error.value.detail)


def test_recovery_plan_detects_corrupt_vidgrid_mp4_even_when_metadata_says_ten_seconds(tmp_path, monkeypatch):
    from modules.ai_video_studio.api.routes import video
    from modules.ai_video_studio.media import job_store, output_paths

    roots = {name: tmp_path / name for name in ("images", "videos", "voice")}
    for root in roots.values():
        root.mkdir()
    image = roots["images"] / "scene.png"
    image.write_bytes(b"approved-image")
    clip = roots["videos"] / "broken.mp4"
    clip.write_bytes(b"not-an-mp4")
    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: roots[name])
    monkeypatch.setattr(video, "_probe_media_asset", lambda *_args: {
        "status": "corrupt", "reason": "ffprobe_rejected_media",
    })
    record = {
        "job_id": "corrupt-vidgrid-clip", "status": "completed",
        "vidgrid_compatible": True, "resolution": "1280x720", "frame_rate": 30,
        "params": {},
        "_edited_scenes": [{"_source_scene_index": 0, "background_image_path": str(image)}],
        "scene_clips": [{
            "scene_index": 0, "status": "ready", "output_path": str(clip),
            "duration": 10.0, "width": 1280, "height": 720, "fps": 30,
            "source_image_fingerprint": video._asset_sha256(image),
        }],
    }
    video._jobs["corrupt-vidgrid-clip"] = record

    import asyncio
    plan = asyncio.run(video.get_video_job_recovery_plan("corrupt-vidgrid-clip"))

    assert plan["repair_scene_indices"] == [0]
    assert "vidgrid_clip_mp4_invalid" in plan["scenes"][0]["reasons"]


def test_vidgrid_export_blocks_scene_clip_when_required_narration_was_not_muxed(tmp_path, monkeypatch):
    from fastapi import HTTPException
    from modules.ai_video_studio.api.routes import video
    from modules.ai_video_studio.media import output_paths

    roots = {name: tmp_path / name for name in ("videos", "voice")}
    for root in roots.values():
        root.mkdir()
    clip = roots["videos"] / "scene.mp4"
    clip.write_bytes(b"nonempty")
    narration = roots["voice"] / "scene.wav"
    narration.write_bytes(b"narration")
    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: roots[name])
    monkeypatch.setattr(video, "_probe_media_asset", lambda *_args: {
        "probe_status": "passed", "duration_seconds": 10.0,
    })
    record = {
        "voiceover": {
            "narration_style": "per_scene",
            "clips": [{"index": 0, "audio_path": str(narration)}],
        },
        "scene_clips": [{
            "scene_index": 0, "status": "updated", "output_path": str(clip),
            "duration": 10.0, "audio_status": "narration_mux_failed",
        }],
    }

    with pytest.raises(HTTPException) as error:
        video._ordered_vidgrid_clip_paths(record, [{"_source_scene_index": 0}])

    assert error.value.status_code == 409
    assert "scenes [0]" in str(error.value.detail)




def test_vidgrid_export_blocks_clip_when_source_narration_changed(tmp_path, monkeypatch):
    from fastapi import HTTPException
    from modules.ai_video_studio.api.routes import video
    from modules.ai_video_studio.media import output_paths

    roots = {name: tmp_path / name for name in ("videos", "voice")}
    for root in roots.values():
        root.mkdir()
    clip = roots["videos"] / "scene.mp4"
    clip.write_bytes(b"valid-container-placeholder")
    narration = roots["voice"] / "scene.wav"
    narration.write_bytes(b"new narration bytes")
    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: roots[name])
    monkeypatch.setattr(video, "_probe_media_asset", lambda *_args: {
        "probe_status": "passed", "duration_seconds": 10.0,
    })
    record = {
        "voiceover": {
            "narration_style": "per_scene",
            "clips": [{"index": 0, "audio_path": str(narration)}],
        },
        "scene_clips": [{
            "scene_index": 0, "status": "updated", "output_path": str(clip),
            "duration": 10.0, "audio_status": "per_scene_narration_muxed",
            "source_narration_fingerprint": "old-audio-fingerprint",
        }],
    }

    with pytest.raises(HTTPException) as error:
        video._ordered_vidgrid_clip_paths(record, [{"_source_scene_index": 0}])

    assert error.value.status_code == 409
    assert "scenes [0]" in str(error.value.detail)



@pytest.mark.asyncio
async def test_requested_audio_shorter_than_video_invalidates_final_mp4(tmp_path, monkeypatch):
    from types import SimpleNamespace
    from modules.ai_video_studio.api.routes import video as video_routes
    from modules.ai_video_studio.media import output_paths

    root = tmp_path / "videos"
    root.mkdir()
    output = root / "truncated-audio.mp4"
    output.write_bytes(b"mp4")
    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda _name: root)
    monkeypatch.setattr(video_routes.shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(
        video_routes.subprocess, "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0, stderr="",
            stdout='{"format":{"duration":"12"},"streams":[{"codec_type":"video","codec_name":"h264","width":1280,"height":720,"avg_frame_rate":"24/1","duration":"12"},{"codec_type":"audio","codec_name":"aac","duration":"8"}]}',
        ),
    )
    monkeypatch.setattr(video_routes, "_persist_job", lambda _record: None)
    video_routes._jobs["truncated-audio-job"] = {
        "job_id": "truncated-audio-job", "project_id": "p1",
        "status": "completed", "edited_output_path": str(output),
        "params": {"voiceover": False}, "edit_render_audio": "mixed_audio",
        "edited_video_duration": 12,
    }

    report = await video_routes.validate_video_job_output("truncated-audio-job")

    assert report["audio_video_duration_delta_seconds"] == -4.0
    assert report["valid"] is False
    assert any("termina 4.00s antes" in item for item in report["errors"])


def test_saved_audio_timeline_survives_sqlite_job_reload(tmp_path, monkeypatch):
    from modules.ai_video_studio.media import job_store

    database = tmp_path / "darkstudio_jobs.sqlite3"
    monkeypatch.setattr(job_store, "_database_path", lambda: database)
    record = {
        "job_id": "audio-reload-job",
        "project_id": "local-project",
        "status": "completed",
        "_audio_clips": {
            "music": [{
                "asset": "music/background.wav",
                "asset_fingerprint": "music-sha256",
                "start": 0.5,
                "end": 18.0,
                "volume": 0.22,
                "loop": True,
            }],
            "sfx": [{
                "asset": "effects/impact.wav",
                "asset_fingerprint": "sfx-sha256",
                "start": 4.0,
                "end": 5.5,
                "volume": 0.8,
            }],
        },
        "_audio_settings": {
            "ducking_enabled": True,
            "ducking_db": 11.0,
            "normalization_enabled": True,
            "normalization_target_dbfs": -18.0,
        },
        "audio_settings": {
            "ducking_enabled": True,
            "ducking_db": 11.0,
            "normalization_enabled": True,
            "normalization_target_dbfs": -18.0,
        },
        "edit_timeline": {
            "fps": 30,
            "tracks": [
                {"id": "music", "type": "audio", "role": "music", "clips": [
                    {"asset": "music/background.wav", "start_frame": 15, "end_frame": 540},
                ]},
                {"id": "sfx", "type": "audio", "role": "sound_effect", "clips": [
                    {"asset": "effects/impact.wav", "start_frame": 120, "end_frame": 165},
                ]},
            ],
        },
    }

    job_store.save_job(record)
    restored = job_store.load_jobs("local-project")["audio-reload-job"]

    assert restored["_audio_clips"] == record["_audio_clips"]
    assert restored["_audio_settings"] == record["_audio_settings"]
    assert restored["audio_settings"] == record["audio_settings"]
    assert restored["edit_timeline"] == record["edit_timeline"]


@pytest.mark.asyncio
async def test_single_track_narration_is_included_when_editing_audio_mix(tmp_path, monkeypatch):
    from modules.ai_video_studio.api.routes import video as video_routes
    from modules.ai_video_studio.media import output_paths, render, audio, audio_timeline

    roots = {name: tmp_path / name for name in ("videos", "voice", "mix", "subtitles")}
    for root in roots.values():
        root.mkdir()
    source_voiceover = roots["videos"] / "original_voiced.mp4"
    source_voiceover.write_bytes(b"source-video-with-narration")
    rendered = roots["videos"] / "edited-visual.mp4"
    rendered.write_bytes(b"silent-edited-video")
    mixed = roots["mix"] / "mixed.wav"
    mixed.write_bytes(b"mixed-audio")
    captured = {}
    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: roots[name])
    monkeypatch.setattr(output_paths, "unique_filename", lambda directory, prefix, extension: Path(directory) / (
        "final.mp4" if prefix == "text_to_video_edited_final"
        else "edited_visual.mp4" if prefix == "text_to_video_edited"
        else "recovered.wav" if prefix == "edited_single_track_narration"
        else f"{prefix}.{extension}"
    ))
    monkeypatch.setattr(render, "render_mixed_scene_video", lambda *_args, **_kwargs: {
        "output_path": str(rendered), "frames": 48, "bytes": rendered.stat().st_size,
        "engine": "test", "transition_policy": "frame_accurate", "transitions_applied": [],
    })

    def fake_extract(source, destination):
        assert Path(source) == source_voiceover
        Path(destination).write_bytes(b"extracted-narration")
        return {"extracted": True, "output_path": str(destination), "bytes": 19}

    def fake_mix(clips, output_path, **kwargs):
        captured["clips"] = clips
        captured["total_duration"] = kwargs["total_duration"]
        return {"output_path": str(mixed), "quality": {"export_allowed": True}}

    def fake_mux(_video, _audio, destination):
        Path(destination).write_bytes(b"final-video-with-mixed-audio")
        return {"muxed": True, "output_path": str(destination), "bytes": 28}

    monkeypatch.setattr(audio, "extract_audio_track", fake_extract)
    monkeypatch.setattr(audio_timeline, "mix_audio_timeline", fake_mix)
    monkeypatch.setattr(audio, "mux_audio_into_video", fake_mux)
    monkeypatch.setattr(audio_timeline, "measure_encoded_audio", lambda *_args: {
        "measured": {"integrated_lufs": -18.0, "true_peak_dbTP": -1.0},
    })
    monkeypatch.setattr(video_routes, "_persist_job", lambda _record: None)
    job_id = "single-track-narration-edit"
    video_routes._jobs[job_id] = {
        "job_id": job_id, "status": "completed",
        "params": {"resolution": "320x180", "frame_rate": 24},
        "_edited_scenes": [{"_source_scene_index": 0, "duration": 2, "generative_video_path": str(rendered)}],
        "voiceover": {"muxed": True, "narration_style": "single_track", "output_path": str(source_voiceover)},
        "_audio_clips": {"music": [{"asset": "music/background.wav", "start": 0, "end": 2, "volume": 0.2}], "sfx": []},
        "_audio_settings": {"ducking_enabled": True, "ducking_db": 9},
    }

    await video_routes.render_video_job_edits(job_id)

    narration_inputs = [clip for clip in captured["clips"] if clip.get("kind") == "narration"]
    music_inputs = [clip for clip in captured["clips"] if clip.get("kind") == "music"]
    assert len(narration_inputs) == 1
    assert narration_inputs[0]["audio_path"].endswith("recovered.wav")
    assert narration_inputs[0]["start"] == 0
    assert narration_inputs[0]["end"] == pytest.approx(2.0)
    assert len(music_inputs) == 1
    assert video_routes._jobs[job_id]["edit_render_audio"] == "mixed_audio"


def test_video_status_response_exposes_interruption_recovery_report():
    from modules.ai_video_studio.api.routes.video import VideoStatusResponse

    report = {
        "kind": "server_restart",
        "preserved_image_count": 2,
        "preserved_clip_count": 1,
        "preserved_narration_count": 1,
        "recoverable_scene_indices": [0, 1],
        "automatic_resume_supported": False,
    }
    response = VideoStatusResponse(
        job_id="job-recovery",
        status="failed",
        progress=0.5,
        failure_info=report,
    )
    assert response.model_dump()["failure_info"] == report


@pytest.mark.asyncio
async def test_failed_generation_recovery_reports_and_preserves_new_scene_checkpoints(tmp_path, monkeypatch):
    from fastapi import BackgroundTasks
    from modules.ai_video_studio.api.routes import video
    from modules.ai_video_studio.ai_video_generator.text_to_video import text_to_video_engine
    from modules.ai_video_studio.media import job_store, output_paths

    roots = {name: tmp_path / name for name in ("images", "videos", "voice")}
    for root in roots.values():
        root.mkdir()
    image = roots["images"] / "scene.png"
    image.write_bytes(b"recovered-image")
    clip = roots["videos"] / "scene.mp4"
    clip.write_bytes(b"recovered-ten-second-clip")
    narration = roots["voice"] / "scene.wav"
    narration.write_bytes(b"recovered-narration")
    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: roots[name])
    monkeypatch.setattr(job_store, "get_subsystem_dir", lambda name: roots[name])

    job_id = "failed-recovery-checkpoints"
    record = {
        "job_id": job_id,
        "project_id": "local-project",
        "status": "failed",
        "params": {
            "num_scenes": 1,
            "resolution": "320x180",
            "frame_rate": 24,
            "duration_seconds": 10,
            "prompt": "A test scene",
            "voiceover": True,
            "vidgrid_compatible": True,
        },
        "_source_scenes": [{"_source_scene_index": 0, "prompt": "A test scene"}],
        "scene_assets": [],
        "scene_clips": [],
        "voiceover": {"narration_style": "per_scene", "clips": []},
    }
    video._jobs[job_id] = record
    persisted = []
    monkeypatch.setattr(video, "_persist_job", lambda saved: persisted.append(dict(saved)))

    class FailingEngine:
        async def generate_async(self, _request, scene_callback=None):
            scene_callback({
                "scene_index": 0,
                "stage": "clip_ready",
                "status": "completed",
                "image_path": str(image),
                "narration_path": str(narration),
                "narration_text": "Recovered narration",
                "narration_engine": "test",
                "narration_duration": 2.0,
                "clip_path": str(clip),
                "clip_bytes": clip.stat().st_size,
                "clip_duration": 10.0,
                "clip_fps": 24,
                "clip_width": 320,
                "clip_height": 180,
                "clip_audio_status": "per_scene_narration_muxed",
                "clip_narration_path": str(narration),
            })
            raise RuntimeError("simulated failure after scene checkpoint")

    monkeypatch.setattr(text_to_video_engine, "TextToVideoEngine", FailingEngine)
    tasks = BackgroundTasks()

    queued = await video.resume_interrupted_generation(job_id, tasks)
    assert queued["queued"] is True
    assert len(tasks.tasks) == 1

    task = tasks.tasks[0]
    await task.func(*task.args, **task.kwargs)

    assert record["status"] == "failed"
    assert record["scene_assets"][0]["image_path"] == str(image)
    assert record["scene_clips"][0]["output_path"] == str(clip.resolve())
    assert record["scene_clips"][0]["duration"] == 10.0
    assert record["voiceover"]["clips"][0]["audio_path"] == str(narration.resolve())
    report = record["failure_info"]
    assert report["kind"] == "generation_recovery_error"
    assert report["preserved_image_count"] == 1
    assert report["preserved_clip_count"] == 1
    assert report["preserved_narration_count"] == 1
    assert report["recoverable_scene_indices"] == [0]
    assert report["scene_assets_preserved"] is True
    assert persisted[-1]["failure_info"] == report


@pytest.mark.asyncio
async def test_scene_narration_audio_preview_is_confined_to_voice_assets(tmp_path, monkeypatch):
    from fastapi import HTTPException
    from modules.ai_video_studio.api.routes import video
    from modules.ai_video_studio.media import output_paths

    voice_root = tmp_path / "voice"
    voice_root.mkdir()
    audio = voice_root / "scene-1.wav"
    audio.write_bytes(b"RIFF-test-audio")
    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: voice_root if name == "voice" else tmp_path / name)

    job_id = "scene-audio-preview-test"
    video._jobs[job_id] = {
        "job_id": job_id,
        "voiceover": {
            "narration_style": "per_scene",
            "clips": [{"index": 0, "audio_path": str(audio)}],
        },
    }
    try:
        response = await video.get_video_job_scene_narration_audio(job_id, 0)
        assert Path(response.path) == audio
        assert response.media_type == "audio/wav"

        with pytest.raises(HTTPException) as missing:
            await video.get_video_job_scene_narration_audio(job_id, 1)
        assert missing.value.status_code == 404

        outside = tmp_path / "outside.wav"
        outside.write_bytes(b"not-approved")
        video._jobs[job_id]["voiceover"]["clips"][0]["audio_path"] = str(outside)
        with pytest.raises(HTTPException) as unsafe:
            await video.get_video_job_scene_narration_audio(job_id, 0)
        assert unsafe.value.status_code == 404

        video._jobs[job_id]["voiceover"]["narration_style"] = "single_track"
        with pytest.raises(HTTPException) as single:
            await video.get_video_job_scene_narration_audio(job_id, 0)
        assert single.value.status_code == 409
    finally:
        video._jobs.pop(job_id, None)
