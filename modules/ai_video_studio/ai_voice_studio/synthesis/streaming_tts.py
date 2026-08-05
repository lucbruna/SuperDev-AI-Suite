"""Streaming TTS — chunked synthesis for long text.

Splits long text into sentences, synthesizes them in order (reporting
progress), and returns both the combined file and per-sentence segments —
useful for dubbing alignment and subtitle timing.
"""
from __future__ import annotations

import re
from typing import Any

from modules.ai_video_studio.ai_voice_studio.synthesis.tts_engine import get_tts_engine
from modules.ai_video_studio.media import dsp

_SENTENCE_RE = re.compile(r"[^.!?…]+[.!?…]*")


def split_sentences(text: str, max_chars: int = 400) -> list[str]:
    """Split into sentences, further splitting any sentence over max_chars."""
    sentences = [s.strip() for s in _SENTENCE_RE.findall(text) if s.strip()]
    out: list[str] = []
    for s in sentences:
        while len(s) > max_chars:
            cut = s.rfind(" ", 0, max_chars)
            if cut < 1:
                cut = max_chars
            out.append(s[:cut].strip())
            s = s[cut:].strip()
        if s:
            out.append(s)
    return out


async def synthesize_stream(
    text: str,
    *,
    voice_id: str = "default",
    language: str = "en",
    speed: float = 1.0,
    pitch: float = 1.0,
    output_path: str | None = None,
    progress: Any = None,
) -> dict[str, Any]:
    """Synthesize sentence by sentence, returning segments + combined file."""
    sentences = split_sentences(text)
    if not sentences:
        return {"output_path": "", "duration": 0.0, "engine": "none", "segments": []}

    tts = get_tts_engine()
    segments: list[dict[str, Any]] = []
    buffers: list = []
    cursor = 0.0
    for i, sentence in enumerate(sentences):
        result = await tts.synthesize(
            sentence, voice_id=voice_id, language=language, speed=speed, pitch=pitch,
        )
        segments.append({
            "text": sentence,
            "start": round(cursor, 3),
            "end": round(cursor + result["duration"], 3),
            "engine": result["engine"],
        })
        buffers.append(dsp.read_audio(result["output_path"])[0])
        cursor += result["duration"]
        if progress is not None:
            progress({"index": i + 1, "total": len(sentences)})

    combined = dsp.concatenate(buffers, sample_rate=44100) if buffers else dsp.silence(0.5)
    if output_path is None:
        from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename

        output_path = str(unique_filename(get_subsystem_dir("voice"), "voice_stream", "wav"))
    dsp.write_audio(output_path, combined)
    return {
        "output_path": output_path,
        "duration": round(len(combined) / 44100, 3),
        "engine": "stream",
        "segments": segments,
    }
