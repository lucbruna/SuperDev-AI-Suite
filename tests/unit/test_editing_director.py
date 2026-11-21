"""Regression tests for the automatic editing director."""
from __future__ import annotations

from modules.ai_video_studio.media.editing_director import classify_shot, direct_storyboard


def test_classify_shot_uses_visual_evidence_and_avoids_repetition() -> None:
    assert classify_shot({"description": "Panorama da cidade inteira"}) == "establishing"
    assert classify_shot({"description": "Close detail de um manuscrito"}) == "detail"
    assert classify_shot({"description": "O personagem caminha pelo mercado"}) == "tracking"
    assert classify_shot({"description": "Close-up do rosto e expressão"}) == "close_up"
    assert classify_shot({"description": "Cena comum"}, "medium") == "close_up"


def test_director_adds_varied_shots_and_cameras_for_historical_studio() -> None:
    scenes = [
        {"duration": 2.0, "description": "Panorama da cidade inteira", "chapter": "A"},
        {"duration": 2.0, "description": "Um personagem caminha pela praça", "chapter": "A"},
        {"duration": 2.0, "description": "Detalhe de um manuscrito", "chapter": "B"},
    ]
    directed = direct_storyboard(scenes, studio_id="historical_documentary", fps=24, fallback_duration=2.0)
    assert [scene["shot_type"] for scene in directed] == ["establishing", "tracking", "detail"]
    assert all(len(scene["camera"]["keyframes"]) == 3 for scene in directed)
    assert directed[0]["transition_out"]["type"] == "crossfade"
    assert directed[1]["transition_out"]["type"] == "fade_through_black"
    assert "camera" not in scenes[0]  # source storyboard remains unchanged


def test_director_preserves_authored_camera_and_transition() -> None:
    camera = {"keyframes": [{"frame": 0, "zoom": 1.0}, {"frame": 10, "zoom": 1.1}]}
    transition = {"type": "cut", "duration_frames": 0}
    directed = direct_storyboard(
        [{"duration": 1.0, "camera": camera, "transition_out": transition}, {"duration": 1.0}],
        studio_id="whymentary", fps=24, fallback_duration=1.0,
    )
    assert directed[0]["camera"] == camera
    assert directed[0]["transition_out"] == transition
    assert directed[0]["shot_type"] == "medium"
    assert directed[1]["shot_type"]


def test_whymentary_director_keeps_fast_cut_style() -> None:
    directed = direct_storyboard(
        [{"duration": 1.0, "description": "Uma explicação"}, {"duration": 1.0, "description": "Outro exemplo"}],
        studio_id="whymentary", fps=24, fallback_duration=1.0,
    )
    assert directed[0]["transition_out"] == {"type": "cut", "duration_frames": 0}
    assert directed[0]["camera"]["keyframes"][-1]["roll"] == 0


def test_editing_report_flags_dense_narration_and_low_shot_variety() -> None:
    from modules.ai_video_studio.media.editing_director import build_editing_report

    scenes = [
        {"duration": 2.0, "shot_type": "medium", "narration": " ".join(["palavra"] * 12),
         "transition_out": {"type": "crossfade", "duration_frames": 12}},
        {"duration": 2.0, "shot_type": "medium", "narration": "Frase curta."},
        {"duration": 2.0, "shot_type": "medium"},
        {"duration": 2.0, "shot_type": "medium"},
    ]
    report = build_editing_report(scenes, fps=24, fallback_duration=2.0)
    assert report["scene_count"] == 4
    assert report["timeline_duration_seconds"] == 7.5
    assert report["shot_counts"] == {"medium": 4}
    assert report["transition_counts"] == {"crossfade": 1, "cut": 3}
    assert any("narration is dense" in warning for warning in report["warnings"])
    assert any("Low shot variety" in warning for warning in report["warnings"])
    assert report["scenes"][0]["speech_wpm"] == 360.0


def test_editing_report_accepts_balanced_speech_and_multiple_shots() -> None:
    from modules.ai_video_studio.media.editing_director import build_editing_report

    scenes = [
        {"duration": 10.0, "shot_type": "wide", "voiceover_text": " ".join(["palavra"] * 20), "visual_prompt": "Plano geral da cidade."},
        {"duration": 10.0, "shot_type": "close_up", "voiceover_text": " ".join(["palavra"] * 20), "visual_prompt": "Close do documento."},
        {"duration": 10.0, "shot_type": "detail", "voiceover_text": " ".join(["palavra"] * 20), "visual_prompt": "Detalhe da evidência."},
    ]
    report = build_editing_report(scenes, fps=30, fallback_duration=10.0)
    assert report["warnings"] == []
    assert report["timeline_duration_seconds"] == 30.0
    assert [row["pacing"] for row in report["scenes"]] == ["balanced"] * 3


def test_editing_report_rejects_invalid_timing_settings() -> None:
    import pytest
    from modules.ai_video_studio.media.editing_director import build_editing_report

    with pytest.raises(ValueError):
        build_editing_report([], fps=0, fallback_duration=2.0)


def test_director_classifies_narrative_beats_and_suggests_missing_visuals() -> None:
    from modules.ai_video_studio.media.editing_director import (
        classify_narrative_beat, build_editing_report,
    )

    assert classify_narrative_beat({"narration": "A descoberta revelou uma evidência decisiva"}) == "revelation"
    assert classify_narrative_beat({"narration": "Isso provocou uma consequência inesperada"}) == "cause_effect"
    scenes = [
        {"duration": 10.0, "narration": "Primeiro, veja como funciona o processo."},
        {"duration": 10.0, "narration": "Compare o cenário antes e depois."},
    ]
    directed = direct_storyboard(
        scenes, studio_id="historical_documentary", fps=24, fallback_duration=10.0,
    )
    assert directed[0]["narrative_beat"] == "process"
    assert directed[1]["narrative_beat"] == "comparison"
    assert "visual_prompt_suggestion" in directed[0]
    assert "profundidade em camadas" in directed[0]["visual_direction"]
    report = build_editing_report(directed, fps=24, fallback_duration=10.0)
    assert report["scenes"][0]["narrative_beat"] == "process"
    assert report["scenes"][0]["visual_prompt_suggestion"]


def test_custom_director_preserves_user_style_and_generates_camera() -> None:
    directed = direct_storyboard(
        [
            {"duration": 10.0, "narration": "Uma cidade futurista surge no oceano."},
            {"duration": 10.0, "narration": "A câmera acompanha uma nave entre as torres."},
        ],
        studio_id="custom", fps=30, fallback_duration=10.0,
    )
    assert "estilo visual, materiais, paleta e direção de arte definidos pelo usuário" in directed[0]["visual_direction"]
    assert len(directed[0]["camera"]["keyframes"]) == 3
    assert directed[0]["transition_out"] == {"type": "cut", "duration_frames": 0}


def test_felt_clay_director_uses_felt_style_and_camera_preset() -> None:
    directed = direct_storyboard(
        [{"duration": 10.0, "narration": "Uma criatura atravessa a floresta."},
         {"duration": 10.0, "narration": "A criatura encontra uma cabana."}],
        studio_id="felt_clay", fps=30, fallback_duration=10.0,
    )
    assert "feltro e argila" in directed[0]["visual_direction"]
    assert len(directed[0]["camera"]["keyframes"]) == 3
