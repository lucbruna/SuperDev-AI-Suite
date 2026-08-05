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
    """The narration text for one scene (description > name > empty)."""
    return str(
        scene.get("description")
        or scene.get("voiceover_text")
        or scene.get("name")
        or ""
    ).strip()[:_MAX_SCENE_CHARS]


def compute_scene_offsets(scenes: list[dict[str, Any]], *, fallback_duration: float = 3.0) -> list[float]:
    """Cumulative start time of each scene inside the video timeline.

    A scene without an explicit ``duration`` gets ``fallback_duration``.
    """
    offsets: list[float] = []
    cursor = 0.0
    for scene in scenes:
        offsets.append(cursor)
        cursor += max(0.1, float(scene.get("duration") or fallback_duration))
    return offsets


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
    runs through the full ``ai_voice_studio`` chain (edge-tts → gTTS →
    pyttsx3 → formant) whose last resort is fully local, so narration always
    synthesizes even with no network.

    Returns ``{muxed, output_path, bytes, clips, total_duration, ...}`` where
    ``clips`` lists each scene's ``{index, text, start, end, audio_path,
    tts_engine, audio_duration}``.
    """
    params = params or {}
    scenes = list(scenes)
    if not scenes:
        return {"muxed": False, "reason": "no scenes"}

    offsets = compute_scene_offsets(scenes)
    voice_id = str(params.get("voice_id", "default"))
    language = str(params.get("voice_language", "en"))
    speed = float(params.get("voice_speed", 1.0))
    pitch = float(params.get("voice_pitch", 1.0))

    from modules.ai_video_studio.ai_voice_studio import get_voice_engine

    voice_engine = get_voice_engine()

    clips: list[dict[str, Any]] = []
    synthesized_any = False
    for index, (scene, start) in enumerate(zip(scenes, offsets, strict=False)):
        text = scene_narration_text(scene)
        end = start + max(0.1, float(scene.get("duration") or 3.0))
        clip: dict[str, Any] = {
            "index": scene.get("index", index),
            "text": text[:120],
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
