"""Deterministic seed derivation for per-scene image generation."""
from modules.ai_video_studio.ai_video_generator.text_to_video.text_to_video_engine import (
    derive_scene_image_seed,
)


def test_scene_seed_is_repeatable_for_same_job_and_scene():
    scene = {"storyboard_scene_id": "scene-001-abc123"}

    first = derive_scene_image_seed("job-123", scene, 0)
    second = derive_scene_image_seed("job-123", scene, 0)

    assert first == second
    assert 0 <= first <= 0x7FFFFFFF


def test_scene_seeds_differ_between_scenes_in_one_job():
    first = derive_scene_image_seed(
        "job-123", {"storyboard_scene_id": "scene-001-a"}, 0
    )
    second = derive_scene_image_seed(
        "job-123", {"storyboard_scene_id": "scene-002-b"}, 1
    )

    assert first != second


def test_explicit_base_seed_reproduces_scene_across_jobs():
    scene = {"storyboard_scene_id": "scene-001-abc123"}

    first = derive_scene_image_seed("job-one", scene, 0, base_seed=9876)
    second = derive_scene_image_seed("job-two", scene, 0, base_seed=9876)

    assert first == second


def test_changing_base_seed_changes_scene_seed():
    scene = {"storyboard_scene_id": "scene-001-abc123"}

    first = derive_scene_image_seed("job-one", scene, 0, base_seed=9876)
    second = derive_scene_image_seed("job-one", scene, 0, base_seed=9877)

    assert first != second
