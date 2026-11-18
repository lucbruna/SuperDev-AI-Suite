from __future__ import annotations

import pytest

from modules.ai_video_studio.media.visual_intelligence import analyze_visual_quality


def test_historical_visual_report_scores_camera_and_shot_variety():
    scenes = [
        {"duration": 4, "shot_type": "wide", "camera": {"keyframes": [
            {"frame": 0, "zoom": 1.0, "dx": 0}, {"frame": 95, "zoom": 1.08, "dx": 12},
        ]}, "rects": [{}, {}, {}], "background_colors": ["#111111"]},
        {"duration": 4, "shot_type": "close_up", "camera": {"keyframes": [
            {"frame": 0, "zoom": 1.02, "dx": 0}, {"frame": 95, "zoom": 1.12, "dx": -10},
        ]}, "circles": [{}, {}, {}], "background_colors": ["#222222"]},
        {"duration": 4, "shot_type": "detail", "camera": {"keyframes": [
            {"frame": 0, "zoom": 1.05}, {"frame": 95, "zoom": 1.15},
        ]}, "lines": [{}, {}, {}], "background_colors": ["#333333"]},
    ]
    report = analyze_visual_quality(scenes, studio_id="historical_documentary", fps=24)
    assert report["scene_count"] == 3
    assert report["moving_camera_scenes"] == 3
    assert report["unique_shot_types"] == 3
    assert report["transition_counts"] == {"cut": 3}
    assert report["components"]["motion"] == 100
    assert report["score"] > 0
    assert report["analysis_method"] == "scene_descriptor_metadata"


def test_whymentary_counts_primitive_motion_and_text_clarity():
    scenes = [
        {"duration": 3, "shot_type": "wide", "rects": [{"motion_dx": 20, "motion_frames": 20}],
         "text": {"content": "EXPLICAÇÃO"}},
        {"duration": 3, "shot_type": "medium", "circles": [{"dx": 0.5}],
         "text": {"content": "EXEMPLO"}},
    ]
    report = analyze_visual_quality(scenes, studio_id="whymentary", fps=30)
    assert report["animated_primitives"] == 2
    assert report["components"]["clarity"] == 100
    assert report["scene_count"] == 2


def test_visual_intelligence_flags_static_and_repeated_scenes():
    scene = {"duration": 13, "shot_type": "medium", "rects": [{"x": 1, "y": 1}]}
    report = analyze_visual_quality([scene, dict(scene)], studio_id="whymentary", fps=24)
    codes = {item["code"] for item in report["warnings"]}
    assert "static_scene_metadata" in codes
    assert "long_unchanged_shot_risk" in codes
    assert "consecutive_visual_repetition" in codes


def test_visual_intelligence_reports_character_identity_changes():
    scenes = [
        {"duration": 2, "_darkstudio_characters": ["leo"]},
        {"duration": 2, "_darkstudio_characters": ["mia"]},
    ]
    report = analyze_visual_quality(scenes, studio_id="whymentary", fps=24)
    assert report["character_continuity_changes"] == 1
    assert any(item["code"] == "character_continuity_change" for item in report["warnings"])


@pytest.mark.parametrize("studio_id", ["unknown", ""])
def test_visual_intelligence_rejects_unknown_studio(studio_id):
    with pytest.raises(ValueError, match="Unknown studio"):
        analyze_visual_quality([{"duration": 1}], studio_id=studio_id, fps=24)


def test_visual_intelligence_rejects_invalid_fps_and_empty_scenes():
    with pytest.raises(ValueError, match="fps"):
        analyze_visual_quality([{"duration": 1}], studio_id="whymentary", fps=0)
    with pytest.raises(ValueError, match="empty"):
        analyze_visual_quality([], studio_id="whymentary", fps=24)
