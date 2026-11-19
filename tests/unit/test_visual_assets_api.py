from __future__ import annotations

import asyncio

import pytest
from fastapi import HTTPException

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
    assert record["_edited_scenes"][0]["background_image_path"] is None
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
