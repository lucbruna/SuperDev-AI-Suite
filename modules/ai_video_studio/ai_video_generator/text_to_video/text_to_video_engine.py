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
import logging
import time
from typing import Any, Callable

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.media.llm import get_scene_planner
from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename
from modules.ai_video_studio.media.render import render_multi_scene_video
from modules.ai_video_studio.ai_video_generator.generation_statistics import get_generation_statistics

logger = logging.getLogger(__name__)

# Single worker used when a sync caller needs to run the async pipeline from
# inside a thread that already owns an event loop.
_SYNC_BRIDGE = concurrent.futures.ThreadPoolExecutor(max_workers=1, thread_name_prefix="ttv_async")

# Cap on narration characters so TTS stays responsive on long storyboards.
_MAX_NARRATION_CHARS = 800


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
    ) -> dict[str, Any]:
        prompt = str(job.get("prompt", "")).strip()
        if not prompt:
            raise ValidationError("A non-empty prompt is required", field="prompt")
        params = job.get("params", {})
        started = time.time()

        num_scenes = max(1, int(params.get("num_scenes", 3)))
        duration = max(1.0, float(params.get("duration", 6.0)))
        fps = max(1, int(params.get("fps", 24)))
        width = int(params.get("width", 1280))
        height = int(params.get("height", 720))

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
        )

        result: dict[str, Any] = {
            "mode": "text_to_video",
            "ai_planner": plan["provider"] or "deterministic",
            "ai_generated": plan["ai_generated"],
            "scenes": scenes,
            "frames": video_result["frames"],
            "fps": fps,
            "duration": duration,
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
            has_scene_text = any(
                (s.get("description") or s.get("voiceover_text") or s.get("name")) for s in scenes
            )
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
                language=str(params.get("voice_language", "en")),
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
        for scene in scenes:
            description = scene.get("description") or scene.get("name") or ""
            if description:
                parts.append(str(description))
        joined = " ".join(parts).strip() if parts else prompt
        return joined[:_MAX_NARRATION_CHARS] or prompt
