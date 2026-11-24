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
    assert exc.value.status_code == 503


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
    pending_plan = asyncio.run(
        visual_assets.create_job_visual_plan(
            "job-visual-1", visual_assets.VisualPlanRequest()
        )
    )
    pending_prompt = pending_plan["plan"]["briefs"][0]["character_identity_prompts"][0]
    assert pending_prompt["requires_human_review"] is True
    assert pending_prompt["reference_asset_ids"] == []
    assert "asset-mia-approved" not in pending_prompt["prompt"]
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
    assert len(saved) == 2


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


def test_character_identity_rejects_reference_asset_from_another_project(monkeypatch, tmp_path) -> None:
    reference_file = tmp_path / "foreign.png"
    reference_file.write_bytes(b"image")
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": _record()})
    monkeypatch.setattr(asset_routes, "_assets", {
        "foreign-image": {
            "id": "foreign-image", "project_id": "another-project",
            "asset_type": "image", "mime_type": "image/png",
            "file_path": str(reference_file), "file_size_bytes": 5,
        }
    })
    with pytest.raises(HTTPException) as exc:
        asyncio.run(visual_assets.save_job_character_identity(
            "job-visual-1", "mia",
            visual_assets.CharacterIdentityRequest(
                name="Mia", visual_identity="Mia felt character",
                reference_asset_ids=["foreign-image"],
            ),
        ))
    assert exc.value.status_code == 404


def test_character_identity_rejects_missing_reference_asset(monkeypatch) -> None:
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": _record()})
    monkeypatch.setattr(asset_routes, "_assets", {})
    with pytest.raises(HTTPException) as exc:
        asyncio.run(visual_assets.save_job_character_identity(
            "job-visual-1", "mia",
            visual_assets.CharacterIdentityRequest(
                name="Mia", visual_identity="Mia felt character",
                reference_asset_ids=["does-not-exist"],
            ),
        ))
    assert exc.value.status_code == 404


def test_character_reference_review_rejects_non_image_asset(monkeypatch, tmp_path) -> None:
    file_path = tmp_path / "voice.wav"
    file_path.write_bytes(b"audio")
    record = _record()
    record["character_identities"] = {
        "mia": {
            "reference_asset_ids": ["voice-asset"],
            "approved_reference_asset_ids": [],
            "reference_asset_reviews": {"voice-asset": "pending"},
        }
    }
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": record})
    monkeypatch.setattr(asset_routes, "_assets", {
        "voice-asset": {
            "id": "voice-asset", "project_id": "project-1",
            "asset_type": "audio", "mime_type": "audio/wav",
            "file_path": str(file_path), "file_size_bytes": 5,
        }
    })
    with pytest.raises(HTTPException) as exc:
        asyncio.run(visual_assets.review_job_character_reference(
            "job-visual-1", "mia", "voice-asset",
            visual_assets.CharacterReferenceReviewRequest(status="approved"),
        ))
    assert exc.value.status_code == 422


def test_character_reference_rejection_removes_previously_approved_asset(monkeypatch, tmp_path) -> None:
    file_path = tmp_path / "mia.png"
    file_path.write_bytes(b"image")
    record = _record()
    record["character_identities"] = {
        "mia": {
            "reference_asset_ids": ["mia-image"],
            "approved_reference_asset_ids": ["mia-image"],
            "reference_asset_reviews": {"mia-image": "approved"},
        }
    }
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": record})
    monkeypatch.setattr(asset_routes, "_assets", {
        "mia-image": {
            "id": "mia-image", "project_id": "project-1",
            "asset_type": "image", "mime_type": "image/png",
            "file_path": str(file_path), "file_size_bytes": 5,
        }
    })
    saved = []
    monkeypatch.setattr(video, "_persist_job", lambda item: saved.append(item.copy()))
    response = asyncio.run(visual_assets.review_job_character_reference(
        "job-visual-1", "mia", "mia-image",
        visual_assets.CharacterReferenceReviewRequest(status="rejected"),
    ))
    assert response["status"] == "rejected"
    assert response["approved_reference_asset_ids"] == []
    assert response["review_status"] == "needs_reference_review"
    assert record["character_identities"]["mia"]["approved_reference_asset_ids"] == []
    assert len(saved) == 1


def test_visual_plan_drops_deleted_approved_character_reference(monkeypatch) -> None:
    record = _record()
    record["_source_scenes"][0]["character_ids"] = ["mia"]
    record["character_identities"] = {
        "mia": {
            "character_id": "mia",
            "name": "Mia",
            "visual_identity": "Menina de cabelo castanho preso e vestido vermelho.",
            "reference_asset_ids": ["deleted-image"],
            "approved_reference_asset_ids": ["deleted-image"],
            "reference_asset_reviews": {"deleted-image": "approved"},
            "invariants": ["cabelo castanho preso", "vestido vermelho"],
            "forbidden_variations": [],
        }
    }
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": record})
    monkeypatch.setattr(asset_routes, "_assets", {})

    response = asyncio.run(
        visual_assets.create_job_visual_plan(
            "job-visual-1", visual_assets.VisualPlanRequest()
        )
    )

    brief = response["plan"]["briefs"][0]
    prompt = brief["character_identity_prompts"][0]
    assert prompt["reference_asset_ids"] == []
    assert prompt["requires_human_review"] is True
    assert "deleted-image" not in prompt["prompt"]
    assert record["character_identities"]["mia"]["approved_reference_asset_ids"] == ["deleted-image"]


def test_character_identity_reference_file_must_exist_and_be_nonempty(monkeypatch, tmp_path) -> None:
    missing_file = tmp_path / "missing.png"
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": _record()})
    monkeypatch.setattr(asset_routes, "_assets", {
        "missing-image": {
            "id": "missing-image", "project_id": "project-1",
            "asset_type": "image", "mime_type": "image/png",
            "file_path": str(missing_file), "file_size_bytes": 0,
        }
    })
    with pytest.raises(HTTPException) as exc:
        asyncio.run(visual_assets.save_job_character_identity(
            "job-visual-1", "mia",
            visual_assets.CharacterIdentityRequest(
                name="Mia", visual_identity="Mia felt character",
                reference_asset_ids=["missing-image"],
            ),
        ))
    assert exc.value.status_code == 422



def test_character_reference_generate_sends_only_approved_asset_bytes(monkeypatch, tmp_path):
    from io import BytesIO
    from PIL import Image

    reference = BytesIO()
    Image.new("RGB", (12, 12), (220, 40, 90)).save(reference, format="PNG")
    source_bytes = reference.getvalue()
    reference_file = tmp_path / "mia-reference.png"
    reference_file.write_bytes(source_bytes)
    output_file = tmp_path / "generated.png"
    output_file.write_bytes(source_bytes)
    record = _record()
    record["character_identities"] = {
        "mia": {
            "reference_asset_ids": ["mia-ref"],
            "approved_reference_asset_ids": ["mia-ref"],
            "reference_asset_reviews": {"mia-ref": "approved"},
        }
    }
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": record})
    monkeypatch.setattr(asset_routes, "_assets", {
        "mia-ref": {
            "id": "mia-ref", "project_id": "project-1", "name": "Mia",
            "asset_type": "image", "mime_type": "image/png",
            "file_path": str(reference_file), "file_size_bytes": len(source_bytes),
        }
    })
    captured = {}

    def fake_edit_image_bytes(data, prompt, **kwargs):
        captured.update(data=data, prompt=prompt, kwargs=kwargs)
        return {
            "provider": "automatic1111_compatible",
            "operation": "image_to_image",
            "reference_transmitted": True,
            "reference_bytes": len(data),
            "image_path": str(output_file),
            "seed": 123,
        }

    from modules.ai_video_studio.ai_image_generator.providers import local_diffusion
    monkeypatch.setattr(local_diffusion, "edit_image_bytes", fake_edit_image_bytes)
    monkeypatch.setattr(visual_assets, "to_download_url", lambda path: f"/media/{Path(path).name}")

    response = asyncio.run(visual_assets.generate_character_reference_edit(
        "job-visual-1", "mia", "mia-ref",
        visual_assets.CharacterReferenceEditRequest(prompt="Mia running in a forest"),
    ))

    assert captured["data"] == source_bytes
    assert captured["prompt"] == "Mia running in a forest"
    assert response["status"] == "reference_transmitted"
    assert response["reference_transmitted"] is True
    assert response["reference_asset_id"] == "mia-ref"
    assert response["pixel_identity_verified"] is False
    assert response["download_url"] == "/media/generated.png"


def test_character_reference_generate_rejects_pending_reference_without_provider_call(monkeypatch, tmp_path):
    reference_file = tmp_path / "mia.png"
    reference_file.write_bytes(b"image")
    record = _record()
    record["character_identities"] = {
        "mia": {
            "reference_asset_ids": ["mia-ref"],
            "approved_reference_asset_ids": [],
            "reference_asset_reviews": {"mia-ref": "pending"},
        }
    }
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": record})
    monkeypatch.setattr(asset_routes, "_assets", {
        "mia-ref": {
            "id": "mia-ref", "project_id": "project-1",
            "asset_type": "image", "mime_type": "image/png",
            "file_path": str(reference_file), "file_size_bytes": 5,
        }
    })

    from modules.ai_video_studio.ai_image_generator.providers import local_diffusion
    monkeypatch.setattr(
        local_diffusion, "edit_image_bytes",
        lambda *_args, **_kwargs: pytest.fail("provider must not receive pending references"),
    )
    with pytest.raises(HTTPException) as exc:
        asyncio.run(visual_assets.generate_character_reference_edit(
            "job-visual-1", "mia", "mia-ref",
            visual_assets.CharacterReferenceEditRequest(prompt="Edit Mia"),
        ))
    assert exc.value.status_code == 409



def test_scene_character_generation_stages_candidate_without_replacing_active_image(monkeypatch, tmp_path):
    from io import BytesIO
    from PIL import Image

    reference_buffer = BytesIO()
    Image.new("RGB", (16, 16), (200, 30, 80)).save(reference_buffer, format="PNG")
    reference_bytes = reference_buffer.getvalue()
    reference_file = tmp_path / "mia-reference.png"
    reference_file.write_bytes(reference_bytes)
    image_root = tmp_path / "images"
    image_root.mkdir()
    output_file = image_root / "generated.png"
    output_file.write_bytes(reference_bytes)

    record = _record()
    record["_source_scenes"][0].update({
        "character_ids": ["mia"],
        "visual_prompt": "Mia em uma floresta iluminada pelo sol",
        "background_image_path": str(image_root / "old-active.png"),
    })
    (image_root / "old-active.png").write_bytes(reference_bytes)
    record["character_identities"] = {
        "mia": {
            "character_id": "mia",
            "name": "Mia",
            "visual_identity": "Menina de cabelo castanho preso, vestido vermelho, estilo felt-clay.",
            "reference_asset_ids": ["mia-ref"],
            "approved_reference_asset_ids": ["mia-ref"],
            "reference_asset_reviews": {"mia-ref": "approved"},
            "invariants": ["cabelo castanho preso", "vestido vermelho"],
            "forbidden_variations": ["cabelo loiro", "roupa azul"],
        }
    }
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": record})
    monkeypatch.setattr(asset_routes, "_assets", {
        "mia-ref": {
            "id": "mia-ref", "project_id": "project-1", "name": "Mia reference",
            "asset_type": "image", "mime_type": "image/png",
            "file_path": str(reference_file), "file_size_bytes": len(reference_bytes),
        }
    })
    from modules.ai_video_studio.media import output_paths
    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda name: image_root)
    from modules.ai_video_studio.ai_image_generator.providers import local_diffusion
    captured = {}
    def fake_edit(data, prompt, **kwargs):
        captured.update(data=data, prompt=prompt, kwargs=kwargs)
        return {
            "provider": "automatic1111_compatible", "operation": "image_to_image",
            "reference_transmitted": True, "reference_bytes": len(data),
            "image_path": str(output_file), "seed": 77,
        }
    monkeypatch.setattr(local_diffusion, "edit_image_bytes", fake_edit)
    monkeypatch.setattr(visual_assets, "to_download_url", lambda path: f"/media/{Path(path).name}")
    persisted = []
    monkeypatch.setattr(video, "_persist_job", lambda item: persisted.append(item.copy()))

    response = asyncio.run(visual_assets.generate_scene_character_image(
        "job-visual-1", 4, visual_assets.SceneCharacterImageGenerationRequest()
    ))

    assert captured["data"] == reference_bytes
    assert "Mia em uma floresta" in captured["prompt"]
    assert "vestido vermelho" in captured["prompt"]
    assert response["status"] == "pending_approval"
    assert response["reference_transmitted"] is True
    assert response["active_image_replaced"] is False
    assert record["_source_scenes"][0]["background_image_path"] == str(image_root / "old-active.png")
    candidate = next(
        item for item in record["scene_image_candidates"]["4"]
        if item["candidate_id"] == response["candidate_id"]
    )
    assert candidate["character_id"] == "mia"
    assert candidate["reference_asset_id"] == "mia-ref"
    assert candidate["status"] == "pending_approval"
    assert len(persisted) == 1


def test_scene_character_generation_requires_comfyui_for_multiple_characters(monkeypatch, tmp_path):
    reference_file = tmp_path / "reference.png"
    reference_file.write_bytes(b"image")
    record = _record()
    record["_source_scenes"][0]["character_ids"] = ["mia", "leo"]
    record["character_identities"] = {
        character_id: {
            "character_id": character_id, "name": character_id,
            "visual_identity": "Test character",
            "reference_asset_ids": [f"{character_id}-ref"],
            "approved_reference_asset_ids": [f"{character_id}-ref"],
        }
        for character_id in ("mia", "leo")
    }
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": record})
    monkeypatch.setattr(asset_routes, "_assets", {
        f"{character_id}-ref": {
            "id": f"{character_id}-ref", "project_id": "project-1",
            "asset_type": "image", "mime_type": "image/png",
            "file_path": str(reference_file), "file_size_bytes": 5,
        }
        for character_id in ("mia", "leo")
    })
    from modules.ai_video_studio.ai_image_generator.providers import local_diffusion
    monkeypatch.setattr(
        local_diffusion, "edit_image_bytes",
        lambda *_args, **_kwargs: pytest.fail("provider must not be called for multi-character scene"),
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(visual_assets.generate_scene_character_image(
            "job-visual-1", 4, visual_assets.SceneCharacterImageGenerationRequest(prompt="Two characters")
        ))
    assert exc.value.status_code == 409


def test_scene_character_generation_uses_comfyui_for_multiple_approved_characters(monkeypatch, tmp_path):
    from io import BytesIO
    from PIL import Image

    reference_buffer = BytesIO()
    Image.new("RGB", (16, 16), (90, 120, 180)).save(reference_buffer, format="PNG")
    reference_bytes = reference_buffer.getvalue()
    mia_file = tmp_path / "mia.png"
    leo_file = tmp_path / "leo.png"
    mia_file.write_bytes(reference_bytes)
    leo_file.write_bytes(reference_bytes)
    image_root = tmp_path / "images"
    image_root.mkdir()
    output_file = image_root / "comfyui-scene.png"

    record = _record()
    record["_source_scenes"][0].update({
        "character_ids": ["mia", "leo"],
        "visual_prompt": "Mia e Leo conversam em uma praça de feltro",
    })
    record["character_identities"] = {
        character_id: {
            "character_id": character_id,
            "name": character_id.title(),
            "visual_identity": f"{character_id.title()} felt character",
            "reference_asset_ids": [f"{character_id}-ref"],
            "approved_reference_asset_ids": [f"{character_id}-ref"],
            "reference_asset_reviews": {f"{character_id}-ref": "approved"},
            "invariants": [f"{character_id} invariant"],
            "forbidden_variations": [],
        }
        for character_id in ("mia", "leo")
    }
    monkeypatch.setattr(video, "_jobs", {"job-visual-1": record})
    monkeypatch.setattr(asset_routes, "_assets", {
        f"{character_id}-ref": {
            "id": f"{character_id}-ref", "project_id": "project-1",
            "asset_type": "image", "mime_type": "image/png",
            "file_path": str(path), "file_size_bytes": path.stat().st_size,
        }
        for character_id, path in (("mia", mia_file), ("leo", leo_file))
    })
    from modules.ai_video_studio.media import output_paths
    monkeypatch.setattr(output_paths, "get_subsystem_dir", lambda _name: image_root)

    captured = {}
    class FakeComfyUIImageProvider:
        def is_configured(self):
            return True

        def generate(self, **kwargs):
            captured.update(kwargs)
            Image.new("RGB", (32, 32), (30, 180, 90)).save(kwargs["output_path"])
            return {
                "provider": "comfyui_image_workflow",
                "prompt_id": "fake-image-job",
                "output_path": str(kwargs["output_path"]),
                "character_ids": ["leo", "mia"],
                "reference_count": 2,
            }

    from modules.ai_video_studio.ai_image_generator.providers import comfyui_image_provider
    monkeypatch.setattr(comfyui_image_provider, "ComfyUIImageProvider", FakeComfyUIImageProvider)
    monkeypatch.setattr(visual_assets, "to_download_url", lambda path: f"/media/{Path(path).name}")
    persisted = []
    monkeypatch.setattr(video, "_persist_job", lambda item: persisted.append(item.copy()))

    response = asyncio.run(visual_assets.generate_scene_character_image(
        "job-visual-1", 4, visual_assets.SceneCharacterImageGenerationRequest()
    ))

    assert set(captured["references_by_character"]) == {"mia", "leo"}
    assert captured["references_by_character"]["mia"] == mia_file
    assert captured["references_by_character"]["leo"] == leo_file
    assert "Mia felt character" in captured["prompt"]
    assert "Leo felt character" in captured["prompt"]
    assert response["provider"] == "comfyui_image_workflow"
    assert response["character_ids"] == ["mia", "leo"]
    assert response["reference_asset_ids"] == ["mia-ref", "leo-ref"]
    assert response["active_image_replaced"] is False
    candidate = next(
        item for item in record["scene_image_candidates"]["4"]
        if item["candidate_id"] == response["candidate_id"]
    )
    assert candidate["status"] == "pending_approval"
    assert candidate["pixel_identity_verified"] is False
    assert len(persisted) == 1
