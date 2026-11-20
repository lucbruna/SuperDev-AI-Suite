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


def test_video_job_assets_sync_only_real_files_and_refresh_metadata(tmp_path, monkeypatch):
    from modules.ai_video_studio.api.routes import assets

    store = {}
    monkeypatch.setattr(assets, "_assets", store)
    image = tmp_path / "scene.png"
    image.write_bytes(b"image-bytes")
    master = tmp_path / "final.mp4"
    master.write_bytes(b"video-bytes")
    record = {
        "job_id": "job-assets",
        "project_id": "project-assets",
        "scene_assets": [{"scene_index": 0, "image_path": str(image)}],
        "scene_clips": [{"scene_index": 0, "output_path": str(tmp_path / "missing.mp4")}],
        "output_path": str(master),
    }

    assets.sync_video_job_assets(record)
    image_record = store["job:job-assets:image-0"]
    assert image_record["asset_type"] == "image"
    assert image_record["file_size_bytes"] == len(b"image-bytes")
    assert image_record["project_id"] == "project-assets"
    assert "job:job-assets:clip-0" not in store
    assert store["job:job-assets:master-video"]["asset_type"] == "video"

    image.write_bytes(b"updated-image")
    assets.sync_video_job_assets(record)
    assert store["job:job-assets:image-0"]["file_size_bytes"] == len(b"updated-image")


def test_video_job_asset_sync_does_not_create_records_without_project_or_job(monkeypatch):
    from modules.ai_video_studio.api.routes import assets

    store = {}
    monkeypatch.setattr(assets, "_assets", store)
    assets.sync_video_job_assets({"project_id": "p", "output_path": "/tmp/video.mp4"})
    assets.sync_video_job_assets({"job_id": "j", "output_path": "/tmp/video.mp4"})
    assert store == {}


def test_video_job_assets_sync_indexes_each_per_scene_narration(tmp_path, monkeypatch):
    from modules.ai_video_studio.api.routes import assets

    store = {}
    monkeypatch.setattr(assets, "_assets", store)
    narration_one = tmp_path / "scene-1.mp3"
    narration_two = tmp_path / "scene-2.mp3"
    narration_one.write_bytes(b"voice-one")
    narration_two.write_bytes(b"voice-two")
    assets.sync_video_job_assets({
        "job_id": "job-voice",
        "project_id": "project-voice",
        "voiceover": {
            "narration_style": "per_scene",
            "clips": [
                {"index": 0, "audio_path": str(narration_one)},
                {"index": 1, "audio_path": str(narration_two)},
            ],
        },
    })

    first = store["job:job-voice:narration-0"]
    second = store["job:job-voice:narration-1"]
    assert first["asset_type"] == "audio"
    assert first["file_size_bytes"] == len(b"voice-one")
    assert second["asset_type"] == "audio"
    assert second["_source_scene_index"] == 1
    assert "job:job-voice:voiceover" not in store
