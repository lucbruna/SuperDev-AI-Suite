from __future__ import annotations

import asyncio
from io import BytesIO
from pathlib import Path

import pytest
from fastapi import HTTPException
from PIL import Image
from starlette.datastructures import Headers, UploadFile

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



def _png_upload(*, color: str = "red", content_type: str = "image/png") -> UploadFile:
    buffer = BytesIO()
    Image.new("RGB", (128, 96), color=color).save(buffer, format="PNG")
    buffer.seek(0)
    return UploadFile(
        filename="my-scene.png",
        file=buffer,
        headers=Headers({"content-type": content_type}),
    )


def test_upload_scene_image_stages_candidate_without_replacing_active_image(monkeypatch, tmp_path: Path) -> None:
    image_root = tmp_path / "images"
    image_root.mkdir()
    record = {
        "job_id": "job-candidate-api",
        "status": "completed",
        "_source_scenes": [
            {"_source_scene_index": 3, "background_image_path": "/images/current.png", "visual_prompt": "current"},
        ],
        "scene_clips": [{"scene_index": 3, "status": "updated"}],
    }
    persisted = []
    monkeypatch.setattr(video, "_jobs", {record["job_id"]: record})
    monkeypatch.setattr(video, "_scene_batch_jobs", set())
    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda _name: image_root)
    monkeypatch.setattr(video, "to_download_url", lambda path: f"/downloads/{Path(path).name}")
    monkeypatch.setattr(video, "_persist_job", lambda current: persisted.append(current.copy()))

    response = asyncio.run(
        video.upload_video_job_scene_image(record["job_id"], 3, _png_upload())
    )

    assert response["status"] == "candidate"
    assert response["approval_required"] is True
    assert response["operation"] == "manual_upload"
    assert len(persisted) == 1
    assert record["_source_scenes"][0]["background_image_path"] == "/images/current.png"
    assert record["scene_clips"][0]["status"] == "updated"
    candidate = record["scene_image_candidates"]["3"][0]
    assert candidate["candidate_id"] == response["candidate_id"]
    assert candidate["provider"] == "user_upload"
    assert Path(candidate["image_path"]).is_file()
    with Image.open(candidate["image_path"]) as saved:
        assert saved.format == "PNG"
        assert saved.size == (128, 96)


def test_upload_scene_image_rejects_mime_mismatch_and_bad_payload(monkeypatch, tmp_path: Path) -> None:
    image_root = tmp_path / "images"
    image_root.mkdir()
    record = {
        "job_id": "job-candidate-api",
        "status": "completed",
        "_source_scenes": [{"_source_scene_index": 3}],
    }
    monkeypatch.setattr(video, "_jobs", {record["job_id"]: record})
    monkeypatch.setattr(video, "_scene_batch_jobs", set())
    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda _name: image_root)

    with pytest.raises(HTTPException) as mime_error:
        asyncio.run(
            video.upload_video_job_scene_image(
                record["job_id"], 3, _png_upload(content_type="application/pdf")
            )
        )
    assert mime_error.value.status_code == 415

    invalid = UploadFile(
        filename="broken.png",
        file=BytesIO(b"not-an-image"),
        headers=Headers({"content-type": "image/png"}),
    )
    with pytest.raises(HTTPException) as image_error:
        asyncio.run(video.upload_video_job_scene_image(record["job_id"], 3, invalid))
    assert image_error.value.status_code == 422
