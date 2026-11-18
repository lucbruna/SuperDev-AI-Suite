from __future__ import annotations

import shutil
import subprocess

import numpy as np
import pytest
from PIL import Image

from modules.ai_video_studio.media.mp4_visual_analysis import (
    analyze_frame_sequence,
    analyze_mp4_visuals,
)


def test_frame_sequence_finds_identical_frames_and_static_run():
    black = Image.fromarray(np.zeros((90, 160, 3), dtype=np.uint8), "RGB")
    white = Image.fromarray(np.full((90, 160, 3), 255, dtype=np.uint8), "RGB")
    report = analyze_frame_sequence(
        [black, black.copy(), black.copy(), white],
        sample_times=[0.0, 1.0, 2.0, 3.0],
    )
    assert report["sample_count"] == 4
    assert report["duplicate_pair_count"] == 2
    assert report["low_change_pair_count"] == 2
    assert report["static_runs"] == [{
        "start_seconds": 0.0, "end_seconds": 2.0, "comparison_count": 2,
    }]
    assert report["warnings"][0]["code"] == "near_duplicate_sampled_frames"
    black.close()
    white.close()


def test_frame_sequence_maps_sampled_changes_to_timeline_scenes():
    first = Image.fromarray(np.zeros((90, 160, 3), dtype=np.uint8), "RGB")
    second = Image.fromarray(np.full((90, 160, 3), 180, dtype=np.uint8), "RGB")
    timeline = {"tracks": [{
        "type": "video",
        "clips": [
            {"scene_index": 0, "start_seconds": 0, "end_seconds": 1},
            {"scene_index": 1, "start_seconds": 1, "end_seconds": 2},
        ],
    }]}
    report = analyze_frame_sequence(
        [first, second], sample_times=[0.5, 1.5], timeline=timeline,
    )
    assert [row["scene_index"] for row in report["scene_summaries"]] == [0, 1]
    assert report["scene_summaries"][1]["sampled_comparisons"] == 1
    first.close()
    second.close()


def test_frame_sequence_rejects_mismatched_timestamps():
    frame = Image.new("RGB", (32, 32), "black")
    with pytest.raises(ValueError, match="sample_times"):
        analyze_frame_sequence([frame, frame.copy()], sample_times=[0.0])
    frame.close()


@pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"), reason="FFmpeg/ffprobe required")
def test_analyze_mp4_visuals_extracts_frames_from_real_encoded_file(tmp_path):
    video = tmp_path / "visual-sample.mp4"
    subprocess.run(
        [shutil.which("ffmpeg"), "-hide_banner", "-loglevel", "error",
         "-f", "lavfi", "-i", "color=c=blue:s=160x90:d=1:r=6",
         "-pix_fmt", "yuv420p", "-c:v", "libx264", "-y", str(video)],
        capture_output=True, check=True, timeout=30,
    )
    report = analyze_mp4_visuals(video, max_frames=6)
    assert report["sample_count"] >= 3
    assert report["video_duration_seconds"] > 0
    assert report["analysis_method"] == "ffmpeg_sampled_frames_pillow_numpy"
