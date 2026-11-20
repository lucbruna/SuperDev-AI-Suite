"""Per-scene narration — a separate voice clip for every scene, placed on the
video timeline at each scene's cumulative offset (instead of one flat track).

Pipeline: synthesize one TTS clip per scene → time-stretch each clip to its
scene slot (reusing the dubbing aligner) → mix into a single track spanning
the whole video → mux onto the video. Output metadata exposes per-clip
offsets so callers can verify the sync.
"""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename

logger = logging.getLogger(__name__)

# Cap per-scene narration so long descriptions don't stall TTS.
_MAX_SCENE_CHARS = 400


def scene_narration_text(scene: dict[str, Any]) -> str:
    """Prefer authored speech text; use visual description only as a fallback."""
    return str(
        scene.get("voiceover_text")
        or scene.get("narration")
        or scene.get("dialogue")
        or scene.get("description")
        or scene.get("name")
        or ""
    ).strip()[:_MAX_SCENE_CHARS]


def compute_scene_offsets(
    scenes: list[dict[str, Any]], *, fallback_duration: float = 3.0, fps: int = 24
) -> list[float]:
    """Return scene starts on the final rendered timeline.

    Crossfades overlap adjacent scenes, so their duration is subtracted from
    the next scene's start. Fade-through-black and hard cuts do not overlap.
    Frame clamping mirrors the multi-scene renderer.
    """
    if fps < 1:
        raise ValueError("fps must be at least 1")
    from modules.ai_video_studio.media.transitions import transition_spec

    offsets: list[float] = []
    cursor = 0.0
    durations = [max(0.1, float(scene.get("duration") or fallback_duration)) for scene in scenes]
    frame_counts = [max(1, int(round(duration * fps))) for duration in durations]
    for index, scene in enumerate(scenes):
        offsets.append(round(cursor, 6))
        cursor += frame_counts[index] / fps
        spec = transition_spec(scene)
        if spec["type"] == "crossfade":
            if index == len(scenes) - 1:
                raise ValueError("The final scene cannot have an outgoing crossfade")
            overlap = min(spec["duration_frames"], frame_counts[index] // 2, frame_counts[index + 1] // 2)
            if overlap < 2:
                raise ValueError("Scenes are too short for the requested crossfade")
            cursor -= overlap / fps
    return offsets

def _original_clips_by_source(
    original_clips: list[dict[str, Any]],
) -> dict[int, dict[str, Any]]:
    """Index saved narration by source scene, tolerating legacy positional clips."""
    indexed: dict[int, dict[str, Any]] = {}
    for position, clip in enumerate(original_clips):
        if not isinstance(clip, dict):
            continue
        source_index = clip.get("index", position)
        if isinstance(source_index, int) and not isinstance(source_index, bool) and source_index >= 0:
            indexed[source_index] = clip
    return indexed


def narration_text_changes_for_edits(
    scenes: list[dict[str, Any]], original_clips: list[dict[str, Any]]
) -> list[int]:
    """Return source scenes whose speech changed or whose audio is missing."""
    originals = _original_clips_by_source(original_clips)
    changed: list[int] = []
    for position, scene in enumerate(scenes):
        source_index = scene.get("_source_scene_index", position)
        if not isinstance(source_index, int) or isinstance(source_index, bool):
            raise ValueError("scene source index must be an integer")
        original = originals.get(source_index)
        if original is None:
            continue
        previous_text = str(original.get("text") or "").strip()
        current_text = scene_narration_text(scene)
        # A changed/new speech line must be synthesized even when the original
        # TTS attempt failed and therefore left no audio_path.
        if previous_text != current_text and current_text:
            changed.append(source_index)
    return changed


def remap_narration_clips_for_edits(
    scenes: list[dict[str, Any]],
    original_clips: list[dict[str, Any]],
    *,
    fps: int = 24,
    fallback_duration: float = 3.0,
) -> list[dict[str, Any]]:
    """Map original per-scene audio assets onto an edited storyboard.

    Scene identity is carried by _source_scene_index (assigned by
    apply_scene_edits); clip array position is the original scene index.
    Returned clips use the edited scene's frame-accurate slot and order.
    """
    if fps < 1:
        raise ValueError("fps must be at least 1")
    offsets = compute_scene_offsets(
        scenes, fallback_duration=fallback_duration, fps=fps
    )
    stale_source_indices = set(narration_text_changes_for_edits(scenes, original_clips))
    originals = _original_clips_by_source(original_clips)
    remapped: list[dict[str, Any]] = []
    for position, (scene, start) in enumerate(zip(scenes, offsets, strict=False)):
        source_index = scene.get("_source_scene_index", position)
        if not isinstance(source_index, int) or isinstance(source_index, bool):
            raise ValueError("scene source index must be an integer")
        original = originals.get(source_index)
        if not isinstance(original, dict) or not original.get("audio_path") or source_index in stale_source_indices:
            continue
        duration = max(0.1, float(scene.get("duration") or fallback_duration))
        duration_frames = max(1, int(round(duration * fps)))
        remapped.append({
            "index": source_index,
            "text": str(original.get("text") or ""),
            "start": round(start, 6),
            "end": round(start + duration_frames / fps, 6),
            "audio_path": original["audio_path"],
        })
    return remapped




def build_edited_subtitle_scenes(
    scenes: list[dict[str, Any]], narration_clips: list[dict[str, Any]] | None,
    *, fps: int = 24, per_scene_narration: bool = False,
) -> list[dict[str, Any]]:
    """Build captions aligned to the edited timeline and actual speech assets."""
    if fps < 1:
        raise ValueError("fps must be at least 1")
    offsets = compute_scene_offsets(scenes, fps=fps)
    clips_by_source = {
        int(clip.get("index", -1)): clip for clip in (narration_clips or [])
        if isinstance(clip, dict)
    } if per_scene_narration else {}
    output: list[dict[str, Any]] = []
    for position, (scene, start) in enumerate(zip(scenes, offsets, strict=False)):
        source_index = scene.get("_source_scene_index", position)
        if per_scene_narration:
            clip = clips_by_source.get(source_index)
            if not isinstance(clip, dict) or not clip.get("audio_path"):
                continue
            text = str(clip.get("text") or "")
        else:
            text = scene_narration_text(scene)
        if not text.strip():
            continue
        duration = max(1, int(round(float(scene.get("duration") or 3.0) * fps))) / fps
        output.append({"text": text, "duration": duration, "start_offset": start})
    return output

async def regenerate_changed_scene_narration_async(
    scenes: list[dict[str, Any]],
    original_clips: list[dict[str, Any]],
    *,
    params: dict[str, Any] | None = None,
    fps: int = 24,
) -> dict[str, Any]:
    """Regenerate only edited speech while retaining valid scene audio assets.

    The returned clip list follows the edited scene order. Failed TTS scenes are
    represented with an error and no audio path; unchanged clips are never
    synthesized again.
    """
    params = params or {}
    if fps < 1:
        raise ValueError("fps must be at least 1")
    stale = set(narration_text_changes_for_edits(scenes, original_clips))
    valid = remap_narration_clips_for_edits(scenes, original_clips, fps=fps)
    by_source = {int(clip["index"]): dict(clip) for clip in valid}
    if stale:
        from modules.ai_video_studio.ai_voice_studio import get_voice_engine

        engine = get_voice_engine()
        voice_id = str(params.get("voice_id", "default"))
        language = str(params.get("voice_language", "pt-BR"))
        speed = float(params.get("voice_speed", 1.0))
        pitch = float(params.get("voice_pitch", 1.0))
        offsets = compute_scene_offsets(scenes, fps=fps)
        for position, (scene, start) in enumerate(zip(scenes, offsets, strict=False)):
            source_index = scene.get("_source_scene_index", position)
            if source_index not in stale:
                continue
            text = scene_narration_text(scene)
            duration = max(0.1, float(scene.get("duration") or 3.0))
            duration = max(1, int(round(duration * fps))) / fps
            clip: dict[str, Any] = {
                "index": source_index, "text": text,
                "start": round(start, 6), "end": round(start + duration, 6),
            }
            if text:
                try:
                    result = await engine.synthesize_async(
                        text, voice_id=voice_id, language=language,
                        speed=speed, pitch=pitch, output_path=None, use_cache=False,
                    )
                    clip.update({
                        "audio_path": result["output_path"],
                        "tts_engine": result.get("engine"),
                        "audio_duration": result.get("duration"),
                    })
                except Exception as exc:  # TTS failure is isolated to this scene.
                    logger.warning("Edited scene %s narration failed: %s", source_index, exc)
                    clip["error"] = str(exc)[:240]
            by_source[int(source_index)] = clip
    ordered: list[dict[str, Any]] = []
    for position, scene in enumerate(scenes):
        source_index = scene.get("_source_scene_index", position)
        clip = by_source.get(source_index)
        if clip is not None:
            ordered.append(dict(clip))
    return {
        "clips": ordered,
        "regenerated_scene_indices": sorted(stale),
        "failed_scene_indices": sorted(
            int(clip["index"]) for clip in ordered
            if clip.get("error") and not clip.get("audio_path")
        ),
    }

def build_narration_tracks(
    clips: list[dict[str, Any]],
    *,
    sample_rate: int | None = None,
) -> list[dict[str, Any]]:
    """Turn ``{text, start, end, audio_path}`` clips into mix-ready tracks.

    Reuses the dubbing ``place_clips`` aligner so every clip is time-stretched
    to fit its scene slot exactly.
    """
    from modules.ai_video_studio.ai_dubbing.speech_alignment import place_clips

    # Only clips that actually produced audio land on the timeline; scenes
    # with no text (or failed TTS) stay silent at their slot.
    lines = [
        {"text": c["text"], "start": c["start"], "end": c["end"], "audio_path": c["audio_path"]}
        for c in clips
        if c.get("audio_path")
    ]
    if not lines:
        return []
    kwargs: dict[str, Any] = {}
    if sample_rate is not None:
        kwargs["sample_rate"] = sample_rate
    return place_clips(lines, **kwargs)


async def synthesize_scene_narration_async(
    scenes: list[dict[str, Any]],
    *,
    video_path: str,
    params: dict[str, Any] | None = None,
    output_dir: str | None = None,
    output_path: str | None = None,
) -> dict[str, Any]:
    """Synthesize per-scene narration, place it on the timeline and mux.

    Fails soft (``muxed=False`` + ``reason``) so TTS problems never break
    video generation — consistent with the module's pipeline patterns. TTS
    runs through the ``ai_voice_studio`` chain (edge-tts → gTTS →
    pyttsx3). If no speech engine is available, the scene is marked as failed;
    synthetic formant effects are not accepted as spoken narration.

    Returns ``{muxed, output_path, bytes, clips, total_duration, ...}`` where
    ``clips`` lists each scene's ``{index, text, start, end, audio_path,
    tts_engine, audio_duration}``.
    """
    params = params or {}
    scenes = list(scenes)
    if not scenes:
        return {"muxed": False, "reason": "no scenes"}

    fps = max(1, int(params.get("fps", 24)))
    offsets = compute_scene_offsets(scenes, fps=fps)
    voice_id = str(params.get("voice_id", "default"))
    language = str(params.get("voice_language", "pt-BR"))
    speed = float(params.get("voice_speed", 1.0))
    pitch = float(params.get("voice_pitch", 1.0))

    from modules.ai_video_studio.ai_voice_studio import get_voice_engine

    voice_engine = get_voice_engine()

    clips: list[dict[str, Any]] = []
    synthesized_any = False
    for index, (scene, start) in enumerate(zip(scenes, offsets, strict=False)):
        text = scene_narration_text(scene)
        scene_duration = max(0.1, float(scene.get("duration") or 3.0))
        scene_duration = max(1, int(scene_duration * fps)) / fps
        end = start + scene_duration
        clip: dict[str, Any] = {
            "index": scene.get("index", index),
            "text": text,
            "start": round(start, 3),
            "end": round(end, 3),
        }
        if not text:
            clips.append(clip)
            continue
        try:
            synth = await voice_engine.synthesize_async(
                text,
                voice_id=voice_id,
                language=language,
                speed=speed,
                pitch=pitch,
                output_path=None,
                use_cache=False,
            )
        except Exception as e:  # noqa: BLE001 — TTS failure is per-scene non-fatal
            logger.warning("Scene %s narration failed: %s", index, e)
            clip["error"] = str(e)[:120]
            clips.append(clip)
            continue
        clip["audio_path"] = synth["output_path"]
        clip["tts_engine"] = synth["engine"]
        clip["audio_duration"] = synth["duration"]
        clips.append(clip)
        synthesized_any = True

    if not synthesized_any:
        return {"muxed": False, "reason": "no scene narration synthesized", "clips": clips}

    # Mix the placed clips into one track spanning the whole video.
    from modules.ai_video_studio.ai_dubbing.export_dubbing import export_audio_track
    from modules.ai_video_studio.media.audio import mux_audio_into_video

    total_duration = offsets[-1] + max(0.1, float(scenes[-1].get("duration") or 3.0)) \
        if offsets else 0.0
    out_dir = Path(output_dir or get_subsystem_dir("videos"))
    audio_track = str(unique_filename(out_dir, "scene_narration_track", "wav"))
    tracks = build_narration_tracks(clips)
    audio_report = export_audio_track(tracks, audio_track, total_duration=total_duration)

    out = output_path or str(unique_filename(out_dir, "text_to_video_scene_voiced", "mp4"))
    muxed = mux_audio_into_video(video_path, audio_track, out)

    return {
        "muxed": bool(muxed.get("muxed")),
        "output_path": muxed.get("output_path"),
        "bytes": muxed.get("bytes"),
        "clips": clips,
        "total_duration": round(total_duration, 3),
        "audio": audio_report,
        "voice_id": voice_id,
        "language": language,
        "narration_style": "per_scene",
        **({} if muxed.get("muxed") else {"reason": muxed.get("reason")}),
    }


def synthesize_scene_narration(
    scenes: list[dict[str, Any]],
    *,
    video_path: str,
    params: dict[str, Any] | None = None,
    output_dir: str | None = None,
    output_path: str | None = None,
) -> dict[str, Any]:
    """Synchronous wrapper around :func:`synthesize_scene_narration_async`."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(
            synthesize_scene_narration_async(
                scenes, video_path=video_path, params=params,
                output_dir=output_dir, output_path=output_path,
            )
        )
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(
            asyncio.run,
            synthesize_scene_narration_async(
                scenes, video_path=video_path, params=params,
                output_dir=output_dir, output_path=output_path,
            ),
        ).result()
