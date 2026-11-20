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
