"""Exercise the real DARKSTUDIO prompt-to-video pipeline without external AI services.

Renders a deterministic two-scene, 10-second-per-scene VidGrid job using the
production TextToVideoEngine and FFmpeg. Validates the master MP4, both scene
clips, and the generated SRT sidecar.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from modules.ai_video_studio.ai_video_generator.text_to_video import text_to_video_engine as engine_module


class _DeterministicPlanner:
    def plan(self, prompt: str, *, num_scenes: int, duration: float, timeout: float) -> dict[str, Any]:
        if num_scenes != 2 or duration != 20.0:
            raise AssertionError(f"Unexpected smoke-test plan request: {num_scenes=} {duration=}")
        return {
            "provider": "deterministic-smoke",
            "ai_generated": False,
            "scenes": [
                {
                    "title": "A cidade desperta",
                    "description": "Uma cidade futurista surge ao amanhecer.",
                    "visual_prompt": "Wide cinematic view of a futuristic city at sunrise",
                    "voiceover_text": "Ao amanhecer, uma cidade futurista desperta.",
                    "duration": 10.0,
                    "background_type": "gradient",
                    "background_colors": ["#101A35", "#263F70", "#E07A35"],
                    "camera": {"zoom": 1.02, "dx": 0.1},
                },
                {
                    "title": "A energia se transforma",
                    "description": "Painéis solares capturam a luz e alimentam a cidade.",
                    "visual_prompt": "Tracking view of solar panels powering a futuristic city",
                    "voiceover_text": "A energia do sol transforma o futuro da cidade.",
                    "duration": 10.0,
                    "background_type": "gradient",
                    "background_colors": ["#321B3D", "#773B52", "#E7A45B"],
                    "camera": {"zoom": 1.03, "dx": -0.1},
                },
            ],
        }


def _probe(path: Path) -> dict[str, Any]:
    command = [
        "ffprobe", "-v", "error", "-show_entries",
        "stream=codec_type,codec_name,width,height",
        "-show_entries", "format=duration,size", "-of", "json", str(path),
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=30)
    return json.loads(result.stdout)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise SystemExit("FFmpeg and ffprobe are required for the DARKSTUDIO pipeline proof")

    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="darkstudio-pipeline-smoke-") as temp_dir:
        work = Path(temp_dir)

        def subsystem_dir(name: str) -> Path:
            directory = work / name
            directory.mkdir(parents=True, exist_ok=True)
            return directory

        engine_module.get_scene_planner = lambda: _DeterministicPlanner()
        engine_module.get_subsystem_dir = subsystem_dir

        result = asyncio.run(engine_module.TextToVideoEngine().generate_async(
            {
                "id": "ci-darkstudio-pipeline-smoke",
                "prompt": "Um documentário cinematográfico sobre uma cidade sustentável.",
                "params": {
                    "duration": 20.0,
                    "num_scenes": 2,
                    "fps": 12,
                    "width": 320,
                    "height": 180,
                    "studio_id": "custom",
                    "style": "cinematic documentary, rich environmental detail",
                    "scene_image_mode": "procedural",
                    "vidgrid_compatible": True,
                    "generate_subtitles": True,
                    "voiceover": False,
                },
            }
        ))

        master = Path(result["output_path"])
        clips = [Path(item["output_path"]) for item in result["scene_clips"]]
        subtitle = Path(result["subtitles"]["file_path"])
        if not master.is_file() or master.stat().st_size == 0:
            raise SystemExit("TextToVideoEngine did not produce a non-empty master MP4")
        if len(clips) != 2 or any(not clip.is_file() or clip.stat().st_size == 0 for clip in clips):
            raise SystemExit("TextToVideoEngine did not produce both VidGrid scene MP4s")
        if not subtitle.is_file() or subtitle.stat().st_size == 0 or result["subtitles"]["cue_count"] < 2:
            raise SystemExit("TextToVideoEngine did not produce the expected SRT subtitle sidecar")

        master_probe = _probe(master)
        master_video = next(s for s in master_probe["streams"] if s["codec_type"] == "video")
        master_duration = float(master_probe["format"]["duration"])
        if master_video["codec_name"] != "h264" or (master_video["width"], master_video["height"]) != (320, 180):
            raise SystemExit(f"Unexpected master MP4 stream: {master_video}")
        if abs(master_duration - 20.0) > 0.2:
            raise SystemExit(f"Expected a 20-second master MP4, got {master_duration:.3f}s")

        clip_reports = []
        for index, clip in enumerate(clips):
            metadata = _probe(clip)
            stream = next(s for s in metadata["streams"] if s["codec_type"] == "video")
            duration = float(metadata["format"]["duration"])
            if abs(duration - 10.0) > 0.2 or stream["codec_name"] != "h264":
                raise SystemExit(f"VidGrid clip {index + 1} failed validation: {metadata}")
            clip_reports.append({"path": clip.name, "duration": duration, "bytes": metadata["format"]["size"]})

        shutil.copy2(master, output)
        print(json.dumps({
            "status": "passed",
            "planner": result["ai_planner"],
            "master_mp4": {"path": str(output), "duration": master_duration, "bytes": output.stat().st_size},
            "vidgrid_clips": clip_reports,
            "subtitles": {"cue_count": result["subtitles"]["cue_count"], "format": "srt"},
        }, indent=2))


if __name__ == "__main__":
    main()
