from __future__ import annotations

import pytest

from modules.ai_video_studio.media.visual_asset_director import (
    build_scene_visual_brief,
    plan_scene_visuals,
    rank_visual_candidates,
)


def test_visual_brief_uses_scene_text_and_selected_studio_style() -> None:
    brief = build_scene_visual_brief(
        {"narration": "O navio chegou ao porto.", "description": "Navio no cais"},
        scene_index=2,
        studio_id="historical_documentary",
    )
    assert brief["status"] == "ready_for_generation"
    assert brief["shot_type"] == "close_up"
    assert "cinematic illustrated historical documentary" in brief["image_prompt"]
    assert "O navio chegou ao porto." == brief["source_text"]


def test_visual_brief_does_not_invent_scene_when_text_is_missing() -> None:
    brief = build_scene_visual_brief({}, studio_id="whymentary")
    assert brief["status"] == "needs_storyboard_detail"
    assert brief["requires_human_review"] is True
    assert "não criar conteúdo por inferência" in brief["visual_core"]


def test_visual_brief_preserves_locked_shot_type() -> None:
    brief = build_scene_visual_brief(
        {"narration": "A personagem abre a porta.", "shot_type": "close_up", "shot_type_locked": True},
        scene_index=1,
    )
    assert brief["shot_type"] == "close_up"
    assert brief["shot_type_locked"] is True


def test_visual_plan_varies_unlocked_shots_and_reports_repeated_visuals() -> None:
    plan = plan_scene_visuals([
        {"narration": "O navio chega ao porto."},
        {"narration": "A tripulação desembarca."},
        {"narration": "O navio chega ao porto."},
    ], studio_id="historical_documentary")
    assert [item["shot_type"] for item in plan["briefs"]] == [
        "wide_establishing", "medium_action", "close_up"
    ]
    assert plan["scene_count"] == 3
    assert plan["repeated_visual_groups"] == [[0, 2]]


def test_visual_plan_rejects_empty_or_invalid_input() -> None:
    with pytest.raises(ValueError):
        plan_scene_visuals([])
    with pytest.raises(ValueError):
        plan_scene_visuals([{"narration": "texto"}], studio_id="invalid")


def test_candidate_ranking_uses_metadata_overlap_not_pixel_claims() -> None:
    ranked = rank_visual_candidates(
        {"visual_prompt": "navio antigo no porto"},
        [
            {"candidate_id": "a", "prompt": "floresta e montanha"},
            {"candidate_id": "b", "prompt": "navio antigo atracado no porto"},
        ],
    )
    assert ranked[0]["candidate_id"] == "b"
    assert ranked[0]["metadata_match_score"] > ranked[1]["metadata_match_score"]


def test_visual_brief_applies_stable_mia_and_leo_identity_locks() -> None:
    from modules.ai_video_studio.media.visual_asset_director import build_scene_visual_brief

    brief = build_scene_visual_brief(
        {
            "narration": "Mia e Leo explicam como o corpo reage ao exercício.",
            "visual_prompt": "Mia e Leo em uma sala clara, conversando sobre movimento.",
            "character_ids": ["mia", "leo"],
        },
        scene_index=2,
        studio_id="felt_clay",
    )
    assert "cabelo loiro" in brief["image_prompt"]
    assert "camisa azul" in brief["image_prompt"]
    assert "cabelo castanho preso" in brief["image_prompt"]
    assert "vestido vermelho" in brief["image_prompt"]
    assert set(brief["character_visual_locks"]) == {"mia", "leo"}
    assert any("figurino" in item for item in brief["continuity_constraints"])


def test_visual_brief_does_not_inject_characters_when_none_are_requested() -> None:
    from modules.ai_video_studio.media.visual_asset_director import build_scene_visual_brief

    brief = build_scene_visual_brief(
        {"narration": "Uma paisagem ao amanhecer.", "visual_prompt": "Paisagem ao amanhecer com luz suave."},
        scene_index=0,
        studio_id="historical_documentary",
    )
    assert brief["character_visual_locks"] == {}
    assert brief["continuity_constraints"] == []
