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
        {"duration": 10.0, "shot_type": "wide", "voiceover_text": " ".join(["palavra"] * 20)},
        {"duration": 10.0, "shot_type": "close_up", "voiceover_text": " ".join(["palavra"] * 20)},
        {"duration": 10.0, "shot_type": "detail", "voiceover_text": " ".join(["palavra"] * 20)},
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
