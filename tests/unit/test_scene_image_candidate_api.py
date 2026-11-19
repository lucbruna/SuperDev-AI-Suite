from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from fastapi import HTTPException

from modules.ai_video_studio.api.routes import video
from modules.ai_video_studio.media import output_paths


def _job(candidate_path: Path) -> dict:
    return {
        "job_id": "job-candidate-api",
        "status": "completed",
        "params": {"studio_id": "historical_documentary"},
        "_source_scenes": [
            {"_source_scene_index": 3, "background_image_path": "/images/old.png", "visual_prompt": "old"},
        ],
        "scene_image_candidates": {
            "3": [{
                "candidate_id": "candidate-3a",
                "scene_index": 3,
                "image_path": str(candidate_path),
                "provider": "test-provider",
                "operation": "image_to_image",
                "prompt": "new visual",
                "negative_prompt": "blur",
                "seed": 17,
                "status": "pending_approval",
            }],
        },
        "scene_assets": [{"scene_index": 3, "image_path": "/images/old.png"}],
        "scene_clips": [{"scene_index": 3, "status": "updated"}],
    }


def test_approve_candidate_uses_workflow_and_preserves_asset_history(monkeypatch, tmp_path: Path) -> None:
    image_root = tmp_path / "images"
    image_root.mkdir()
    candidate_path = image_root / "candidate.png"
    candidate_path.write_bytes(b"image-data")
    record = _job(candidate_path)

    monkeypatch.setattr(video, "_jobs", {record["job_id"]: record})
    monkeypatch.setattr(video, "_scene_batch_jobs", set())
    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda _name: image_root)
    monkeypatch.setattr(video, "to_download_url", lambda path: f"/downloads/{Path(path).name}")
    monkeypatch.setattr(video, "_persist_job", lambda _record: None)

    response = asyncio.run(
        video.approve_video_job_scene_image(record["job_id"], 3, "candidate-3a")
    )

    assert response["status"] == "approved"
    assert response["image_url"] == "/downloads/candidate.png"
    assert record["_edited_scenes"][0]["background_image_path"] == str(candidate_path.resolve())
    assert record["scene_asset_history"][0]["image_path"] == "/images/old.png"
    assert record["scene_clips"][0]["status"] == "stale"
    assert record["scene_image_candidates"] == {}


def test_approve_candidate_rejects_empty_or_unsafe_asset(monkeypatch, tmp_path: Path) -> None:
    image_root = tmp_path / "images"
    image_root.mkdir()
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"outside")
    record = _job(outside)

    monkeypatch.setattr(video, "_jobs", {record["job_id"]: record})
    monkeypatch.setattr(video, "_scene_batch_jobs", set())
    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda _name: image_root)
    monkeypatch.setattr(video, "_persist_job", lambda _record: None)

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            video.approve_video_job_scene_image(record["job_id"], 3, "candidate-3a")
        )
    assert exc.value.status_code == 422


def test_discard_candidate_obeys_render_lock(monkeypatch) -> None:
    record = {
        "job_id": "job-candidate-api",
        "status": "completed",
        "_rendering_edits": True,
        "scene_image_candidates": {"3": [{"candidate_id": "candidate-3a"}]},
    }
    monkeypatch.setattr(video, "_jobs", {record["job_id"]: record})
    monkeypatch.setattr(video, "_scene_batch_jobs", set())

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            video.discard_video_job_scene_image(record["job_id"], 3, "candidate-3a")
        )
    assert exc.value.status_code == 409


def test_discard_candidate_keeps_approved_image_and_clip(monkeypatch) -> None:
    record = {
        "job_id": "job-candidate-api",
        "status": "completed",
        "_source_scenes": [{"_source_scene_index": 3, "background_image_path": "/images/current.png"}],
        "scene_image_candidates": {"3": [{"candidate_id": "candidate-3a", "image_path": "/images/new.png"}]},
        "scene_clips": [{"scene_index": 3, "status": "updated"}],
    }
    monkeypatch.setattr(video, "_jobs", {record["job_id"]: record})
    monkeypatch.setattr(video, "_scene_batch_jobs", set())
    monkeypatch.setattr(video, "_persist_job", lambda _record: None)

    response = asyncio.run(
        video.discard_video_job_scene_image(record["job_id"], 3, "candidate-3a")
    )

    assert response["status"] == "discarded"
    assert record["_source_scenes"][0]["background_image_path"] == "/images/current.png"
    assert record["scene_clips"][0]["status"] == "updated"
    assert record["scene_image_candidates"] == {}
