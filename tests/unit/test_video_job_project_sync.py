"""Tests for syncing durable video jobs into the local project catalog."""
from __future__ import annotations

import pytest

from modules.ai_video_studio.api.routes import project


def test_video_job_summary_creates_project_metadata():
    summary = project._video_job_project_summary({
        "project_id": "workspace-1",
        "status": "completed",
        "resolution": "1920x1080",
        "frame_rate": 30,
        "video_duration": 42.0,
        "output_url": "/downloads/final.mp4",
        "_source_scenes": [{}, {}, {}],
        "params": {"prompt": "A cinematic story", "style": "cinematic", "voice_language": "pt-BR"},
    })

    assert summary["id"] == "workspace-1"
    assert summary["aspect_ratio"] == "16:9"
    assert summary["duration_seconds"] == 42.0
    assert summary["scene_count"] == 3
    assert summary["output_url"] == "/downloads/final.mp4"
    assert summary["ai_prompt"] == "A cinematic story"
    assert summary["status"] == "completed"


def test_video_job_summary_preserves_user_project_name():
    summary = project._video_job_project_summary(
        {
            "project_id": "workspace-1",
            "status": "processing",
            "params": {"prompt": "New prompt", "num_scenes": 5},
        },
        {"id": "workspace-1", "name": "My Project", "description": "My description"},
    )

    assert summary["name"] == "My Project"
    assert summary["description"] == "My description"
    assert summary["scene_count"] == 5
    assert summary["status"] == "active"


def test_video_job_summary_requires_project_id():
    with pytest.raises(ValueError, match="project_id"):
        project._video_job_project_summary({"params": {}})


def test_generated_scenes_sync_to_project_and_preserve_manual_edits(monkeypatch):
    from modules.ai_video_studio.api.routes import scene

    store = {}
    monkeypatch.setattr(scene, "_scenes", store)
    record = {
        "job_id": "job-123",
        "project_id": "project-456",
        "vidgrid_compatible": True,
        "_edited_scenes": [
            {"_source_scene_index": 0, "title": "Opening", "visual_prompt": "A wide cinematic shot", "voiceover_text": "Welcome"},
            {"_source_scene_index": 1, "title": "The reveal", "visual_prompt": "A dramatic reveal"},
        ],
        "scene_assets": [{"scene_index": 0, "image_url": "/media/scene-0.png"}],
        "scene_clips": [{"scene_index": 0, "output_url": "/media/scene-0.mp4"}],
        "scene_progress": [{"scene_index": 1, "status": "processing"}],
    }

    scene.sync_video_job_scenes(record)
    first = store["job:job-123:0"]
    second = store["job:job-123:1"]
    assert first["project_id"] == "project-456"
    assert first["duration"] == 10
    assert first["generated_image_url"] == "/media/scene-0.png"
    assert first["generated_video_url"] == "/media/scene-0.mp4"
    assert second["start_time"] == 10
    assert second["generation_status"] == "processing"

    first["name"] = "My manual title"
    first["_user_modified_fields"] = ["name"]
    record["_edited_scenes"][0]["title"] = "Updated generated title"
    scene.sync_video_job_scenes(record)
    assert store["job:job-123:0"]["name"] == "My manual title"


def test_generated_scene_sync_ignores_invalid_asset_indexes(monkeypatch):
    from modules.ai_video_studio.api.routes import scene

    store = {}
    monkeypatch.setattr(scene, "_scenes", store)
    scene.sync_video_job_scenes({
        "job_id": "job-1",
        "project_id": "project-1",
        "_source_scenes": [{"title": "Scene"}],
        "scene_assets": [{"scene_index": None}],
        "scene_clips": [{"scene_index": "invalid"}],
    })
    assert store["job:job-1:0"]["name"] == "Scene"
