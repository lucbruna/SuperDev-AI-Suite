"""Dubbing Engine — dubs a video into another language with real audio.

Pipeline: extract audio → transcribe (whisper/VAD) → translate lines
(Ollama) → synthesize each line (AI voice studio) → align to the video
timeline → mix → mux into a new MP4. All files are real; every step has a
deterministic fallback so dubbing never fails.
"""
from __future__ import annotations

import asyncio
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename
from modules.ai_video_studio.ai_dubbing.automatic_translation import AutomaticTranslation
from modules.ai_video_studio.ai_dubbing.voice_casting import VoiceCasting
from modules.ai_video_studio.ai_dubbing.sentence_alignment import align_sentences
from modules.ai_video_studio.ai_dubbing.pause_alignment import apply_pauses
from modules.ai_video_studio.ai_dubbing.emotion_alignment import emotion_prosody_for_line
from modules.ai_video_studio.ai_dubbing.timing_optimizer import fit_to_duration
from modules.ai_video_studio.ai_dubbing.speech_alignment import place_clips
from modules.ai_video_studio.ai_dubbing.export_dubbing import export_audio_track, mux_dubbed_video, probe_duration

logger = logging.getLogger(__name__)

_DUBBING = None


def get_dubbing_engine() -> DubbingEngine:
    global _DUBBING
    if _DUBBING is None:
        _DUBBING = DubbingEngine()
    return _DUBBING


class DubbingEngine:
    """Dubs a video to a target language with real AI voices."""

    def __init__(self) -> None:
        self.translator = AutomaticTranslation()
        self.casting = VoiceCasting()

    def dub(
        self,
        video_path: str,
        target_language: str,
        *,
        source_transcript: str | None = None,
        source_language: str | None = None,
        voices: dict[str, str] | None = None,
        output_path: str | None = None,
        llm_timeout: float = 60.0,
        use_llm: bool = True,
    ) -> dict[str, Any]:
        """Dubbed video → real MP4 under ``modules/downloads/dubbing/``."""
        try:
            return asyncio.run(self.dub_async(
                video_path, target_language, source_transcript=source_transcript,
                source_language=source_language, voices=voices,
                output_path=output_path, llm_timeout=llm_timeout, use_llm=use_llm,
            ))
        except RuntimeError:
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(asyncio.run, self.dub_async(
                    video_path, target_language, source_transcript=source_transcript,
                    source_language=source_language, voices=voices,
                    output_path=output_path, llm_timeout=llm_timeout, use_llm=use_llm,
                )).result()

    async def dub_async(
        self,
        video_path: str,
        target_language: str,
        *,
        source_transcript: str | None = None,
        source_language: str | None = None,
        voices: dict[str, str] | None = None,
        output_path: str | None = None,
        llm_timeout: float = 60.0,
        use_llm: bool = True,
    ) -> dict[str, Any]:
        if not Path(video_path).exists():
            raise ValidationError(f"Video not found: {video_path}", field="video_path")

        with tempfile.TemporaryDirectory(prefix="avs_dub_") as tmp:
            tmp_dir = Path(tmp)

            # 1) Extract the original audio track.
            source_audio = tmp_dir / "source.wav"
            self._extract_audio(video_path, source_audio)

            # 2) Get source lines (transcript or transcription).
            source_slots = await self._source_lines(
                source_audio, source_transcript, source_language,
            )
            source_texts = [s["text"] for s in source_slots]
            if not source_texts:
                raise ValidationError("No dialogue detected for dubbing", field="video_path")

            # 3) Translate the lines.
            translated, translation_report = await self.translator.translate_lines_async(
                source_texts, target_language, source=source_language, use_llm=use_llm,
                provider_timeout=llm_timeout,
            )

            # 4) Align translations onto the source timing.
            layout = align_sentences(source_slots, translated)

            # 5) Synthesize each line with its actor voice.
            from modules.ai_video_studio.ai_voice_studio import get_voice_engine

            voice_engine = get_voice_engine()
            audio_paths: list[str] = []
            for i, line in enumerate(layout):
                voice = self._voice_for_line(line, voices)
                prosody = emotion_prosody_for_line(line["text"])
                clip = tmp_dir / f"line_{i:03d}.mp3"
                result = await voice_engine.synthesize_async(
                    line["text"], voice_id=voice, language=target_language,
                    emotion=prosody["emotion"],
                    speed=float(prosody["rate"]), pitch=float(prosody["pitch"]),
                    output_path=str(clip), use_cache=False,
                )
                line["audio_path"] = result["output_path"]
                line["voice"] = voice
                line["tts_engine"] = result["engine"]
                audio_paths.append(result["output_path"])

            # 6) Fit, place, mix and mux.
            video_duration = probe_duration(video_path)
            layout = fit_to_duration(apply_pauses(layout), max(video_duration, 1.0))
            tracks = place_clips(layout)

            out_dir = Path(output_path).parent if output_path else get_subsystem_dir("dubbing")
            audio_track = str(tmp_dir / "dubbed_mix.wav")
            audio_report = export_audio_track(tracks, audio_track)

            out_path = output_path or str(unique_filename(out_dir, "dubbed", "mp4"))
            mux = mux_dubbed_video(video_path, audio_track, out_path)

            return {
                "output_path": mux.get("output_path", out_path),
                "muxed": bool(mux.get("muxed")),
                "target_language": target_language,
                "lines": len(layout),
                "translation": translation_report,
                "tts_engines": sorted({l["tts_engine"] for l in layout}),
                "audio": audio_report,
                "video_duration": video_duration,
            }

    # ── Helpers ───────────────────────────────────────────────────
    def _voice_for_line(self, line: dict, voices: dict[str, str] | None) -> str:
        voices = voices or {}
        if line.get("character") and line["character"] in voices:
            return voices[line["character"]]
        return self.casting.voice_for(line.get("character", "narrator"))

    async def _source_lines(self, source_audio: Path, transcript: str | None,
                            source_language: str | None) -> list[dict[str, Any]]:
        if transcript and transcript.strip():
            from modules.ai_video_studio.ai_subtitles.speech_recognition import transcribe

            # Use the transcript as the dialogue, timed by reading speed.
            import re

            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", transcript.strip()) if s.strip()]
            segments = []
            cursor = 0.0
            for s in sentences:
                dur = max(1.0, len(s) / 15.0)
                segments.append({"start": cursor, "end": cursor + dur, "text": s})
                cursor += dur
            return segments
        result = await asyncio.to_thread(transcribe, str(source_audio), language=source_language)
        segments = result["segments"]
        if segments and not segments[0].get("text"):
            raise ValidationError(
                "No speech text available (install faster-whisper or pass source_transcript)",
                field="source_transcript",
            )
        return segments

    @staticmethod
    def _extract_audio(video_path: str, out_wav: Path) -> None:
        """Extract the video's audio track; silent bed when there is none."""
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", video_path, "-vn", "-ac", "1", "-ar", "44100", str(out_wav)],
            capture_output=True, text=True, timeout=600,
        )
        if result.returncode == 0 and out_wav.exists() and out_wav.stat().st_size > 0:
            return
        # No audio stream (or extraction failure) — lay down silence for the
        # video duration so the pipeline can still time the dub.
        from modules.ai_video_studio.media import dsp

        duration = probe_duration(video_path) or 3.0
        dsp.write_audio(out_wav, dsp.silence(duration))
