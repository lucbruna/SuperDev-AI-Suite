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
import wave

import numpy as np
from pathlib import Path
from typing import Any

from modules.ai_video_studio.ai_video_generator.text_to_video import text_to_video_engine as engine_module
from modules.ai_video_studio import ai_voice_studio


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
        "stream=codec_type,codec_name,width,height,duration",
        "-show_entries", "format=duration,size", "-of", "json", str(path),
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=30)
    return json.loads(result.stdout)


class _DeterministicVoiceEngine:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def synthesize_async(self, text: str, **kwargs: Any) -> dict[str, Any]:
        # A real WAV file exercises the production alignment, mix and mux path.
        # This is a pipeline integration proof, not a Portuguese voice-quality test.
        output = self.output_dir / f"darkstudio-voice-{abs(hash(text))}.wav"
        sample_rate = 22050
        duration = 1.25
        samples = (0.12 * np.sin(2 * np.pi * 440 * np.arange(int(sample_rate * duration)) / sample_rate))
        pcm = (samples * 32767).astype(np.int16)
        with wave.open(str(output), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            wav.writeframes(pcm.tobytes())
        return {"output_path": str(output), "engine": "deterministic-smoke-tone", "duration": duration}


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

        # Keep every generated asset inside this smoke test's temporary tree.
        # scene_narration imports get_subsystem_dir independently from the engine,
        # so patch both module references to avoid leaking files into the checkout.
        from modules.ai_video_studio.media import scene_narration

        engine_module.get_scene_planner = lambda: _DeterministicPlanner()
        engine_module.get_subsystem_dir = subsystem_dir
        scene_narration.get_subsystem_dir = subsystem_dir
        voice_dir = subsystem_dir("voice")
        ai_voice_studio.get_voice_engine = lambda: _DeterministicVoiceEngine(voice_dir)

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
                    "voiceover": True,
                    "voiceover_mode": "per_scene",
                    "voice_language": "pt-BR",
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
        subtitle_text = subtitle.read_text(encoding="utf-8-sig")
        if "-->" not in subtitle_text:
            raise SystemExit("Generated SRT does not contain valid cue timing separators")

        master_probe = _probe(master)
        master_video = next(s for s in master_probe["streams"] if s["codec_type"] == "video")
        master_duration = float(master_probe["format"]["duration"])
        if master_video["codec_name"] != "h264" or (master_video["width"], master_video["height"]) != (320, 180):
            raise SystemExit(f"Unexpected master MP4 stream: {master_video}")
        if abs(master_duration - 20.0) > 0.2:
            raise SystemExit(f"Expected a 20-second master MP4, got {master_duration:.3f}s")
        master_audio = [stream for stream in master_probe["streams"] if stream["codec_type"] == "audio"]
        if not master_audio:
            raise SystemExit("Narration was requested but the master MP4 has no audio stream")
        master_audio_duration = max(
            (float(stream.get("duration") or 0.0) for stream in master_audio),
            default=0.0,
        )
        if not 19.5 <= master_audio_duration <= 20.5:
            raise SystemExit(
                f"Expected master narration audio to span ~20 seconds, got {master_audio_duration:.3f}s"
            )
        voiceover = result.get("voiceover") or {}
        if not voiceover.get("muxed") or voiceover.get("narration_style") != "per_scene":
            raise SystemExit(f"Per-scene narration did not complete: {voiceover}")
        narration_assets = voiceover.get("clips") or []
        if len(narration_assets) != 2 or any(not clip.get("audio_path") for clip in narration_assets):
            raise SystemExit("Expected one synthesized audio asset for each scene")
        for index, narration in enumerate(narration_assets):
            audio_path = Path(narration["audio_path"])
            if not audio_path.is_file() or audio_path.stat().st_size == 0:
                raise SystemExit(f"Scene {index + 1} narration source is missing or empty: {audio_path}")
        if any(item.get("audio_status") != "per_scene_narration_muxed" for item in result["scene_clips"]):
            raise SystemExit(f"Per-scene narration was not muxed into every VidGrid clip: {result['scene_clips']}")

        clip_reports = []
        for index, clip in enumerate(clips):
            metadata = _probe(clip)
            stream = next(s for s in metadata["streams"] if s["codec_type"] == "video")
            duration = float(metadata["format"]["duration"])
            if abs(duration - 10.0) > 0.2 or stream["codec_name"] != "h264":
                raise SystemExit(f"VidGrid clip {index + 1} failed validation: {metadata}")
            clip_audio = [item for item in metadata["streams"] if item["codec_type"] == "audio"]
            if not clip_audio:
                raise SystemExit(f"VidGrid clip {index + 1} is missing its scene narration audio")
            audio_duration = max(
                (float(item.get("duration") or 0.0) for item in clip_audio),
                default=0.0,
            )
            if not 9.5 <= audio_duration <= 10.5:
                raise SystemExit(
                    f"VidGrid clip {index + 1} narration does not span its 10-second scene: "
                    f"{audio_duration:.3f}s"
                )
            clip_reports.append({
                "path": clip.name,
                "duration": duration,
                "audio_duration": audio_duration,
                "bytes": metadata["format"]["size"],
                "audio": True,
            })

        shutil.copy2(master, output)
        print(json.dumps({
            "status": "passed",
            "planner": result["ai_planner"],
            "master_mp4": {"path": str(output), "duration": master_duration, "bytes": output.stat().st_size},
            "vidgrid_clips": clip_reports,
            "subtitles": {"cue_count": result["subtitles"]["cue_count"], "format": "srt"},
            "narration": {"style": voiceover["narration_style"], "clips": len(voiceover["clips"]), "master_audio_duration": master_audio_duration, "audio_stream": True},
        }, indent=2))


if __name__ == "__main__":
    main()
