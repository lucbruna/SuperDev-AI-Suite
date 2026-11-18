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


def test_update_timeline_draft_keeps_non_video_tracks(completed_job) -> None:
    request = video.TimelineEditRequest(
        scene_order=[1, 0],
        scene_edits=[
            video.SceneEdit(scene_index=0, duration_frames=72, transition_type="cut"),
            video.SceneEdit(scene_index=1, duration_frames=48, transition_type="cut"),
        ],
    )
    result = asyncio.run(video.update_video_job_timeline(completed_job, request))
    record = video._jobs[completed_job]
    assert result["edit_draft_status"] == "in_memory_only"
    assert [scene["index"] for scene in record["_edited_scenes"]] == [1, 0]
    assert [track["type"] for track in result["edit_timeline"]["tracks"]] == ["video", "audio"]


def test_update_timeline_draft_rejects_unknown_job() -> None:
    with pytest.raises(HTTPException) as error:
        asyncio.run(video.update_video_job_timeline("missing-job", video.TimelineEditRequest()))
    assert error.value.status_code == 404


def test_render_edits_returns_new_mp4_and_discloses_audio_limitation(completed_job, monkeypatch, tmp_path) -> None:
    from modules.ai_video_studio.media import output_paths, render

    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda *_: tmp_path)
    monkeypatch.setattr(output_paths, "unique_filename", lambda *_: tmp_path / "edited.mp4")
    monkeypatch.setattr(video, "to_download_url", lambda path: "/downloads/edited.mp4")

    def fake_render(scenes, output_path, **kwargs):
        assert [scene["index"] for scene in scenes] == [0, 1]
        assert kwargs["require_mp4"] is True
        return {"output_path": str(output_path), "frames": 96, "bytes": 1234, "engine": "ffmpeg"}

    monkeypatch.setattr(render, "render_multi_scene_video", fake_render)
    result = asyncio.run(video.render_video_job_edits(completed_job))
    assert result["status"] == "completed"
    assert result["output_url"] == "/downloads/edited.mp4"
    assert result["audio_status"] == "not_retimed"
    assert video._jobs[completed_job]["edit_render_status"] == "completed"


def test_render_edits_rejects_job_without_saved_scene_draft() -> None:
    job_id = "no-draft-job"
    video._jobs[job_id] = {"job_id": job_id, "status": "processing"}
    try:
        with pytest.raises(HTTPException) as error:
            asyncio.run(video.render_video_job_edits(job_id))
        assert error.value.status_code == 409
    finally:
        video._jobs.pop(job_id, None)
