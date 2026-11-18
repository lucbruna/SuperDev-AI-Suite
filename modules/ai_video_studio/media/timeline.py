"""Serializable, frame-accurate edit decision list for DARKSTUDIO AI.

Frames are the canonical unit. Seconds are accepted only at input boundaries and
are retained as derived metadata for clients that need human-readable timing.
"""
from __future__ import annotations

from typing import Any


TIMELINE_VERSION = "1.0"


def _seconds_to_frames(value: Any, fps: int, *, field: str) -> int:
    try:
        seconds = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be a number of seconds") from exc
    if seconds < 0:
        raise ValueError(f"{field} cannot be negative")
    return int(round(seconds * fps))


def _asset_clips(items: list[dict[str, Any]], fps: int, *, track_type: str) -> list[dict[str, Any]]:
    clips: list[dict[str, Any]] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"{track_type} clip {index} must be an object")
        asset = item.get("asset") or item.get("audio_path") or item.get("path")
        if not asset:
            raise ValueError(f"{track_type} clip {index} requires an asset path")
        start = _seconds_to_frames(item.get("start", 0), fps, field=f"{track_type}[{index}].start")
        end = _seconds_to_frames(item.get("end"), fps, field=f"{track_type}[{index}].end")
        if end <= start:
            raise ValueError(f"{track_type} clip {index} must have positive duration")
        clips.append({
            "asset": str(asset),
            "start_frame": start,
            "end_frame": end,
            "duration_frames": end - start,
            "start_seconds": round(start / fps, 6),
            "end_seconds": round(end / fps, 6),
            **({"text": str(item["text"])} if item.get("text") is not None else {}),
        })
    return clips


def build_edit_timeline(
    scenes: list[dict[str, Any]],
    *,
    fps: int = 24,
    width: int = 1920,
    height: int = 1080,
    fallback_duration: float = 3.0,
    narration: dict[str, Any] | list[dict[str, Any]] | None = None,
    subtitle_cues: list[dict[str, Any]] | None = None,
    music_clips: list[dict[str, Any]] | None = None,
    sfx_clips: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a deterministic multi-track EDL without mutating source scenes.

    Crossfades shorten the assembled timeline by their actual clamped overlap.
    Fade-through-black and cuts do not overlap. Audio/subtitle input times are
    converted to frames and validated independently from the video track.
    """
    if not isinstance(fps, int) or fps < 1:
        raise ValueError("fps must be a positive integer")
    if width < 1 or height < 1:
        raise ValueError("width and height must be positive")
    if not scenes:
        raise ValueError("scenes cannot be empty")

    from modules.ai_video_studio.media.transitions import transition_spec

    video_clips: list[dict[str, Any]] = []
    cursor = 0
    frame_counts: list[int] = []
    specs: list[dict[str, Any]] = []
    for index, scene in enumerate(scenes):
        if not isinstance(scene, dict):
            raise ValueError(f"scene {index} must be an object")
        duration = scene.get("duration", fallback_duration)
        count = _seconds_to_frames(duration, fps, field=f"scene[{index}].duration")
        if count < 1:
            raise ValueError(f"scene {index} duration must be at least one frame")
        frame_counts.append(count)
        specs.append(transition_spec(scene))

    for index, scene in enumerate(scenes):
        start = cursor
        end = start + frame_counts[index]
        transition = specs[index]
        overlap = 0
        if transition["type"] == "crossfade":
            if index == len(scenes) - 1:
                raise ValueError("The final scene cannot have an outgoing crossfade")
            overlap = min(
                transition["duration_frames"],
                frame_counts[index] // 2,
                frame_counts[index + 1] // 2,
            )
            if overlap < 2:
                raise ValueError("Scenes are too short for the requested crossfade")
        video_clips.append({
            "scene_index": index,
            "source_scene_index": scene.get("_source_scene_index", index),
            "start_frame": start,
            "end_frame": end,
            "duration_frames": frame_counts[index],
            "start_seconds": round(start / fps, 6),
            "end_seconds": round(end / fps, 6),
            "shot_type": scene.get("shot_type", "medium"),
            "transition_out": {
                "type": transition["type"],
                "duration_frames": transition["duration_frames"],
                "overlap_frames": overlap,
            },
        })
        cursor = end - overlap

    tracks: list[dict[str, Any]] = [{"id": "video-main", "type": "video", "clips": video_clips}]

    narration_items: list[dict[str, Any]] = []
    if isinstance(narration, dict):
        narration_items = list(narration.get("clips") or [])
    elif isinstance(narration, list):
        narration_items = narration
    # Per-scene TTS reports include silent/failed scenes without audio_path.
    narration_items = [item for item in narration_items if item.get("audio_path") or item.get("asset") or item.get("path")]
    narration_clips = _asset_clips(narration_items, fps, track_type="narration")
    if narration_clips:
        tracks.append({"id": "audio-narration", "type": "audio", "role": "narration", "clips": narration_clips})

    music = _asset_clips(list(music_clips or []), fps, track_type="music")
    if music:
        tracks.append({"id": "audio-music", "type": "audio", "role": "music", "clips": music})

    effects = _asset_clips(list(sfx_clips or []), fps, track_type="sfx")
    if effects:
        tracks.append({"id": "audio-sfx", "type": "audio", "role": "sound_effect", "clips": effects})

    captions: list[dict[str, Any]] = []
    for index, cue in enumerate(subtitle_cues or []):
        if not isinstance(cue, dict):
            raise ValueError(f"subtitle cue {index} must be an object")
        start = _seconds_to_frames(cue.get("start"), fps, field=f"subtitle[{index}].start")
        end = _seconds_to_frames(cue.get("end"), fps, field=f"subtitle[{index}].end")
        if end <= start:
            raise ValueError(f"subtitle cue {index} must have positive duration")
        if not str(cue.get("text") or "").strip():
            raise ValueError(f"subtitle cue {index} requires text")
        captions.append({
            "cue_index": int(cue.get("index", index + 1)),
            "start_frame": start,
            "end_frame": end,
            "duration_frames": end - start,
            "text": str(cue["text"]),
        })
    if captions:
        tracks.append({"id": "text-subtitles", "type": "subtitle", "clips": captions})

    return {
        "version": TIMELINE_VERSION,
        "timebase": "frames",
        "fps": fps,
        "width": width,
        "height": height,
        "duration_frames": cursor,
        "duration_seconds": round(cursor / fps, 6),
        "tracks": tracks,
    }


def apply_scene_edits(
    scenes: list[dict[str, Any]],
    *,
    scene_order: list[int] | None = None,
    scene_edits: list[dict[str, Any]] | None = None,
    fps: int = 24,
) -> list[dict[str, Any]]:
    """Return a validated, reordered storyboard with frame-accurate edits.

    The input is never mutated. Scene indices refer to the original storyboard,
    not to positions after reordering.
    """
    import copy

    if not isinstance(fps, int) or fps < 1:
        raise ValueError("fps must be a positive integer")
    if not scenes:
        raise ValueError("scenes cannot be empty")
    total = len(scenes)
    order = list(range(total)) if scene_order is None else list(scene_order)
    if len(order) != total or set(order) != set(range(total)):
        raise ValueError("scene_order must contain every scene index exactly once")

    edits_by_index: dict[int, dict[str, Any]] = {}
    for edit in scene_edits or []:
        if not isinstance(edit, dict):
            raise ValueError("each scene edit must be an object")
        index = edit.get("scene_index")
        if not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < total:
            raise ValueError("scene edit has an invalid scene_index")
        if index in edits_by_index:
            raise ValueError(f"duplicate edit for scene {index}")
        edits_by_index[index] = edit

    result = []
    for original_index in order:
        scene = copy.deepcopy(scenes[original_index])
        scene["_source_scene_index"] = original_index
        result.append(scene)
    for position, scene in enumerate(result):
        original_index = order[position]
        edit = edits_by_index.get(original_index)
        if not edit:
            continue
        if "duration_frames" in edit:
            frames = edit["duration_frames"]
            if not isinstance(frames, int) or isinstance(frames, bool) or not fps // 2 <= frames <= fps * 60:
                raise ValueError("duration_frames must be between 0.5 and 60 seconds")
            scene["duration"] = frames / fps
        transition = edit.get("transition_type")
        if transition is not None:
            if transition not in {"cut", "crossfade", "fade_through_black"}:
                raise ValueError("unsupported transition_type")
            if position == total - 1 and transition != "cut":
                raise ValueError("the final scene must use cut")
            if transition == "cut":
                scene["transition_out"] = {"type": "cut", "duration_frames": 0}
            else:
                frames = edit.get("transition_duration_frames", max(2, round(fps * 0.5)))
                if not isinstance(frames, int) or isinstance(frames, bool) or not 2 <= frames <= fps * 5:
                    raise ValueError("transition duration must be between 2 frames and 5 seconds")
                scene["transition_out"] = {"type": transition, "duration_frames": frames}
        elif position == total - 1:
            # A scene moved to the end cannot retain an outgoing crossfade.
            current = scene.get("transition_out") or {}
            if current.get("type") != "cut":
                scene["transition_out"] = {"type": "cut", "duration_frames": 0}

    # Validate the complete resulting timeline, including transition overlap.
    build_edit_timeline(result, fps=fps)
    return result
