"""Tests for DARKSTUDIO's reusable character primitive library."""
from __future__ import annotations

import numpy as np
import pytest

from modules.ai_video_studio.media.canvas import SceneCanvas
from modules.ai_video_studio.media.characters import (
    add_character,
    add_character_motion,
    character_primitives,
)


def test_character_identity_and_geometry_are_deterministic() -> None:
    a = character_primitives("whymentary_host", x=160, y=300)
    b = character_primitives("whymentary_host", x=160, y=300)
    assert a == b
    assert len(a["rects"]) == 2
    assert len(a["circles"]) >= 5
    assert len(a["lines"]) >= 6


def test_pose_and_expression_change_appearance_data() -> None:
    neutral = character_primitives("whymentary_host", x=160, y=300)
    expressive = character_primitives(
        "whymentary_host", x=160, y=300, pose="point", expression="surprised"
    )
    assert neutral["lines"] != expressive["lines"]
    assert neutral["circles"] != expressive["circles"]


def test_scale_scales_character_proportionally() -> None:
    small = character_primitives("historical_narrator", x=100, y=300, scale=0.5)
    large = character_primitives("historical_narrator", x=100, y=300, scale=2)
    assert large["rects"][0]["w"] == pytest.approx(small["rects"][0]["w"] * 4)


def test_invalid_character_pose_expression_and_scale_fail_fast() -> None:
    with pytest.raises(ValueError, match="Unknown character"):
        character_primitives("not_registered", x=0, y=0)
    with pytest.raises(ValueError, match="Unknown pose"):
        character_primitives("whymentary_host", x=0, y=0, pose="running")
    with pytest.raises(ValueError, match="Unknown expression"):
        character_primitives("whymentary_host", x=0, y=0, expression="angry")
    with pytest.raises(ValueError, match="scale"):
        character_primitives("whymentary_host", x=0, y=0, scale=0)


def test_add_character_integrates_with_scene_canvas_without_mutation() -> None:
    original = {
        "background_type": "solid",
        "background_colors": ["#FFFFFF"],
        "rects": [{"x": 5, "y": 5, "w": 10, "h": 10, "color": "#FF0000"}],
    }
    scene = add_character(
        original, "whymentary_host", x=160, y=190, pose="explain", expression="happy"
    )
    assert len(scene["rects"]) == 3
    assert len(scene["circles"]) >= 5
    assert len(original["rects"]) == 1
    frame = SceneCanvas(width=320, height=240).render_scene(scene, 0)
    assert frame.shape == (240, 320, 3)
    assert frame.dtype == np.uint8
    assert np.unique(frame.reshape(-1, 3), axis=0).shape[0] > 4



def test_character_motion_is_eased_finite_and_rendered_by_canvas() -> None:
    scene = add_character_motion(
        {"background_type": "solid", "background_colors": ["#FFFFFF"]},
        "whymentary_host",
        from_x=70,
        from_y=205,
        to_x=230,
        to_y=205,
        duration_frames=20,
        start_frame=5,
    )
    head = scene["circles"][0]
    assert head["motion_start_frame"] == 5
    assert head["motion_frames"] == 20
    canvas = SceneCanvas(width=320, height=240)
    before = canvas.render_scene(scene, 0)
    middle = canvas.render_scene(scene, 15)
    after = canvas.render_scene(scene, 30)
    assert not np.array_equal(before, middle)
    assert not np.array_equal(middle, after)
    assert np.array_equal(after, canvas.render_scene(scene, 60))


def test_character_motion_rejects_invalid_timing() -> None:
    base = {"rects": []}
    with pytest.raises(ValueError, match="duration_frames"):
        add_character_motion(
            base, "whymentary_host", from_x=0, from_y=0,
            to_x=10, to_y=10, duration_frames=0,
        )
    with pytest.raises(ValueError, match="start_frame"):
        add_character_motion(
            base, "whymentary_host", from_x=0, from_y=0,
            to_x=10, to_y=10, duration_frames=10, start_frame=-1,
        )



def test_narration_cues_map_to_absolute_video_frames() -> None:
    from modules.ai_video_studio.media.characters import build_character_cue_timeline

    events = build_character_cue_timeline(
        {"start": 4.0, "end": 8.0},
        [
            {"offset_seconds": 2.0, "pose": "point", "expression": "surprised"},
            {"offset_seconds": 0.5, "pose": "explain", "expression": "happy"},
        ],
        fps=30,
    )
    assert events == [
        {"frame": 135, "time_seconds": 4.5, "pose": "explain", "expression": "happy"},
        {"frame": 180, "time_seconds": 6.0, "pose": "point", "expression": "surprised"},
    ]


def test_narration_cue_timeline_rejects_out_of_range_and_invalid_cues() -> None:
    from modules.ai_video_studio.media.characters import build_character_cue_timeline

    with pytest.raises(ValueError, match="within narration clip"):
        build_character_cue_timeline(
            {"start": 2.0, "end": 4.0}, [{"offset_seconds": 3.0}]
        )
    with pytest.raises(ValueError, match="Unknown pose"):
        build_character_cue_timeline(
            {"start": 2.0, "end": 4.0}, [{"offset_seconds": 1.0, "pose": "dance"}]
        )



def test_character_performance_switches_pose_and_expression_by_frame() -> None:
    from modules.ai_video_studio.media.characters import add_character_performance
    from modules.ai_video_studio.media.canvas import SceneCanvas
    import numpy as np

    scene = add_character_performance(
        {"background_type": "solid", "background_colors": ["#FFFFFF"], "noise": 0},
        "historical_narrator",
        narration_clip={"start": 0, "end": 3},
        cues=[
            {"offset_seconds": 1, "pose": "point", "expression": "surprised"},
            {"offset_seconds": 2, "pose": "explain", "expression": "happy"},
        ],
        x=80, y=175, fps=10, scale=0.5,
    )
    canvas = SceneCanvas(width=160, height=190, fps=10)
    neutral = canvas.render_scene(scene, 5)
    pointing = canvas.render_scene(scene, 15)
    explaining = canvas.render_scene(scene, 25)
    assert not np.array_equal(neutral, pointing)
    assert not np.array_equal(pointing, explaining)


def test_mia_and_leo_keep_distinct_visual_signatures() -> None:
    leo = character_primitives("leo", x=100, y=200)
    mia = character_primitives("mia", x=100, y=200)
    assert leo["rects"][1]["color"] == "#2563EB"
    assert mia["rects"][1]["color"] == "#DC2626"
    assert len(mia["rects"]) == 3
    assert len(mia["circles"]) == len(leo["circles"]) + 1
