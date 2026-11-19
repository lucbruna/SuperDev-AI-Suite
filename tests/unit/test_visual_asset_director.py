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


def test_visual_brief_accepts_arbitrary_user_style_and_continuity() -> None:
    brief = build_scene_visual_brief(
        {
            "narration": "A cidade desperta sob uma tempestade.",
            "visual_prompt": "Vista aérea de uma cidade costeira durante a tempestade.",
            "visual_style": "Anime cyberpunk com aquarela, neon magenta e chuva volumétrica.",
            "continuity_prompt": "Manter o mesmo protagonista, casaco amarelo e cicatriz no rosto.",
        },
        scene_index=0,
        studio_id="custom",
    )
    assert "Anime cyberpunk com aquarela" in brief["image_prompt"]
    assert "casaco amarelo" in brief["image_prompt"]
    assert brief["requested_style"].startswith("Anime cyberpunk")
    assert brief["continuity_prompt"].startswith("Manter o mesmo protagonista")


def test_visual_brief_does_not_inject_fixed_characters() -> None:
    brief = build_scene_visual_brief(
        {"narration": "Uma paisagem ao amanhecer.", "visual_prompt": "Paisagem ao amanhecer com luz suave."},
        scene_index=0,
        studio_id="historical_documentary",
    )
    assert "Mia" not in brief["image_prompt"]
    assert "Leo" not in brief["image_prompt"]
    assert brief["continuity_prompt"] == ""
