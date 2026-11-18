"""High-level media helpers — render scenes to real files."""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Callable

import numpy as np

from modules.ai_video_studio.media.canvas import SceneCanvas
from modules.ai_video_studio.media.characters import add_character_performance
from modules.ai_video_studio.media.studio_profiles import apply_studio_profile
from modules.ai_video_studio.media.video import frames_to_video, stream_frames_to_video


def _prepare_scene(
    scene: dict[str, Any], studio_id: str | None, *, fps: int = 30
) -> dict[str, Any]:
    """Resolve declarative character performances before canvas rendering.

    Scene metadata uses character_performances entries with character_id,
    narration_clip, cues, x and y. Cue timestamps are local to the scene
    timeline, matching the frame index passed by the scene renderer.
    """
    prepared = dict(scene)
    performances = prepared.pop("character_performances", [])
    if not isinstance(performances, list):
        raise ValueError("character_performances must be a list")
    for performance in performances:
        if not isinstance(performance, dict):
            raise ValueError("each character performance must be an object")
        required = {"character_id", "narration_clip", "cues", "x", "y"}
        missing = required.difference(performance)
        if missing:
            raise ValueError(
                "character performance missing fields: " + ", ".join(sorted(missing))
            )
        options = {
            key: performance[key]
            for key in ("scale", "initial_pose", "initial_expression")
            if key in performance
        }
        prepared = add_character_performance(
            prepared,
            str(performance["character_id"]),
            narration_clip=performance["narration_clip"],
            cues=performance["cues"],
            x=float(performance["x"]),
            y=float(performance["y"]),
            fps=fps,
            **options,
        )
    return apply_studio_profile(studio_id, prepared) if studio_id else prepared


def render_still(
    scene: dict[str, Any],
    output_path: str | Path,
    *,
    width: int = 1280,
    height: int = 720,
    seed: int = 42,
    studio_id: str | None = None,
) -> Path:
    """Render one PNG, optionally enforcing a studio visual profile."""
    canvas = SceneCanvas(width=width, height=height, seed=seed)
    frame = canvas.render_scene(_prepare_scene(scene, studio_id, fps=30), 0)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    from PIL import Image

    Image.fromarray(frame).save(out, format="PNG")
    return out


def render_scene_video(
    scene: dict[str, Any],
    output_path: str | Path,
    *,
    duration: float = 5.0,
    fps: int = 24,
    width: int = 1280,
    height: int = 720,
    seed: int = 42,
    require_mp4: bool = False,
    studio_id: str | None = None,
) -> dict[str, Any]:
    """Render one scene, optionally enforcing a studio visual profile."""
    scene = _prepare_scene(scene, studio_id, fps=fps)
    canvas = SceneCanvas(width=width, height=height, fps=fps, seed=seed)
    total = max(1, int(duration * fps))
    frames: list[np.ndarray] = []
    for i in range(total):
        frames.append(canvas.render_scene(scene, i))
    return frames_to_video(frames, output_path, fps=fps, require_mp4=require_mp4)


def render_multi_scene_video(
    scenes: list[dict[str, Any]],
    output_path: str | Path,
    *,
    fps: int = 24,
    width: int = 1280,
    height: int = 720,
    seed: int = 42,
    on_frame: Callable[[int, int], None] | None = None,
    require_mp4: bool = False,
    studio_id: str | None = None,
) -> dict[str, Any]:
    """Render a storyboard into one continuous video.

    Frames are streamed to FFmpeg so long videos do not accumulate in memory.
    When studio_id is provided, its visual contract is applied to every scene.
    Scene-specific content and geometry are preserved.
    """
    canvas = SceneCanvas(width=width, height=height, fps=fps, seed=seed)
    if not scenes:
        raise ValueError("No scenes to render")
    prepared_scenes = [_prepare_scene(scene, studio_id, fps=fps) for scene in scenes]

    from modules.ai_video_studio.media.transitions import (
        blend_frames, fade_from_black, fade_to_black, transition_spec,
    )

    scene_frames = [max(1, int(float(scene.get("duration", 3.0)) * fps)) for scene in prepared_scenes]
    transitions = [transition_spec(scene) for scene in prepared_scenes]
    effective_transitions: list[dict[str, Any]] = []
    for index, spec in enumerate(transitions):
        frames = spec["duration_frames"]
        if spec["type"] == "crossfade":
            if index == len(prepared_scenes) - 1:
                raise ValueError("The final scene cannot have an outgoing crossfade")
            frames = min(frames, scene_frames[index] // 2, scene_frames[index + 1] // 2)
            if frames < 2:
                raise ValueError("Scenes are too short for the requested crossfade")
        elif spec["type"] == "fade_through_black":
            frames = min(frames, scene_frames[index] // 2)
            if index < len(prepared_scenes) - 1:
                frames = min(frames, scene_frames[index + 1] // 2)
            if frames < 2:
                raise ValueError("Scenes are too short for the requested fade-through-black")
        effective_transitions.append({"type": spec["type"], "duration_frames": frames})

    total_frames = sum(scene_frames) - sum(
        item["duration_frames"] for item in effective_transitions if item["type"] == "crossfade"
    )
    if total_frames <= 0:
        raise ValueError("No scenes to render")

    def _frame_iter():
        rendered = 0
        for scene_index, scene in enumerate(prepared_scenes):
            total = scene_frames[scene_index]
            transition = effective_transitions[scene_index]
            kind = transition["type"]
            transition_frames = transition["duration_frames"]
            next_scene = prepared_scenes[scene_index + 1] if scene_index + 1 < len(prepared_scenes) else None
            next_total = scene_frames[scene_index + 1] if next_scene is not None else 0
            crossfade_head = (
                [canvas.render_scene(next_scene, j) for j in range(transition_frames)]
                if kind == "crossfade" and next_scene is not None else []
            )
            skip_head = transition_frames if kind == "crossfade" else 0
            for frame_index in range(total):
                frame = canvas.render_scene(scene, frame_index)
                if kind == "crossfade" and frame_index >= total - transition_frames:
                    offset = frame_index - (total - transition_frames)
                    alpha = (offset + 1) / transition_frames
                    frame = blend_frames(frame, crossfade_head[offset], alpha)
                elif kind == "fade_through_black" and frame_index >= total - transition_frames:
                    offset = frame_index - (total - transition_frames)
                    progress = (offset + 1) / transition_frames
                    frame = fade_to_black(frame, progress)
                elif kind == "fade_through_black" and frame_index < transition_frames and scene_index > 0:
                    progress = frame_index / (transition_frames - 1)
                    frame = fade_from_black(frame, progress)
                if frame_index < skip_head:
                    continue
                yield frame
                rendered += 1
                if on_frame is not None:
                    on_frame(rendered, total_frames)

    return stream_frames_to_video(
        _frame_iter(),
        output_path,
        fps=fps,
        total_frames=total_frames,
        require_mp4=require_mp4,
    )


def render_sim_frames(
    make_frame: Callable[[int], np.ndarray],
    output_path: str | Path,
    *,
    frames: int = 60,
    fps: int = 24,
    require_mp4: bool = False,
) -> dict[str, Any]:
    """Render video from an arbitrary frame callback."""
    rendered: list[np.ndarray] = []
    for i in range(frames):
        frame = make_frame(i)
        if frame is None:
            continue
        rendered.append(np.asarray(frame, dtype=np.uint8))
    if not rendered:
        raise ValueError("Frame callback produced no frames")
    return frames_to_video(rendered, output_path, fps=fps, require_mp4=require_mp4)


def timeit(fn: Callable[[], Any]) -> tuple[Any, float]:
    """Run a callable and return (result, elapsed_seconds)."""
    started = time.time()
    result = fn()
    return result, round(time.time() - started, 3)



def render_single_scene_clip(
    scene: dict[str, Any],
    output_path: str | Path,
    *,
    duration: float = 10.0,
    fps: int = 24,
    width: int = 1280,
    height: int = 720,
    require_mp4: bool = True,
    studio_id: str | None = None,
) -> dict[str, Any]:
    """Stream one scene as a standalone clip without buffering all frames in RAM."""
    clip_scene = dict(scene)
    clip_scene["duration"] = duration
    # An isolated clip has no outgoing transition; the assembled master keeps
    # the authored transition separately.
    clip_scene["transition_out"] = {"type": "cut", "duration_frames": 0}
    return render_multi_scene_video(
        [clip_scene],
        output_path,
        fps=fps,
        width=width,
        height=height,
        require_mp4=require_mp4,
        studio_id=studio_id,
    )


def render_mixed_scene_video(
    scenes: list[dict[str, Any]],
    output_path: str | Path,
    *,
    generated_clips: dict[int, str],
    fps: int = 24,
    width: int = 1280,
    height: int = 720,
    seed: int = 42,
    require_mp4: bool = True,
    studio_id: str | None = None,
) -> dict[str, Any]:
    """Render mixed AI/procedural scenes with frame-accurate FFmpeg transitions.

    Crossfades overlap by their configured frame count. Fade-through-black
    keeps the scene durations unchanged. Cuts are concatenated without
    dropping frames, so downstream audio and subtitle offsets remain aligned.
    """
    import shutil
    import subprocess
    import tempfile

    from modules.ai_video_studio.media.transitions import transition_spec

    if not scenes:
        raise ValueError("No scenes to render")
    if not isinstance(fps, int) or fps < 1 or width < 2 or height < 2:
        raise ValueError("Invalid mixed render dimensions or frame rate")
    if width % 2 or height % 2:
        raise ValueError("H.264 mixed render requires even width and height")
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("FFmpeg is required for mixed-scene rendering")

    scene_frames = [max(1, int(round(float(scene.get("duration", 3.0)) * fps))) for scene in scenes]
    specs = [transition_spec(scene) for scene in scenes]
    effective: list[dict[str, Any]] = []
    for index, spec in enumerate(specs):
        frames = spec["duration_frames"]
        if spec["type"] == "crossfade":
            if index == len(scenes) - 1:
                raise ValueError("The final scene cannot have an outgoing crossfade")
            frames = min(frames, scene_frames[index] // 2, scene_frames[index + 1] // 2)
            if frames < 2:
                raise ValueError("Scenes are too short for the requested crossfade")
        elif spec["type"] == "fade_through_black":
            frames = min(frames, scene_frames[index] // 2, scene_frames[index + 1] // 2 if index + 1 < len(scenes) else scene_frames[index] // 2)
            if frames < 2:
                raise ValueError("Scenes are too short for the requested fade-through-black")
        effective.append({"type": spec["type"], "duration_frames": frames})

    total_frames = sum(scene_frames) - sum(
        item["duration_frames"] for item in effective if item["type"] == "crossfade"
    )
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="darkstudio-mixed-", dir=str(out.parent)) as temp_dir:
        temp_root = Path(temp_dir)
        video_root = Path(__import__(
            "modules.ai_video_studio.media.output_paths", fromlist=["get_subsystem_dir"]
        ).get_subsystem_dir("videos")).resolve()
        normalized_paths: list[Path] = []

        for position, scene in enumerate(scenes):
            source_index = int(scene.get("_source_scene_index", scene.get("index", position)))
            duration = scene_frames[position] / fps
            generated_path = generated_clips.get(source_index)
            if generated_path:
                source = Path(generated_path).resolve()
                if video_root not in source.parents or not source.is_file():
                    raise ValueError(
                        f"Generated clip for scene {source_index} is not a valid DARKSTUDIO video asset"
                    )
            else:
                source = temp_root / f"scene_{position:03d}_procedural.mp4"
                render_single_scene_clip(
                    scene, source, duration=duration, fps=fps, width=width, height=height,
                    require_mp4=True, studio_id=studio_id,
                )
                source = source.resolve()

            normalized = temp_root / f"scene_{position:03d}_normalized.mp4"
            command = [
                ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
                "-an", "-vf",
                f"fps={fps},scale={width}:{height}:force_original_aspect_ratio=decrease,"
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1",
                "-frames:v", str(scene_frames[position]), "-r", str(fps), "-c:v", "libx264",
                "-preset", "veryfast", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                str(normalized),
            ]
            completed = subprocess.run(
                command, capture_output=True, text=True, timeout=max(180, duration * 30)
            )
            if completed.returncode != 0 or not normalized.is_file() or normalized.stat().st_size == 0:
                raise RuntimeError(
                    f"Could not normalize mixed scene {source_index}: {completed.stderr[-1200:]}"
                )
            normalized_paths.append(normalized)

        inputs: list[str] = []
        filters: list[str] = []
        for index, clip_path in enumerate(normalized_paths):
            inputs.extend(["-i", str(clip_path)])
            filters.append(
                f"[{index}:v]settb=AVTB,setpts=PTS-STARTPTS,format=yuv420p[v{index}]"
            )

        current_label = "v0"
        current_frames = scene_frames[0]
        for index in range(1, len(scenes)):
            previous_transition = effective[index - 1]
            kind = previous_transition["type"]
            overlap_frames = previous_transition["duration_frames"]
            incoming_label = f"v{index}"
            output_label = f"mix{index}"
            if kind == "crossfade":
                duration_seconds = overlap_frames / fps
                offset_seconds = (current_frames - overlap_frames) / fps
                filters.append(
                    f"[{current_label}][{incoming_label}]"
                    f"xfade=transition=fade:duration={duration_seconds:.9f}:"
                    f"offset={offset_seconds:.9f}[{output_label}]"
                )
                current_frames += scene_frames[index] - overlap_frames
            else:
                if kind == "fade_through_black":
                    fade_seconds = overlap_frames / fps
                    fade_start = (current_frames - overlap_frames) / fps
                    faded_current = f"fadeout{index}"
                    faded_incoming = f"fadein{index}"
                    filters.append(
                        f"[{current_label}]fade=t=out:st={fade_start:.9f}:"
                        f"d={fade_seconds:.9f}:color=black[{faded_current}]"
                    )
                    filters.append(
                        f"[{incoming_label}]fade=t=in:st=0:d={fade_seconds:.9f}:"
                        f"color=black[{faded_incoming}]"
                    )
                    current_label = faded_current
                    incoming_label = faded_incoming
                filters.append(
                    f"[{current_label}][{incoming_label}]concat=n=2:v=1:a=0[{output_label}]"
                )
                current_frames += scene_frames[index]
            current_label = output_label

        command = [
            ffmpeg, "-hide_banner", "-loglevel", "error", "-y", *inputs,
            "-filter_complex", ";".join(filters), "-map", f"[{current_label}]",
            "-an", "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
            "-r", str(fps), "-frames:v", str(total_frames), "-movflags", "+faststart",
            str(out),
        ]
        completed = subprocess.run(
            command, capture_output=True, text=True, timeout=max(300, total_frames / fps * 30)
        )
        if completed.returncode != 0 or not out.is_file() or out.stat().st_size == 0:
            out.unlink(missing_ok=True)
            raise RuntimeError(
                f"Could not assemble mixed DARKSTUDIO timeline: {completed.stderr[-1500:]}"
            )

    return {
        "output_path": str(out),
        "frames": total_frames,
        "bytes": out.stat().st_size,
        "engine": "ffmpeg_mixed_scene_transitions",
        "generated_scene_indices": sorted(int(key) for key in generated_clips),
        "transition_policy": "frame_accurate",
        "transitions_applied": [
            {"scene_index": int(scenes[index].get("_source_scene_index", index)),
             "type": item["type"], "duration_frames": item["duration_frames"]}
            for index, item in enumerate(effective) if item["type"] != "cut"
        ],
    }
