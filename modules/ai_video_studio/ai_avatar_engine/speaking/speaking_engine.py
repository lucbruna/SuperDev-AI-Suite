"""Speaking Avatar Engine — avatar × voice studio × lip-sync → narrated video.

Connects three subsystems into one end-to-end pipeline:

1. **AI Voice Studio** (``ai_voice_studio``) synthesizes the narration audio
   (edge-tts → gTTS → pyttsx3 → offline formant) with a real file as output.
2. **AI Lip Sync** (``ai_lip_sync``) times the text against the audio and
   produces a per-frame viseme timeline (mouth open/round/wide + blinks).
3. **Avatar Engine** (this package) composes per-frame facial parameters
   from the visemes, renders a talking presenter head with the avatar's
   appearance (skin/hair/eyes) and muxes the narration onto the video.

Output is a real video file (MP4 via FFmpeg, GIF fallback) under
``modules/downloads/avatars/`` plus a per-frame JSON timeline for animators.

Everything follows the studio pattern: singleton accessor ``get_*``,
numpy/PIL primitives, JSON-serializable results, cross-subsystem imports
kept lazy so optional subsystems never break the core engine.
"""
from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path
from typing import Any

from modules.ai_video_studio.ai_avatar_engine.avatar_engine import get_avatar_engine
from modules.ai_video_studio.ai_avatar_engine.avatar_profiles import AvatarProfile
from modules.ai_video_studio.ai_avatar_engine.facial_animation.facial_engine import (
    get_facial_engine,
)
from modules.ai_video_studio.ai_avatar_engine.speaking.avatar_renderer import render_frames
from modules.ai_video_studio.editor_common import clamp

logger = logging.getLogger(__name__)


def compose_facial(frame: dict[str, Any], emotion_facial: dict[str, float] | None = None) -> dict[str, Any]:
    """Map one lip-sync facial frame to facial-engine compose inputs.

    ``frame`` is an entry of the AI Lip Sync ``facial`` timeline, which
    carries ``time``, ``open`` (mouth openness), ``_blink`` (0 = closed,
    1 = open) plus viseme metadata. ``emotion_facial`` optionally injects a
    base emotion (smile, brows) on top of the visemes.
    """
    ef = emotion_facial or {}
    blink_closed = 1.0 if float(frame.get("_blink", 1.0)) < 0.5 else 0.0
    return {
        "t": float(frame.get("time", 0.0)),
        "smile": float(ef.get("smile", 0.0)),
        "mouth_open": clamp(float(frame.get("open", 0.0)), 0.0, 1.0),
        "brow_raise": float(ef.get("brow_raise", 0.0)),
        "brow_frown": float(ef.get("brow_frown", 0.0)),
        "forced_blink": blink_closed,
    }


class SpeakingAvatarEngine:
    """End-to-end narrator: TTS narration → lip-sync → talking-avatar video."""

    async def generate(
        self,
        profile_id: str,
        text: str,
        *,
        voice_id: str | None = None,
        language: str = "en",
        emotion: str | None = None,
        speed: float = 1.0,
        pitch: float = 1.0,
        fps: int = 24,
        width: int = 640,
        height: int = 480,
        quality: str = "high",
        seed: int | None = None,
        audio_path: str | None = None,
        output_path: str | None = None,
        render_video: bool = True,
    ) -> dict[str, Any]:
        """Produce a narrated talking-avatar video for ``profile_id``.

        When ``audio_path`` is given the narration is used as-is (no TTS);
        otherwise the AI Voice Studio synthesizes it. Returns a JSON-safe
        dict with the final ``output_path``, the audio path, the per-frame
        timeline and pipeline metadata.
        """
        profile = self._resolve_profile(profile_id)
        descriptor = get_avatar_engine().generate_avatar(
            profile, quality=quality, fps=fps, seed=seed,
        )
        colors = self._extract_colors(descriptor, profile)

        # 1) Narration audio (Voice Studio) — or a caller-provided file.
        tts_engine: str | None = None
        if audio_path is None:
            from modules.ai_video_studio.ai_voice_studio import get_voice_engine

            synth = await get_voice_engine().synthesize_async(
                text,
                voice_id=voice_id or profile.voice or "default",
                language=language,
                emotion=emotion,
                speed=speed,
                pitch=pitch,
            )
            audio_path = synth["output_path"]
            duration = float(synth["duration"])
            tts_engine = synth.get("engine")
        else:
            from modules.ai_video_studio.media import dsp

            samples, sr = dsp.read_audio(audio_path)
            duration = max(0.5, len(samples) / sr)

        # 2) Lip-sync timeline timed against the narration audio.
        from modules.ai_video_studio.ai_lip_sync import get_lip_sync_engine

        lips = get_lip_sync_engine().generate(
            text, audio_path=audio_path, fps=fps, render_video=False,
        )
        facial = lips.get("facial") or lips.get("timeline") or []

        # 3) Per-frame avatar facial parameters (visemes + emotion + blinks).
        emotion_facial: dict[str, float] = {}
        if emotion:
            from modules.ai_video_studio.ai_avatar_engine.emotions import get_emotion_engine

            try:
                emotion_facial = get_emotion_engine().get(emotion).to_dict().get("facial", {})
            except KeyError:  # unknown emotion → speak with neutral face
                emotion_facial = {}

        facial_engine = get_facial_engine()
        frames = [facial_engine.compose(**compose_facial(f, emotion_facial)) for f in facial]

        # 4) Render the talking head and mux the narration.
        result: dict[str, Any] = {
            "status": "ok",
            "profile_id": profile_id,
            "text": text,
            "text_length": len(text),
            "voice_id": voice_id or profile.voice or "default",
            "language": language,
            "emotion": emotion,
            "fps": fps,
            "resolution": f"{width}x{height}",
            "duration": round(duration, 3),
            "frames": len(frames),
            "phonemes": lips.get("phonemes", 0),
            "audio_path": audio_path,
            "tts_engine": tts_engine,
            "muxed": False,
            "colors": colors,
        }

        out_dir = Path(output_path).resolve().parent if output_path else self._out_dir()
        out_dir.mkdir(parents=True, exist_ok=True)

        if render_video:
            from modules.ai_video_studio.media.output_paths import unique_filename
            from modules.ai_video_studio.media.video import ffmpeg_available, frames_to_video

            rendered = render_frames(frames, colors=colors, width=width, height=height)
            working = unique_filename(out_dir, "speaking_avatar", "mp4")
            encoded = frames_to_video(rendered, working, fps=fps)
            result["video_path"] = encoded["output_path"]

            final_path = encoded["output_path"]
            if audio_path and ffmpeg_available() and encoded["output_path"].lower().endswith((".mp4", ".mov")):
                from modules.ai_video_studio.render_engine import RenderEngine

                # Honor an explicit output_path; otherwise pick a fresh name.
                target = (
                    str(Path(output_path).resolve()) if output_path
                    else str(unique_filename(out_dir, "speaking_avatar", "mp4"))
                )
                Path(target).parent.mkdir(parents=True, exist_ok=True)
                try:
                    await RenderEngine().mux_audio(encoded["output_path"], audio_path, target)
                    final_path = target
                    result["muxed"] = True
                except Exception as e:  # noqa: BLE001 — narration is non-fatal
                    logger.warning("audio mux failed for %s: %s", profile_id, e)
            elif output_path:
                # No mux possible (GIF fallback / no ffmpeg): honor the exact path.
                target = str(Path(output_path).resolve())
                Path(target).parent.mkdir(parents=True, exist_ok=True)
                if Path(encoded["output_path"]).suffix == Path(target).suffix:
                    shutil.copyfile(encoded["output_path"], target)
                    final_path = target

            result["output_path"] = final_path
            p = Path(final_path)
            result["output_bytes"] = p.stat().st_size if p.exists() else 0
        else:
            result["video_path"] = None
            result["output_path"] = None

        # 5) Persist the per-frame avatar timeline for animators.
        from modules.ai_video_studio.media.output_paths import unique_filename

        timeline_path = unique_filename(out_dir, "speaking_timeline", "json")
        timeline_path.write_text(
            json.dumps(
                {"profile": profile_id, "fps": fps, "duration": result["duration"],
                 "frames": frames},
                indent=2,
            ),
            encoding="utf-8",
        )
        result["timeline_path"] = str(timeline_path)
        return result

    # ── helpers ──────────────────────────────────────────────────
    @staticmethod
    def _out_dir() -> Path:
        from modules.ai_video_studio.media.output_paths import get_subsystem_dir

        return get_subsystem_dir("avatars")

    @staticmethod
    def _resolve_profile(profile_id: str) -> AvatarProfile:
        """Find a profile in the avatar library first, then the registry."""
        from modules.ai_video_studio.ai_avatar_engine.library import get_avatar_library

        try:
            return get_avatar_library().get(profile_id)
        except KeyError:
            pass
        try:
            return get_avatar_engine().get_profile(profile_id)
        except (KeyError, ValueError):
            raise KeyError(f"unknown avatar profile '{profile_id}'") from None

    @staticmethod
    def _extract_colors(descriptor: dict[str, Any], profile: AvatarProfile) -> dict[str, str]:
        """Pull skin/hair/eye/shirt colors from a digital-human descriptor."""
        skin = descriptor.get("skin") or {}
        hair = descriptor.get("hair") or {}
        eyes = descriptor.get("eyes") or {}
        clothing = descriptor.get("clothing") or {}
        return {
            "skin": skin.get("hex") or profile.skin_tone,
            "hair": hair.get("color") or profile.hair_color,
            "eye": eyes.get("iris_color") or profile.eye_color,
            "shirt": clothing.get("color") or "#243447",
        }


_speaking_engine: SpeakingAvatarEngine | None = None


def get_speaking_engine() -> SpeakingAvatarEngine:
    """Return the shared speaking-avatar engine singleton."""
    global _speaking_engine
    if _speaking_engine is None:
        _speaking_engine = SpeakingAvatarEngine()
    return _speaking_engine
