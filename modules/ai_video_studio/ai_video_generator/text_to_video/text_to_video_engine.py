"""Text to video engine — real MP4 generation from text prompts.

Pipeline: prompt → Ollama scene plan (deterministic fallback) → PIL/numpy
frame rendering → FFmpeg encoding → optional AI voiceover narration
(VoiceStudioService: edge-tts → gTTS → pyttsx3 offline).

The output is a real video file under ``modules/downloads/videos/``. Voice
narration is additive: when TTS fails, the silent video is returned with a
``voiceover`` metadata block explaining what happened — generation never
breaks because of audio.
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import hashlib
import logging
import time
from typing import Any, Callable

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.media.llm import get_scene_planner
from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename
from modules.ai_video_studio.media.render import render_multi_scene_video, render_single_scene_clip
from modules.ai_video_studio.media.characters import PRESETS, add_character
from modules.ai_video_studio.media.scene_library import OBJECTS, compose_scene_object
from modules.ai_video_studio.ai_video_generator.generation_statistics import get_generation_statistics

logger = logging.getLogger(__name__)

# Single worker used when a sync caller needs to run the async pipeline from
# inside a thread that already owns an event loop.
_SYNC_BRIDGE = concurrent.futures.ThreadPoolExecutor(max_workers=1, thread_name_prefix="ttv_async")

# Cap on narration characters so TTS stays responsive on long storyboards.
_MAX_NARRATION_CHARS = 800


def derive_scene_image_seed(
    job_id: str,
    scene: dict[str, Any],
    scene_index: int,
    base_seed: int | None = None,
) -> int:
    """Return a stable, distinct 31-bit seed for one scene image.

    An explicit base seed makes the same scene reproducible across jobs.
    Without one, the job ID provides a fresh but repeatable seed namespace.
    """
    scene_identity = str(
        scene.get("storyboard_scene_id")
        or scene.get("name")
        or f"scene-{scene_index + 1}"
    )
    namespace = f"seed:{int(base_seed)}" if base_seed is not None else f"job:{job_id}"
    digest = hashlib.sha256(
        f"{namespace}:{scene_identity}:{scene_index}".encode("utf-8")
    ).digest()
    return int.from_bytes(digest[:4], "big") & 0x7FFFFFFF


class TextToVideoEngine:
    """Runs the real text-to-video generation pipeline for a job."""

    # ── Sync entry point (used by the task dispatcher) ────────────
    def generate(
        self,
        job: dict[str, Any],
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> dict[str, Any]:
        """Synchronous convenience wrapper around :meth:`generate_async`.

        * Outside an event loop (typical CLI/dispatcher use) a loop is driven
          here with :func:`asyncio.run`.
        * Inside a running loop, the async pipeline runs in a worker thread.
          Note: calling this from the event-loop thread still blocks it while
          the pipeline runs — async callers should use ``generate_async``
          directly to avoid that.

        ``progress_callback(rendered, total_frames)`` is forwarded to
        :meth:`generate_async` and fired as frames are rendered.
        """
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            # No loop is running → safe to drive one here.
            return asyncio.run(self.generate_async(job, progress_callback=progress_callback))

        # A loop is already running; run the async pipeline in a worker thread.
        return _SYNC_BRIDGE.submit(
            asyncio.run, self.generate_async(job, progress_callback=progress_callback)
        ).result()

    # ── Async entry point (recommended for FastAPI/async callers) ──
    async def generate_async(
        self,
        job: dict[str, Any],
        progress_callback: Callable[[int, int], None] | None = None,
        scene_callback: Callable[[dict[str, Any]], None] | None = None,
    ) -> dict[str, Any]:
        prompt = str(job.get("prompt", "")).strip()
        if not prompt:
            raise ValidationError("A non-empty prompt is required", field="prompt")
        params = job.get("params", {})
        started = time.time()

        num_scenes = min(60, max(1, int(params.get("num_scenes", 3))))
        duration = max(1.0, float(params.get("duration", 6.0)))
        vidgrid_compatible = bool(params.get("vidgrid_compatible", False))
        if vidgrid_compatible:
            duration = num_scenes * 10.0
        fps = max(1, int(params.get("fps", 24)))
        width = int(params.get("width", 1280))
        height = int(params.get("height", 720))

        character_ids = list(params.get("character_ids") or [])
        object_ids = list(params.get("object_ids") or [])
        if len(character_ids) > 20 or len(character_ids) != len(set(character_ids)):
            raise ValidationError(
                "Select up to twenty unique user-defined character references",
                field="character_ids",
            )

        studio_id = str(params.get("studio_id") or "custom")
        if len(object_ids) > 50 or len(object_ids) != len(set(object_ids)):
            raise ValidationError(
                "Select up to fifty unique user-defined object references",
                field="object_ids",
            )

        # Ollama on CPU needs time for the first model load (~90s); callers
        # may override with ``llm_timeout``. Falls back to the deterministic
        # planner automatically on timeout.
        llm_timeout = float(params.get("llm_timeout", 60.0))
        plan = get_scene_planner().plan(
            prompt, num_scenes=num_scenes, duration=duration, timeout=llm_timeout,
        )
        scenes = plan["scenes"]
        if not scenes:
            raise ValidationError("Scene planner returned no scenes", field="prompt")

        def _notify_scene(index: int, status: str, stage: str, **details: Any) -> None:
            if scene_callback is None:
                return
            try:
                scene_callback({
                    "scene_index": index, "status": status, "stage": stage,
                    "updated_at": time.time(), **details,
                })
            except Exception:
                # Progress telemetry must never abort the media pipeline.
                pass

        for scene_index, scene in enumerate(scenes):
            _notify_scene(
                scene_index, "pending", "storyboard",
                title=str(scene.get("title") or scene.get("description") or f"Cena {scene_index + 1}")[:180],
                visual_prompt=str(scene.get("visual_prompt_full") or scene.get("visual_prompt") or scene.get("description") or "")[:1200],
            )
        if vidgrid_compatible:
            for scene in scenes:
                scene["duration"] = 10.0

        # Direct the storyboard before image generation so scene-specific
        # visual prompt suggestions actually influence each generated image.
        from modules.ai_video_studio.media.editing_director import (
            build_editing_report, direct_storyboard,
        )

        scene_fallback_duration = duration / len(scenes)
        scenes = direct_storyboard(
            scenes,
            studio_id=studio_id,
            fps=fps,
            fallback_duration=scene_fallback_duration,
        )

        # Convert each authored narration beat into a scene-specific visual
        # brief, with stable IDs and continuity metadata before image creation.
        from modules.ai_video_studio.media.storyboard_director import build_cinematic_storyboard

        scenes, storyboard_report = build_cinematic_storyboard(
            scenes,
            studio_id=studio_id,
            character_ids=character_ids,
            object_ids=object_ids,
            style_prompt=str(params.get("style") or "").strip() or None,
        )
        for scene in scenes:
            scene["_darkstudio_characters"] = list(character_ids)
            scene["_darkstudio_objects"] = list(object_ids)

        # Generate a unique still image for each storyboard scene when the
        # user explicitly selects the local diffusion provider. Auto mode is
        # allowed to fall back, but records every fallback in the job manifest.
        image_mode = str(params.get("scene_image_mode") or "auto")
        if image_mode not in {"procedural", "ai", "auto"}:
            raise ValidationError("scene_image_mode must be procedural, ai or auto", field="scene_image_mode")
        scene_assets: list[dict[str, Any]] = []
        if image_mode in {"ai", "auto"}:
            from modules.ai_video_studio.ai_image_generator.providers.local_diffusion import (
                fit_image_dimensions, generate_scene_image,
            )
            image_width, image_height = fit_image_dimensions(width, height)

            # The storyboard prompt already contains the selected style. Do not
            # prepend a fixed studio aesthetic: custom prompts must control the
            # visual language scene by scene.
            image_style = ""
            # Circuit breaker for auto mode: once the local diffusion service
            # fails, do not wait through the timeout again for every remaining
            # scene. Preserve each scene in the manifest and use procedural
            # composition for the rest of this job.
            image_provider_unavailable = False
            for scene_index, scene in enumerate(scenes):
                if image_mode == "auto" and image_provider_unavailable:
                    reason = "Local image provider already failed for this job; skipped further connection attempts"
                    _notify_scene(
                        scene_index, "fallback", "image_fallback",
                        image_fallback=True, error=reason,
                    )
                    scene_assets.append({
                        "scene_index": scene_index,
                        "provider": "procedural_fallback",
                        "status": "fallback",
                        "reason": reason,
                        "seed": None,
                    })
                    continue
                _notify_scene(scene_index, "processing", "image_generation")
                visual_prompt = str(
                    scene.get("visual_prompt_full")
                    or scene.get("visual_prompt")
                    or scene.get("visual_prompt_suggestion")
                    or scene.get("description")
                    or prompt
                )
                full_prompt = (
                    f"{image_style + '. ' if image_style else ''}{visual_prompt} "
                    "No captions, no typography, no watermark."
                )
                image_seed = derive_scene_image_seed(
                    str(job.get("id") or job.get("job_id") or prompt[:200]),
                    scene,
                    scene_index,
                    params.get("scene_image_seed"),
                )
                scene["image_generation_seed"] = image_seed
                try:
                    generated = await asyncio.to_thread(
                        generate_scene_image,
                        full_prompt,
                        negative_prompt=str(scene.get("negative_prompt") or ""),
                        width=image_width,
                        height=image_height,
                        steps=int(params.get("scene_image_steps", 20)),
                        seed=image_seed,
                        timeout=float(params.get("scene_image_timeout", 180)),
                    )
                    scene["background_image_path"] = generated["image_path"]
                    scene["image_asset_provider"] = generated["provider"]
                    _notify_scene(
                        scene_index, "completed", "image_ready",
                        image_provider=generated["provider"], image_seed=image_seed,
                        image_path=generated["image_path"], scene_snapshot=dict(scene),
                    )
                    scene_assets.append({
                        "scene_index": scene_index,
                        "image_path": generated["image_path"],
                        "provider": generated["provider"],
                        "status": "generated",
                        "prompt": full_prompt,
                        "seed": image_seed,
                    })
                except Exception as exc:
                    if image_mode == "ai":
                        raise ValidationError(
                            f"AI image generation failed for scene {scene_index + 1}: {str(exc)[:240]}",
                            field="scene_image_mode",
                        ) from exc
                    image_provider_unavailable = True
                    _notify_scene(scene_index, "fallback", "image_fallback", image_fallback=True, error=str(exc)[:240])
                    scene_assets.append({
                        "scene_index": scene_index,
                        "provider": "procedural_fallback",
                        "status": "fallback",
                        "reason": str(exc)[:240],
                        "seed": image_seed,
                    })
            if image_mode == "auto" and any(item["status"] == "fallback" for item in scene_assets):
                image_mode = "auto_with_fallback"
            elif image_mode in {"ai", "auto"}:
                image_mode = "ai_generated"

        # Apply the same registered character identities to every scene.
        # Pose/expression variations are deterministic across the storyboard.
        if character_ids:
            scale = max(0.35, min(width, height) / 720.0)
            for scene_index, scene in enumerate(scenes):
                for character_index, character_id in enumerate(character_ids):
                    # Only built-in procedural avatars can be drawn as primitives.
                    # Arbitrary user references remain in the storyboard/image prompt.
                    if character_id not in PRESETS:
                        continue
                    if len(character_ids) == 1:
                        x = width * 0.5
                    else:
                        x = width * (0.34 if character_index == 0 else 0.66)
                    scene_words = " ".join(str(scene.get(key) or "") for key in (
                        "visual_prompt", "description", "voiceover_text",
                    )).lower()
                    pose = str(scene.get("character_pose") or "")
                    if pose not in {"neutral", "explain", "point"}:
                        pose = (
                            "point" if any(word in scene_words for word in ("point", "pointing", "apont", "indica"))
                            else "explain" if any(word in scene_words for word in ("explain", "explaining", "explica", "mostra"))
                            else "neutral"
                        )
                    expression = str(scene.get("character_expression") or "")
                    if expression not in {"neutral", "happy", "surprised", "concerned"}:
                        expression = (
                            "surprised" if any(word in scene_words for word in ("surprised", "surpresa", "surpres", "espant"))
                            else "concerned" if any(word in scene_words for word in ("concern", "preocup", "alerta"))
                            else "happy" if any(word in scene_words for word in ("happy", "feliz", "sorr"))
                            else "neutral"
                        )
                    scenes[scene_index]["character_pose"] = pose
                    scenes[scene_index]["character_expression"] = expression
                    scenes[scene_index] = add_character(
                        scenes[scene_index],
                        character_id,
                        x=x,
                        y=height * 0.88,
                        scale=scale,
                        pose=pose,
                        expression=expression,
                    )

        # Add selected reusable props to every scene. Spread them across the
        # lower-middle visual field so they remain visible beside characters.
        if object_ids:
            object_scale = max(0.35, min(width, height) / 720.0)
            for scene_index, scene in enumerate(scenes):
                for object_index, object_id in enumerate(object_ids):
                    # Custom object references guide generated imagery; only
                    # registered library objects have procedural primitives.
                    if object_id not in OBJECTS:
                        continue
                    x = width * (0.12 + 0.14 * (object_index % 6))
                    y = height * (0.48 + 0.04 * (object_index % 2))
                    scenes[scene_index] = compose_scene_object(
                        scenes[scene_index], object_id,
                        x=x, y=y, scale=object_scale,
                        motion_start_frame=object_index * max(1, fps // 3),
                    )

        # Persist a complete scene manifest before expensive video rendering.
        # The API stores these snapshots incrementally so a later failure does
        # not leave generated assets without the storyboard that describes them.
        for scene_index, scene in enumerate(scenes):
            _notify_scene(
                scene_index, "processing", "scene_render",
                scene_snapshot=dict(scene),
            )

        # Produce the final pacing and visual-coverage report from the
        # already-directed storyboard used by the image and video renderers.
        editing_report = build_editing_report(
            scenes, fps=fps, fallback_duration=scene_fallback_duration,
            target_words_per_minute=int(params.get("target_words_per_minute", 145)),
        )

        out = unique_filename(get_subsystem_dir("videos"), "text_to_video", "mp4")

        def _on_frame(rendered: int, total: int) -> None:
            if progress_callback is not None:
                progress_callback(rendered, total)

        # Run the CPU-bound render in a worker thread: keeps the event loop
        # free so job polling (progress bar) stays responsive during 5–10 min
        # videos instead of blocking the whole server.
        video_result = await asyncio.to_thread(
            render_multi_scene_video,
            scenes,
            out,
            fps=fps,
            width=width,
            height=height,
            on_frame=_on_frame,
            require_mp4=True,
            studio_id=studio_id,
        )

        # VidGrid imports clips individually, so export a separate strict MP4
        # for every ten-second scene in addition to the assembled full video.
        scene_clips: list[dict[str, Any]] = []
        if vidgrid_compatible:
            clip_dir = get_subsystem_dir("videos") / "vidgrid_clips"
            for scene_index, scene in enumerate(scenes):
                _notify_scene(scene_index, "processing", "clip_render")
                clip_path = unique_filename(clip_dir, f"scene_{scene_index + 1:02d}", "mp4")
                clip_result = await asyncio.to_thread(
                    render_single_scene_clip,
                    scene,
                    clip_path,
                    duration=10.0,
                    fps=fps,
                    width=width,
                    height=height,
                    require_mp4=True,
                    studio_id=studio_id,
                )
                _notify_scene(
                    scene_index, "completed", "clip_ready",
                    clip_path=clip_result["output_path"],
                    clip_bytes=clip_result.get("bytes"),
                )
                scene_clips.append({
                    "scene_index": scene_index,
                    "duration": 10.0,
                    "fps": fps,
                    "width": width,
                    "height": height,
                    "output_path": clip_result["output_path"],
                    "bytes": clip_result["bytes"],
                    "encode_engine": clip_result["engine"],
                    "visual_prompt": scene.get("visual_prompt") or scene.get("description", ""),
                    "narration_text": scene.get("voiceover_text") or scene.get("narration") or "",
                })

        result: dict[str, Any] = {
            "mode": "text_to_video",
            "studio_id": studio_id,
            "scene_image_mode": image_mode,
            "scene_assets": scene_assets,
            "vidgrid_compatible": vidgrid_compatible,
            "clip_duration_seconds": 10.0 if vidgrid_compatible else None,
            "scene_clips": scene_clips,
            "ai_planner": plan["provider"] or "deterministic",
            "ai_generated": plan["ai_generated"],
            "scenes": scenes,
            "editing_report": editing_report,
            "storyboard_report": storyboard_report,
            "frames": video_result["frames"],
            "fps": fps,
            "duration": round(video_result["frames"] / fps, 3),
            "planned_duration": duration,
            "output_path": video_result["output_path"],
            "output_bytes": video_result["bytes"],
            "encode_engine": video_result["engine"],
            "voiceover": None,
        }

        # Optional AI voice narration.
        if params.get("voiceover"):
            voice = await self._add_voiceover(
                prompt,
                scenes,
                video_path=result["output_path"],
                params=params,
            )
            result["voiceover"] = voice
            if voice and voice.get("muxed"):
                result["output_path"] = voice["output_path"]
                result["output_bytes"] = voice.get("bytes", result["output_bytes"])

            # Keep VidGrid scene exports self-contained: mux the matching
            # per-scene narration clip into each ten-second MP4 independently.
            if vidgrid_compatible and scene_clips:
                if voice and voice.get("narration_style") == "per_scene":
                    from modules.ai_video_studio.media.audio import mux_audio_into_video

                    narration_by_index = {
                        int(item.get("index", -1)): item
                        for item in (voice.get("clips") or [])
                        if isinstance(item, dict)
                    }
                    for scene_clip in scene_clips:
                        narration_clip = narration_by_index.get(scene_clip["scene_index"])
                        audio_path = narration_clip.get("audio_path") if narration_clip else None
                        if not audio_path:
                            scene_clip["audio_status"] = "no_scene_narration"
                            continue
                        voiced_path = unique_filename(
                            get_subsystem_dir("videos") / "vidgrid_clips",
                            f"scene_{scene_clip['scene_index'] + 1:02d}_voiced",
                            "mp4",
                        )
                        mux_result = await asyncio.to_thread(
                            mux_audio_into_video,
                            scene_clip["output_path"],
                            audio_path,
                            voiced_path,
                        )
                        if mux_result.get("muxed"):
                            scene_clip["output_path"] = mux_result["output_path"]
                            scene_clip["bytes"] = mux_result.get("bytes", scene_clip["bytes"])
                            scene_clip["audio_status"] = "per_scene_narration_muxed"
                        else:
                            reason = str(mux_result.get("reason") or "audio mux failed")[:200]
                            scene_clip["audio_status"] = "narration_mux_failed"
                            scene_clip["audio_error"] = reason
                            raise RuntimeError(
                                "VidGrid scene {} narration could not be embedded: {}".format(
                                    scene_clip["scene_index"] + 1, reason
                                )
                            )
                elif voice and voice.get("narration_style") == "single_track":
                    for scene_clip in scene_clips:
                        scene_clip["audio_status"] = "single_track_not_split"
                else:
                    for scene_clip in scene_clips:
                        scene_clip["audio_status"] = "silent_or_tts_unavailable"

            # Persist the final clip path and narration result after muxing. The
            # earlier clip_ready checkpoint is only the silent visual intermediate.
            for scene_clip in scene_clips:
                _notify_scene(
                    scene_clip["scene_index"], "completed", "clip_ready",
                    clip_path=scene_clip["output_path"],
                    clip_bytes=scene_clip.get("bytes"),
                    clip_duration=10.0,
                    clip_fps=fps,
                    clip_width=width,
                    clip_height=height,
                    clip_audio_status=scene_clip.get("audio_status"),
                    clip_narration_path=(
                        (narration_by_index.get(scene_clip["scene_index"]) or {}).get("audio_path")
                        if scene_clip.get("audio_status") == "per_scene_narration_muxed"
                        and voice and voice.get("narration_style") == "per_scene"
                        else None
                    ),
                )

        # Optional timed SRT sidecar. Keep subtitles as a separate deliverable
        # so callers can review/edit them before any burn-in/export decision.
        if params.get("generate_subtitles") or params.get("subtitles"):
            try:
                from modules.ai_video_studio.media.scene_narration import (
                    compute_scene_offsets, scene_narration_text,
                )
                from modules.ai_video_studio.services.subtitle_studio import SubtitleStudioService

                subtitle_offsets = compute_scene_offsets(scenes, fallback_duration=duration / len(scenes), fps=fps)
                subtitle_scenes = [
                    {
                        "text": scene_narration_text(scene),
                        "duration": max(1, int(float(scene.get("duration") or duration / len(scenes)) * fps)) / fps,
                        "start_offset": subtitle_offsets[index],
                    }
                    for index, scene in enumerate(scenes)
                ]
                subtitle_path = unique_filename(
                    get_subsystem_dir("subtitles"), "text_to_video_subtitles", "srt"
                )
                subtitle_result = SubtitleStudioService().generate_srt(
                    subtitle_scenes, output_path=str(subtitle_path)
                )
                result["subtitles"] = {
                    "format": "srt",
                    "file_path": subtitle_result["file_path"],
                    "cue_count": subtitle_result["cue_count"],
                    "duration": subtitle_result["duration"],
                }
            except Exception as e:  # noqa: BLE001 — sidecar failure is non-fatal
                logger.warning("Subtitle generation failed: %s", e)
                result["subtitles"] = {"generated": False, "reason": str(e)[:200]}

        # Persist the same frame-accurate EDL used by rendering and sidecar generation.
        try:
            from modules.ai_video_studio.media.timeline import build_edit_timeline
            timeline_subtitles: list[dict[str, Any]] = []
            subtitle_metadata = result.get("subtitles") or {}
            if subtitle_metadata.get("file_path"):
                from modules.ai_video_studio.media.scene_narration import compute_scene_offsets, scene_narration_text
                from modules.ai_video_studio.services.subtitle_studio import cues_for_scene

                subtitle_offsets = compute_scene_offsets(
                    scenes, fallback_duration=scene_fallback_duration, fps=fps
                )
                for scene_index, scene in enumerate(scenes):
                    scene_duration = max(
                        1, int(float(scene.get("duration") or scene_fallback_duration) * fps)
                    ) / fps
                    for cue in cues_for_scene(
                        scene_narration_text(scene), scene_duration,
                        start_offset=subtitle_offsets[scene_index],
                    ):
                        timeline_subtitles.append({
                            "index": cue.index,
                            "start": cue.start,
                            "end": cue.end,
                            "text": cue.text,
                        })
            result["edit_timeline"] = build_edit_timeline(
                scenes,
                fps=fps,
                width=width,
                height=height,
                fallback_duration=scene_fallback_duration,
                narration=result.get("voiceover"),
                subtitle_cues=timeline_subtitles,
            )
        except Exception as e:  # noqa: BLE001 — EDL is diagnostic metadata, not a render blocker
            logger.warning("Edit timeline metadata could not be built: %s", e)
            result["edit_timeline"] = None

        elapsed = (time.time() - started) * 1000
        get_generation_statistics().record(
            mode="text_to_video", duration_ms=elapsed, quality_score=0.8,
        )
        result["elapsed_seconds"] = round(elapsed / 1000, 3)
        result["output_ref"] = f"ttv_{job.get('id')}"
        return result

    # ── Voice narration ────────────────────────────────────────────
    async def _add_voiceover(
        self,
        prompt: str,
        scenes: list[dict[str, Any]],
        *,
        video_path: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Synthesize narration and mux it into the video.

        Default is **per-scene narration**: one TTS clip per scene placed at
        that scene's cumulative offset in the video timeline. When no scene
        carries its own text (or the caller requests ``voiceover_mode="single"``)
        a single flat track over the whole video is used instead.

        Fails soft (logs a warning, returns an unmuxed marker) so TTS
        problems never break generation — consistent with the module's
        pipeline fallback patterns.
        """
        try:
            from modules.ai_video_studio.media.scene_narration import (
                synthesize_scene_narration_async,
            )

            per_scene = str(params.get("voiceover_mode", "per_scene")).lower() != "single"
            from modules.ai_video_studio.media.scene_narration import scene_narration_text

            has_scene_text = any(scene_narration_text(s) for s in scenes)
            if per_scene and has_scene_text:
                result = await synthesize_scene_narration_async(
                    scenes,
                    video_path=video_path,
                    params=params,
                )
                if result.get("muxed"):
                    narration = " ".join(
                        c.get("text", "") for c in (result.get("clips") or []) if c.get("text")
                    )[:200]
                    return {
                        **result,
                        "narration_style": "per_scene",
                        "narration": narration,
                    }
                logger.warning(
                    "Per-scene voiceover not muxed (%s) — falling back to single track",
                    result.get("reason"),
                )
            return await self._add_voiceover_single(prompt, scenes, video_path=video_path, params=params)
        except Exception as e:  # noqa: BLE001 — never let narration break generation
            logger.warning("Per-scene voiceover failed (%s) — falling back to single track", e)
            return await self._add_voiceover_single(prompt, scenes, video_path=video_path, params=params)

    async def _add_voiceover_single(
        self,
        prompt: str,
        scenes: list[dict[str, Any]],
        *,
        video_path: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        """Legacy flat narration track spanning the whole video."""
        narration = self._build_narration(prompt, scenes)
        if not narration.strip():
            return {"muxed": False, "reason": "no narration text"}

        try:
            from modules.ai_video_studio.ai_voice_studio import get_voice_engine
            from modules.ai_video_studio.media.audio import mux_audio_into_video

            synth = await get_voice_engine().synthesize_async(
                narration,
                voice_id=str(params.get("voice_id", "default")),
                language=str(params.get("voice_language", "pt-BR")),
                speed=float(params.get("voice_speed", 1.0)),
                pitch=float(params.get("voice_pitch", 1.0)),
            )
        except Exception as e:  # noqa: BLE001 — TTS failure is non-fatal
            logger.warning("Voiceover synthesis failed: %s", e)
            return {"muxed": False, "reason": f"tts_failed: {e}"}

        out = unique_filename(get_subsystem_dir("videos"), "text_to_video_voiced", "mp4")
        muxed = mux_audio_into_video(video_path, synth["output_path"], out)
        return {
            "muxed": bool(muxed.get("muxed")),
            "output_path": muxed.get("output_path"),
            "bytes": muxed.get("bytes"),
            "tts_engine": synth.get("engine"),
            "audio_duration": synth.get("duration"),
            "narration": narration[:200],
            "narration_style": "single_track",
            **({} if muxed.get("muxed") else {"reason": muxed.get("reason")}),
        }

    @staticmethod
    def _build_narration(prompt: str, scenes: list[dict[str, Any]]) -> str:
        """Compose (and cap) the narration text from scene descriptions."""
        parts: list[str] = []
        from modules.ai_video_studio.media.scene_narration import scene_narration_text

        for scene in scenes:
            text = scene_narration_text(scene)
            if text:
                parts.append(text)
        joined = " ".join(parts).strip() if parts else prompt
        return joined[:_MAX_NARRATION_CHARS] or prompt
