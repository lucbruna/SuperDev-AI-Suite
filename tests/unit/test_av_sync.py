from __future__ import annotations

import pytest

from modules.ai_video_studio.media.av_sync import analyze_av_sync


def test_av_sync_accepts_frame_aligned_scene_narration():
    video = [
        {"scene_index": 0, "start_frame": 0, "end_frame": 240},
        {"scene_index": 1, "start_frame": 240, "end_frame": 480},
    ]
    narration = [
        {"start_frame": 0, "end_frame": 240},
        {"start_frame": 240, "end_frame": 480},
    ]
    report = analyze_av_sync(video, narration, fps=24)
    assert report["status"] == "passed"
    assert report["export_blocked"] is False
    assert all(item["aligned"] for item in report["scene_comparisons"])


def test_av_sync_warns_when_narration_starts_late():
    video = [{"scene_index": 0, "start_frame": 0, "end_frame": 240}]
    narration = [{"start_frame": 12, "end_frame": 240}]
    report = analyze_av_sync(video, narration, fps=24)
    assert report["status"] == "needs_review"
    assert any(item["code"] == "scene_narration_timing_mismatch" for item in report["warnings"])


def test_av_sync_blocks_narration_outside_video_duration():
    video = [{"scene_index": 0, "start_frame": 0, "end_frame": 100}]
    narration = [{"start_frame": 0, "end_frame": 120}]
    report = analyze_av_sync(video, narration, fps=24)
    assert report["status"] == "blocked"
    assert report["export_blocked"] is True
    assert any(item["code"] == "narration_outside_video" for item in report["warnings"])


def test_av_sync_warns_on_long_narration_gap():
    video = [{"start_frame": 0, "end_frame": 480}]
    narration = [
        {"start_frame": 0, "end_frame": 100},
        {"start_frame": 130, "end_frame": 240},
    ]
    report = analyze_av_sync(video, narration, fps=24)
    assert any(item["code"] == "narration_gap" for item in report["warnings"])
    assert report["status"] == "needs_review"


@pytest.mark.parametrize("fps", [0, -1])
def test_av_sync_rejects_invalid_fps(fps):
    with pytest.raises(ValueError, match="fps"):
        analyze_av_sync([{"start_frame": 0, "end_frame": 10}], [], fps=fps)
