from __future__ import annotations

from pathlib import Path

import pytest

from modules.ai_video_studio.media.scene_visual_asset_workflow import (
    approve_scene_image_candidate,
    discard_scene_image_candidate,
    list_scene_image_candidates,
    stage_scene_image_candidate,
)


def _job() -> dict:
    return {
        "job_id": "job-1",
        "project_id": "project-1",
        "status": "completed",
        "_source_scenes": [
            {"_source_scene_index": 0, "background_image_path": "old.png", "visual_prompt": "imagem antiga"}
        ],
        "scene_clips": [{"scene_index": 0, "status": "ready"}],
    }


def test_stage_candidate_does_not_replace_active_image() -> None:
    original = _job()
    updated = stage_scene_image_candidate(
        original, 0, {"candidate_id": "c1", "image_path": "/tmp/candidate.png"}
    )
    assert original.get("scene_image_candidates") is None
    assert updated["_source_scenes"][0]["background_image_path"] == "old.png"
    assert list_scene_image_candidates(updated, 0)[0]["status"] == "pending_approval"


def test_stage_rejects_duplicate_and_excess_candidates() -> None:
    record = stage_scene_image_candidate(
        _job(), 0, {"candidate_id": "c1", "image_path": "/tmp/1.png"}, max_per_scene=1
    )
    with pytest.raises(ValueError):
        stage_scene_image_candidate(record, 0, {"candidate_id": "c1", "image_path": "/tmp/2.png"})
    with pytest.raises(ValueError):
        stage_scene_image_candidate(record, 0, {"candidate_id": "c2", "image_path": "/tmp/2.png"})


def test_discard_keeps_active_image_and_clip_unchanged() -> None:
    record = stage_scene_image_candidate(
        _job(), 0, {"candidate_id": "c1", "image_path": "/tmp/candidate.png"}
    )
    updated, removed = discard_scene_image_candidate(record, 0, "c1")
    assert removed["candidate_id"] == "c1"
    assert updated["_source_scenes"][0]["background_image_path"] == "old.png"
    assert updated["scene_clips"][0]["status"] == "ready"
    assert list_scene_image_candidates(updated) == []


def test_approve_replaces_image_records_history_and_invalidates_clip(tmp_path: Path) -> None:
    image_root = tmp_path / "images"
    image_root.mkdir()
    candidate_path = image_root / "candidate.png"
    candidate_path.write_bytes(b"png-bytes")
    record = stage_scene_image_candidate(
        _job(), 0,
        {"candidate_id": "c1", "image_path": str(candidate_path), "prompt": "novo porto", "provider": "test"},
    )
    updated, approved = approve_scene_image_candidate(
        record, 0, "c1", image_root=image_root, image_url_builder=lambda path: f"/media/{Path(path).name}"
    )
    assert approved["candidate_id"] == "c1"
    assert updated["_edited_scenes"][0]["background_image_path"] == str(candidate_path.resolve())
    assert updated["scene_asset_history"][0]["image_path"] == "old.png"
    assert updated["scene_clips"][0]["status"] == "stale"
    assert updated["scene_assets"][0]["image_url"] == "/media/candidate.png"
    assert list_scene_image_candidates(updated) == []


def test_approve_rejects_path_outside_image_root(tmp_path: Path) -> None:
    image_root = tmp_path / "images"
    image_root.mkdir()
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"not-in-image-root")
    record = stage_scene_image_candidate(
        _job(), 0, {"candidate_id": "c1", "image_path": str(outside)}
    )
    with pytest.raises(ValueError, match="outside"):
        approve_scene_image_candidate(
            record, 0, "c1", image_root=image_root, image_url_builder=lambda path: path
        )


def test_approve_rejects_empty_candidate_file(tmp_path: Path) -> None:
    image_root = tmp_path / "images"
    image_root.mkdir()
    empty = image_root / "empty.png"
    empty.write_bytes(b"")
    record = stage_scene_image_candidate(
        _job(), 0, {"candidate_id": "c1", "image_path": str(empty)}
    )
    with pytest.raises(ValueError, match="empty"):
        approve_scene_image_candidate(
            record, 0, "c1", image_root=image_root, image_url_builder=lambda path: path
        )


def test_workflow_refuses_mutation_during_render_lock() -> None:
    record = {**_job(), "_rendering_edits": True}
    with pytest.raises(RuntimeError, match="locked"):
        stage_scene_image_candidate(record, 0, {"candidate_id": "c1", "image_path": "x.png"})


def test_workflow_requires_completed_job() -> None:
    record = {**_job(), "status": "processing"}
    with pytest.raises(ValueError, match="completion"):
        stage_scene_image_candidate(record, 0, {"candidate_id": "c1", "image_path": "x.png"})
