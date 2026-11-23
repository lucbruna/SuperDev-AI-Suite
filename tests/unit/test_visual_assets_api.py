from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from fastapi import HTTPException

from modules.ai_video_studio.api.routes import assets as asset_routes
from modules.ai_video_studio.api.routes import video, visual_assets


def _record() -> dict:
    return {
        "job_id": "job-visual-1",
        "project_id": "project-1",
        "status": "completed",
        "params": {"studio_id": "historical_documentary"},
        "_source_scenes": [
            {
                "_source_scene_index": 4,
                "description": "Navio de madeira chega ao porto",
                "narration": "O navio chega ao porto.",
            }
        ],
        "scene_image_candidates": {
            "4": [
                {
                    "candidate_id": "candidate-1",
                    "image_path": "/private/internal/path.png",
                    "image_url": "/downloads/candidate.png",
                    "provider": "test",
                    "prompt": "navio antigo no porto",
                    "status": "pending_approval",
                }
            ]
        },
    }


def test_visual_plan_preview_is_non_destructive(monkeypatch) -> None:
    record = _record()
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": record})
    saved = []
    monkeypatch.setattr(video, "_persist_job", lambda item: saved.append(item.copy()))

    response = asyncio.run(
        visual_assets.create_job_visual_plan(
            "job-visual-1", visual_assets.VisualPlanRequest()
        )
    )

    assert response["applied"] is False
    assert response["plan"]["scene_count"] == 1
    assert response["plan"]["briefs"][0]["scene_index"] == 4
    assert record.get("scene_visual_plan") is None
    assert saved == []


def test_visual_plan_apply_persists_briefs_without_replacing_image(monkeypatch) -> None:
    record = _record()
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": record})
    saved = []
    monkeypatch.setattr(video, "_persist_job", lambda item: saved.append(item["job_id"]))

    response = asyncio.run(
        visual_assets.create_job_visual_plan(
            "job-visual-1",
            visual_assets.VisualPlanRequest(apply_suggestions=True),
        )
    )

    assert response["applied"] is True
    assert record["scene_visual_plan"]["images_replaced"] is False
    assert record["_edited_scenes"][0]["visual_brief"]["status"] == "ready_for_generation"
    assert "background_image_path" not in record["_edited_scenes"][0]
    assert record["_edited_scenes"][0]["visual_prompt_suggestion"] == "Navio de madeira chega ao porto"
    assert saved == ["job-visual-1"]


def test_visual_plan_rejects_active_render_lock(monkeypatch) -> None:
    record = {**_record(), "_rendering_edits": True}
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": record})

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            visual_assets.create_job_visual_plan(
                "job-visual-1",
                visual_assets.VisualPlanRequest(apply_suggestions=True),
            )
        )
    assert exc.value.status_code == 409


def test_candidate_listing_ranks_and_does_not_expose_local_paths(monkeypatch) -> None:
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": _record()})

    response = asyncio.run(
        visual_assets.list_job_scene_image_candidates("job-visual-1", 4)
    )

    assert response["candidate_count"] == 1
    candidate = response["candidates"][0]
    assert candidate["candidate_id"] == "candidate-1"
    assert candidate["image_url"] == "/downloads/candidate.png"
    assert "image_path" not in candidate
    assert "private" not in str(response)


def test_candidate_listing_returns_404_for_unknown_scene(monkeypatch) -> None:
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": _record()})

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            visual_assets.list_job_scene_image_candidates("job-visual-1", 999)
        )
    assert exc.value.status_code == 404


def test_visual_plan_returns_404_for_unknown_job(monkeypatch) -> None:
    monkeypatch.setattr(video, "_jobs", {})

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            visual_assets.create_job_visual_plan(
                "missing", visual_assets.VisualPlanRequest()
            )
        )
    assert exc.value.status_code == 404



def test_candidate_listing_returns_multiple_options_for_one_scene(monkeypatch) -> None:
    record = _record()
    record["scene_image_candidates"]["4"].append({
        "candidate_id": "candidate-2",
        "image_path": "/private/internal/second.png",
        "image_url": "/downloads/second.png",
        "provider": "test",
        "prompt": "porto histórico em luz dourada",
        "status": "pending_approval",
    })
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": record})

    response = asyncio.run(
        visual_assets.list_job_scene_image_candidates("job-visual-1", 4)
    )

    assert response["candidate_count"] == 2
    assert {item["candidate_id"] for item in response["candidates"]} == {
        "candidate-1", "candidate-2"
    }
    assert all("image_path" not in item for item in response["candidates"])



def test_image_history_list_sanitizes_paths(monkeypatch, tmp_path) -> None:
    image_root = tmp_path / "images"
    image_root.mkdir()
    previous = image_root / "previous.png"
    previous.write_bytes(b"image-bytes")
    record = _record()
    record["scene_asset_history"] = [{"history_id": "history-1", "scene_index": 4, "image_path": str(previous), "prompt": "navio no porto"}]
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": record})
    from modules.ai_video_studio.media import output_paths
    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: image_root)
    monkeypatch.setattr(visual_assets, "to_download_url", lambda path: f"/media/{Path(path).name}", raising=False)
    response = asyncio.run(visual_assets.list_job_scene_image_history("job-visual-1", 4))
    assert response["history_count"] == 1
    assert response["history"][0]["history_id"] == "history-1"
    assert response["history"][0]["available"] is True
    assert "image_path" not in response["history"][0]


def test_image_history_restore_persists_and_marks_target_clip_stale(monkeypatch, tmp_path) -> None:
    image_root = tmp_path / "images"
    image_root.mkdir()
    previous, current = image_root / "previous.png", image_root / "current.png"
    previous.write_bytes(b"previous")
    current.write_bytes(b"current")
    record = _record()
    record["_source_scenes"][0]["background_image_path"] = str(current)
    record["scene_clips"] = [{"scene_index": 4, "status": "ready"}]
    record["scene_asset_history"] = [{"history_id": "history-1", "scene_index": 4, "image_path": str(previous), "prompt": "imagem anterior"}]
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": record})
    from modules.ai_video_studio.media import output_paths
    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: image_root)
    monkeypatch.setattr(visual_assets, "to_download_url", lambda path: f"/media/{Path(path).name}", raising=False)
    saved = []
    monkeypatch.setattr(video, "_persist_job", lambda item: saved.append(item.copy()))
    response = asyncio.run(visual_assets.restore_job_scene_image_history("job-visual-1", 4, "history-1"))
    assert response["status"] == "restored"
    assert response["render_required"] is True
    assert record["_edited_scenes"][0]["background_image_path"] == str(previous.resolve())
    assert record["scene_clips"][0]["status"] == "stale"
    assert record["scene_asset_history"][0]["image_path"] == str(current.resolve())
    assert len(saved) == 1


def test_image_history_restore_rejects_active_render_lock(monkeypatch) -> None:
    record = {**_record(), "_rendering_edits": True}
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": record})
    with pytest.raises(HTTPException) as exc:
        asyncio.run(visual_assets.restore_job_scene_image_history("job-visual-1", 4, "history-1"))
    assert exc.value.status_code == 409



def test_scene_image_framing_persists_transform_and_invalidates_only_target_clip(monkeypatch) -> None:
    record = _record()
    record["scene_clips"] = [
        {"scene_index": 4, "status": "ready"},
        {"scene_index": 5, "status": "ready"},
    ]
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": record})
    saved = []
    monkeypatch.setattr(video, "_persist_job", lambda item: saved.append(item.copy()))
    response = asyncio.run(
        visual_assets.update_job_scene_image_framing(
            "job-visual-1", 4,
            visual_assets.SceneImageFramingRequest(scale=1.6, offset_x=-0.5, offset_y=0.25),
        )
    )
    assert response["status"] == "saved"
    assert response["clip_invalidated"] is True
    assert response["render_started"] is False
    assert record["_edited_scenes"][0]["background_image_transform"] == {
        "scale": 1.6, "offset_x": -0.5, "offset_y": 0.25,
    }
    assert record["scene_clips"][0]["status"] == "stale"
    assert record["scene_clips"][1]["status"] == "ready"
    assert len(saved) == 1


def test_scene_image_framing_rejects_active_render_lock(monkeypatch) -> None:
    record = {**_record(), "_rendering_edits": True}
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": record})
    with pytest.raises(HTTPException) as exc:
        asyncio.run(visual_assets.update_job_scene_image_framing(
            "job-visual-1", 4, visual_assets.SceneImageFramingRequest(scale=1.2)
        ))
    assert exc.value.status_code == 409


def test_scene_image_framing_rejects_unknown_scene(monkeypatch) -> None:
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": _record()})
    with pytest.raises(HTTPException) as exc:
        asyncio.run(visual_assets.update_job_scene_image_framing(
            "job-visual-1", 999, visual_assets.SceneImageFramingRequest()
        ))
    assert exc.value.status_code == 404

    
def test_scene_image_framing_listing_returns_saved_values_by_source_index(monkeypatch) -> None:
    record = _record()
    record["_source_scenes"][0]["background_image_transform"] = {
        "scale": 1.75, "offset_x": -0.25, "offset_y": 0.5,
    }
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": record})
    response = asyncio.run(visual_assets.get_job_scene_image_framing("job-visual-1"))
    assert response["job_id"] == "job-visual-1"
    assert response["scenes"]["4"] == {
        "scale": 1.75, "offset_x": -0.25, "offset_y": 0.5,
    }


def test_scene_image_framing_listing_defaults_legacy_scenes(monkeypatch) -> None:
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": _record()})
    response = asyncio.run(visual_assets.get_job_scene_image_framing("job-visual-1"))
    assert response["scenes"]["4"] == {
        "scale": 1.0, "offset_x": 0.0, "offset_y": 0.0,
    }

def test_character_identity_profile_is_saved_and_used_by_visual_plan(monkeypatch, tmp_path) -> None:
    record = _record()
    reference_file = tmp_path / "mia-reference.png"
    reference_file.write_bytes(b"valid-test-image-bytes")
    monkeypatch.setattr(asset_routes, "_assets", {"asset-mia-approved": {"id": "asset-mia-approved", "project_id": "project-1", "name": "Mia reference", "asset_type": "image", "mime_type": "image/png", "file_path": str(reference_file), "file_size_bytes": reference_file.stat().st_size}})
    record["_source_scenes"][0]["character_ids"] = ["mia"]
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": record})
    saved = []
    monkeypatch.setattr(video, "_persist_job", lambda item: saved.append(item.copy()))

    profile_response = asyncio.run(
        visual_assets.save_job_character_identity(
            "job-visual-1",
            "mia",
            visual_assets.CharacterIdentityRequest(
                name="Mia",
                visual_identity="Menina de cabelo castanho preso, vestido vermelho, estilo felt-clay.",
                reference_asset_ids=["asset-mia-approved"],
                invariants=["cabelo castanho preso", "vestido vermelho"],
                forbidden_variations=["cabelo loiro", "roupa azul"],
            ),
        )
    )
    assert profile_response["generation_started"] is False
    assert profile_response["pixel_identity_verified"] is False
    assert profile_response["profile"]["review_status"] == "needs_reference_review"
    assert profile_response["profile"]["approved_reference_asset_ids"] == []
    review_response = asyncio.run(
        visual_assets.review_job_character_reference(
            "job-visual-1", "mia", "asset-mia-approved",
            visual_assets.CharacterReferenceReviewRequest(status="approved"),
        )
    )
    assert review_response["review_status"] == "references_approved"
    assert review_response["approved_reference_asset_ids"] == ["asset-mia-approved"]
    plan_response = asyncio.run(
        visual_assets.create_job_visual_plan(
            "job-visual-1", visual_assets.VisualPlanRequest()
        )
    )
    brief = plan_response["plan"]["briefs"][0]
    assert brief["character_identity_prompts"][0]["character_id"] == "mia"
    assert "cabelo castanho preso" in brief["visual_core"]
    assert "vestido vermelho" in brief["visual_core"]
    assert "\n\nCHARACTER IDENTITY" in brief["visual_core"]
    assert brief["character_identity_review"]["status"] == "references_attached"
    assert len(saved) == 1


def test_character_identity_audit_marks_unknown_character_for_review(monkeypatch) -> None:
    record = _record()
    record["_source_scenes"][0]["character_ids"] = ["leo"]
    record["character_identities"] = {}
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": record})

    response = asyncio.run(
        visual_assets.get_job_character_identity_audit("job-visual-1")
    )

    assert response["audit"]["review_scene_count"] == 1
    assert response["audit"]["scenes"][0]["status"] == "unknown_character"
    assert response["audit"]["pixel_identity_verified"] is False
