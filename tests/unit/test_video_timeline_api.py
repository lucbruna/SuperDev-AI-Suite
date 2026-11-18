"""API tests for DARKSTUDIO timeline draft and edited MP4 rendering."""
from __future__ import annotations

import asyncio

import pytest
from fastapi import HTTPException

from modules.ai_video_studio.api.routes import video


@pytest.fixture
def completed_job():
    job_id = "timeline-test-job"
    video._jobs[job_id] = {
        "job_id": job_id,
        "project_id": "test-project",
        "status": "completed",
        "output_url": "/downloads/original.mp4",
        "resolution": "1280x720",
        "frame_rate": 24,
        "params": {
            "resolution": "1280x720",
            "frame_rate": 24,
            "studio_id": "whymentary",
        },
        "_source_scenes": [
            {"index": 0, "duration": 2.0, "shot_type": "wide"},
            {"index": 1, "duration": 2.0, "shot_type": "close_up"},
        ],
        "_edited_scenes": [
            {"index": 0, "duration": 2.0, "shot_type": "wide"},
            {"index": 1, "duration": 2.0, "shot_type": "close_up"},
        ],
        "edit_timeline": {
            "tracks": [
                {"id": "video-main", "type": "video", "clips": []},
                {"id": "audio-narration", "type": "audio", "role": "narration", "clips": []},
            ]
        },
    }
    yield job_id
    video._jobs.pop(job_id, None)


def test_update_timeline_draft_keeps_non_video_tracks(completed_job, monkeypatch) -> None:
    monkeypatch.setattr(video, "_persist_job", lambda record: None)
    request = video.TimelineEditRequest(
        scene_order=[1, 0],
        scene_edits=[
            video.SceneEdit(scene_index=0, duration_frames=72, transition_type="cut"),
            video.SceneEdit(scene_index=1, duration_frames=48, transition_type="cut"),
        ],
    )
    result = asyncio.run(video.update_video_job_timeline(completed_job, request))
    record = video._jobs[completed_job]
    assert result["edit_draft_status"] == "persisted_local_sqlite"
    assert [scene["index"] for scene in record["_edited_scenes"]] == [1, 0]
    assert [track["type"] for track in result["edit_timeline"]["tracks"]] == ["video", "audio"]


def test_update_audio_timeline_persists_music_and_sfx_controls(completed_job, monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(video, "_persist_job", lambda record: None)
    from modules.ai_video_studio.media import audio_timeline

    monkeypatch.setattr(audio_timeline, "validate_audio_asset", lambda value: tmp_path / "validated.wav")
    request = video.AudioTimelineEditRequest(
        music_clips=[video.AudioTimelineClip(
            asset=str(tmp_path / "music.wav"), start=0.5, end=3.0,
            volume=0.25, fade_in=0.5, fade_out=0.75,
        )],
        sfx_clips=[video.AudioTimelineClip(
            asset=str(tmp_path / "impact.wav"), start=1.0, end=1.5, volume=0.8,
        )],
    )
    result = asyncio.run(video.update_video_job_audio(completed_job, request))
    record = video._jobs[completed_job]
    assert result["audio_draft_status"] == "saved"
    assert record["_audio_clips"]["music"][0]["volume"] == 0.25
    assert record["_audio_clips"]["sfx"][0]["start"] == 1.0
    music_track = next(track for track in result["edit_timeline"]["tracks"] if track.get("role") == "music")
    assert music_track["clips"][0]["fade_in"] == 0.5


def test_update_timeline_draft_rejects_unknown_job() -> None:
    with pytest.raises(HTTPException) as error:
        asyncio.run(video.update_video_job_timeline("missing-job", video.TimelineEditRequest()))
    assert error.value.status_code == 404


def test_render_edits_returns_new_mp4_and_regenerates_subtitle_sidecar(completed_job, monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(video, "_persist_job", lambda record: None)
    from modules.ai_video_studio.media import output_paths, render

    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda *_: tmp_path)
    monkeypatch.setattr(output_paths, "unique_filename", lambda *_: tmp_path / "edited.mp4")
    monkeypatch.setattr(video, "to_download_url", lambda path: "/downloads/edited.mp4")

    def fake_render(scenes, output_path, **kwargs):
        assert [scene["index"] for scene in scenes] == [0, 1]
        assert kwargs["require_mp4"] is True
        from pathlib import Path
        Path(output_path).write_bytes(b"fake-edited-mp4")
        return {"output_path": str(output_path), "frames": 96, "bytes": 1234, "engine": "ffmpeg"}

    monkeypatch.setattr(render, "render_multi_scene_video", fake_render)
    result = asyncio.run(video.render_video_job_edits(completed_job))
    assert result["status"] == "completed"
    assert result["output_url"] == "/downloads/edited.mp4"
    assert result["audio_status"] == "silent"
    assert result["subtitle_status"] == "regenerated"
    assert result["subtitles"]["format"] == "srt"
    assert video._jobs[completed_job]["edit_render_subtitles"] == "regenerated"
    assert video._jobs[completed_job]["edit_render_status"] == "completed"
    assert video._jobs[completed_job]["output_url"] == "/downloads/original.mp4"
    assert video._jobs[completed_job]["edited_output_url"] == "/downloads/edited.mp4"


def test_render_edits_rejects_job_without_saved_scene_draft() -> None:
    job_id = "no-draft-job"
    video._jobs[job_id] = {"job_id": job_id, "status": "processing"}
    try:
        with pytest.raises(HTTPException) as error:
            asyncio.run(video.render_video_job_edits(job_id))
        assert error.value.status_code == 409
    finally:
        video._jobs.pop(job_id, None)


def test_job_status_exposes_persisted_edit_render_metadata(completed_job) -> None:
    video._jobs[completed_job].update(
        edit_draft_status="saved",
        edit_render_status="completed",
        edited_output_url="/downloads/edited.mp4",
        edited_video_duration=4.0,
        edit_render_audio="silent",
        edit_render_subtitles="regenerated",
        edited_subtitles={"format": "srt", "download_url": "/downloads/edited.srt"},
    )
    result = asyncio.run(video.get_video_job_status(completed_job))
    assert result.edited_output_url == "/downloads/edited.mp4"
    assert result.edit_render_status == "completed"
    assert result.edit_render_audio == "silent"
    assert result.edit_render_subtitles == "regenerated"
    assert result.edited_subtitles["download_url"] == "/downloads/edited.srt"
