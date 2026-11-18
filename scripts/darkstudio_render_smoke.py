"""Render and validate a tiny two-scene DARKSTUDIO MP4 proof.

Run: python scripts/darkstudio_render_smoke.py --output /tmp/darkstudio-two-scene-demo.mp4
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

# Running a file from scripts/ puts that directory, not the repository root,
# at sys.path[0]. Add the root so the project package is importable in CI.
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from modules.ai_video_studio.media.render import render_multi_scene_video


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("artifacts/darkstudio-two-scene-demo.mp4"))
    args = parser.parse_args()

    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        raise SystemExit("FFmpeg and ffprobe are required for the DARKSTUDIO MP4 proof")

    scenes = [
        {
            "duration": 1.5,
            "background_type": "gradient",
            "background_colors": ["#101A35", "#263F70", "#E07A35"],
            "noise": 0.015,
            "rects": [{"x": 28, "y": 28, "w": 264, "h": 124, "color": "#18284B"}],
            "circles": [{"x": 160, "y": 82, "radius": 34, "color": "#F4B942", "dx": 0.8}],
            "text": {"content": "DARKSTUDIO AI", "x": 160, "y": 145, "size": 20, "color": "#FFFFFF"},
            "camera": {"zoom": 1.015},
        },
        {
            "duration": 1.5,
            "background_type": "gradient",
            "background_colors": ["#321B3D", "#773B52", "#E7A45B"],
            "noise": 0.01,
            "circles": [
                {"x": 105, "y": 82, "radius": 28, "color": "#F5D6A1", "dx": 1.1},
                {"x": 215, "y": 82, "radius": 28, "color": "#F2C14E", "dx": -1.1},
            ],
            "lines": [{"x1": 50, "y1": 130, "x2": 270, "y2": 130, "color": "#FFFFFF", "width": 3, "grow_frames": 12}],
            "text": {"content": "HISTORIA EM MOVIMENTO", "x": 160, "y": 155, "size": 15, "color": "#FFFFFF"},
            "camera": {"zoom": 1.02, "dx": -0.15},
        },
    ]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    result = render_multi_scene_video(
        scenes,
        args.output,
        fps=12,
        width=320,
        height=180,
        require_mp4=True,
    )
    if not args.output.is_file() or args.output.stat().st_size <= 0:
        raise SystemExit("Renderer did not create a non-empty MP4")

    probe = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=codec_name,width,height,nb_frames",
            "-show_entries", "format=duration,size", "-of", "json", str(args.output),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    metadata = json.loads(probe.stdout)
    stream = metadata["streams"][0]
    duration = float(metadata["format"]["duration"])
    if stream["codec_name"] != "h264" or (stream["width"], stream["height"]) != (320, 180):
        raise SystemExit(f"Unexpected MP4 stream metadata: {stream}")
    if abs(duration - 3.0) > 0.15:
        raise SystemExit(f"Expected a 3-second two-scene video, got {duration:.3f}s")

    print(json.dumps({"render": result, "probe": metadata}, indent=2))


if __name__ == "__main__":
    main()
