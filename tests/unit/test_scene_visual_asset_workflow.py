from __future__ import annotations

from pathlib import Path

import pytest

from modules.ai_video_studio.media.scene_visual_asset_workflow import (
    approve_scene_image_candidate,
    list_scene_image_history,
    restore_scene_image_history,
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
    assert updated["scene_asset_history"][0]["history_id"]
    assert updated["scene_asset_history"][0]["reason"] == "candidate_approved"
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



def test_history_listing_hides_paths_and_marks_missing_assets(tmp_path: Path) -> None:
    image_root = tmp_path / "images"
    image_root.mkdir()
    image = image_root / "previous.png"
    image.write_bytes(b"image-bytes")
    record = {**_job(), "scene_asset_history": [
        {"history_id": "h1", "scene_index": 0, "image_path": str(image), "prompt": "porto antigo"},
        {"history_id": "h2", "scene_index": 0, "image_path": str(tmp_path / "outside.png")},
    ]}
    history = list_scene_image_history(record, 0, image_root=image_root, image_url_builder=lambda path: f"/media/{Path(path).name}")
    assert history[0]["history_id"] == "h1"
    assert history[0]["available"] is True
    assert history[0]["image_url"] == "/media/previous.png"
    assert "image_path" not in history[0]
    assert history[1]["available"] is False
    assert history[1]["image_url"] is None


def test_restore_history_preserves_current_as_undo_and_stales_only_target_clip(tmp_path: Path) -> None:
    image_root = tmp_path / "images"
    image_root.mkdir()
    previous, current, other = image_root / "previous.png", image_root / "current.png", image_root / "other.png"
    previous.write_bytes(b"previous")
    current.write_bytes(b"current")
    other.write_bytes(b"other")
    record = {
        **_job(),
        "_source_scenes": [
            {"_source_scene_index": 0, "background_image_path": str(current), "visual_prompt": "imagem atual"},
            {"_source_scene_index": 1, "background_image_path": str(other)},
        ],
        "scene_asset_history": [{"history_id": "h1", "scene_index": 0, "image_path": str(previous), "prompt": "imagem anterior", "provider": "test"}],
        "scene_clips": [{"scene_index": 0, "status": "ready"}, {"scene_index": 1, "status": "ready"}],
    }
    updated, restored = restore_scene_image_history(record, 0, "h1", image_root=image_root, image_url_builder=lambda path: f"/media/{Path(path).name}")
    assert restored["history_id"] == "h1"
    assert updated["_edited_scenes"][0]["background_image_path"] == str(previous.resolve())
    assert updated["_edited_scenes"][0]["visual_prompt"] == "imagem anterior"
    assert updated["scene_clips"][0]["status"] == "stale"
    assert updated["scene_clips"][1]["status"] == "ready"
    assert updated["scene_asset_history"][0]["image_path"] == str(current.resolve())
    assert updated["scene_asset_history"][0]["reason"] == "history_restore_undo"
    assert record["_source_scenes"][0]["background_image_path"] == str(current)


def test_restore_history_rejects_missing_or_external_file(tmp_path: Path) -> None:
    image_root = tmp_path / "images"
    image_root.mkdir()
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"outside")
    record = {**_job(), "scene_asset_history": [{"history_id": "h1", "scene_index": 0, "image_path": str(outside)}]}
    with pytest.raises(ValueError, match="outside"):
        restore_scene_image_history(record, 0, "h1", image_root=image_root, image_url_builder=lambda path: path)


def test_restore_history_rejects_unknown_entry_and_render_lock(tmp_path: Path) -> None:
    image_root = tmp_path / "images"
    image_root.mkdir()
    previous = image_root / "previous.png"
    previous.write_bytes(b"previous")
    record = {**_job(), "scene_asset_history": [{"history_id": "h1", "scene_index": 0, "image_path": str(previous)}]}
    with pytest.raises(KeyError):
        restore_scene_image_history(record, 0, "missing", image_root=image_root, image_url_builder=lambda path: path)
    with pytest.raises(RuntimeError, match="locked"):
        restore_scene_image_history({**record, "_rendering_edits": True}, 0, "h1", image_root=image_root, image_url_builder=lambda path: path)
