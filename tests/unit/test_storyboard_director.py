"""Tests for the narration-aware cinematic storyboard planner."""
from __future__ import annotations

from modules.ai_video_studio.media.storyboard_director import build_cinematic_storyboard


def test_storyboard_creates_scene_specific_prompts_and_stable_ids() -> None:
    source = [
        {"voiceover_text": "A cidade cresceu ao redor do porto.", "description": "Vista do porto"},
        {"voiceover_text": "Os navios chegavam carregados.", "description": "Navios no cais"},
    ]
    first, report = build_cinematic_storyboard(
        source, studio_id="historical_documentary",
        character_ids=["historical_narrator"], object_ids=["sailing_ship"],
    )
    second, _ = build_cinematic_storyboard(
        source, studio_id="historical_documentary",
        character_ids=["historical_narrator"], object_ids=["sailing_ship"],
    )

    assert [item["storyboard_scene_id"] for item in first] == [
        item["storyboard_scene_id"] for item in second
    ]
    assert first[0]["storyboard_scene_id"] != first[1]["storyboard_scene_id"]
    assert first[0]["visual_prompt_full"] != first[1]["visual_prompt_full"]
    assert "não inventar eventos" in first[0]["visual_prompt_full"]
    assert first[0]["continuity"]["characters"] == ["historical_narrator"]
    assert first[0]["continuity"]["objects"] == ["sailing_ship"]
    assert "visuals_must_not_add_unsupported_facts" == report["historical_fact_policy"]


def test_storyboard_preserves_authored_prompt_and_detects_repetition() -> None:
    authored = "Uma caravela vista de perfil diante do cais antigo."
    scenes, report = build_cinematic_storyboard(
        [
            {"narration": "A embarcação chegou ao porto.", "visual_prompt": authored},
            {"narration": "O navio atracou pela manhã.", "visual_prompt": authored},
        ],
        studio_id="historical_documentary",
    )

    assert scenes[0]["visual_prompt"] == authored
    assert scenes[1]["visual_prompt"] == authored
    assert report["repeated_visuals"] == [
        {"scene_indices": [0, 1], "prompt": authored.lower()}
    ]
    assert any("Repeated visual concept" in warning for warning in report["warnings"])


def test_storyboard_flags_empty_scene_for_manual_review() -> None:
    scenes, report = build_cinematic_storyboard(
        [{"duration": 10.0}], studio_id="whymentary",
    )
    assert scenes[0]["storyboard_status"] == "needs_review"
    assert report["needs_review_count"] == 1
    assert report["ready_count"] == 0


def test_storyboard_rejects_unknown_studio_and_empty_input() -> None:
    import pytest

    with pytest.raises(ValueError):
        build_cinematic_storyboard([], studio_id="whymentary")
    with pytest.raises(ValueError):
        build_cinematic_storyboard([{"narration": "Texto"}], studio_id="unknown")

def test_storyboard_replaces_generic_prompt_with_directors_scene_suggestion() -> None:
    scenes, _ = build_cinematic_storyboard(
        [{
            "narration": "O manuscrito foi encontrado dentro de uma caixa.",
            "visual_prompt": "Cena",
            "visual_prompt_suggestion": "Close detalhado de um manuscrito dentro de uma caixa de madeira.",
        }],
        studio_id="historical_documentary",
    )
    assert "Close detalhado de um manuscrito" in scenes[0]["visual_prompt_full"]
    assert scenes[0]["visual_prompt"] != "Cena"
