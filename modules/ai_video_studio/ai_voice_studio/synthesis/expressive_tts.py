"""Expressive TTS — markup-driven prosody.

Text can embed tags that change voice behaviour mid-sentence::

    "Hello [emotion:happy] this is great news [pause:0.5] isn't it?"

Supported tags: ``[emotion:...]``, ``[pause:seconds]``, ``[rate:1.1]``,
``[pitch:1.05]``. Segments are synthesized with their own prosody and
concatenated into a single real audio file.
"""
from __future__ import annotations

import re
from typing import Any

from modules.ai_video_studio.ai_voice_studio.synthesis.tts_engine import get_tts_engine
from modules.ai_video_studio.ai_voice_studio.synthesis.emotion_controller import emotion_prosody
from modules.ai_video_studio.media import dsp

_TAG_RE = re.compile(r"\[(emotion|pause|rate|pitch):([^\]]+)\]")


def split_expressive(text: str) -> list[dict[str, Any]]:
    """Split text into ``{text, emotion, pause_after, rate, pitch}`` segments."""
    segments: list[dict[str, Any]] = []
    current: dict[str, Any] = {"text": "", "emotion": None, "rate": 1.0, "pitch": 1.0, "pause_after": 0.0}
    pos = 0
    for m in _TAG_RE.finditer(text):
        current["text"] += text[pos:m.start()]
        tag, value = m.group(1), m.group(2)
        if tag == "emotion":
            current["emotion"] = value.strip()
            prosody = emotion_prosody(value.strip())
            current["rate"] *= prosody["rate"]
            current["pitch"] *= prosody["pitch"]
        elif tag == "pause":
            current["pause_after"] = max(0.0, float(value))
        elif tag == "rate":
            current["rate"] *= float(value)
        elif tag == "pitch":
            current["pitch"] *= float(value)
        pos = m.end()
    current["text"] += text[pos:]
    if current["text"].strip():
        segments.append(current)
    return segments


def render_expressive(text: str, *, voice_id: str = "default", language: str = "en",
                      output_path: str | None = None) -> dict[str, Any]:
    """Synthesize an expressive text to one real audio file (sync bridge)."""
    import asyncio
    import concurrent.futures

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(render_expressive_async(
            text, voice_id=voice_id, language=language, output_path=output_path))
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, render_expressive_async(
            text, voice_id=voice_id, language=language, output_path=output_path)).result()


async def render_expressive_async(text: str, *, voice_id: str = "default", language: str = "en",
                                  output_path: str | None = None) -> dict[str, Any]:
    segments = split_expressive(text)
    if not segments:
        return {"output_path": "", "duration": 0.0, "engine": "none", "segments": 0}

    tts = get_tts_engine()
    parts: list[dict[str, Any]] = []
    total = 0.0
    for seg in segments:
        pause = seg.pop("pause_after", 0.0)
        seg_text = seg.pop("text", "")
        if not seg_text.strip():
            total += pause
            continue
        result = await tts.synthesize(
            seg_text, voice_id=voice_id, language=language,
            speed=float(seg.get("rate", 1.0)), pitch=float(seg.get("pitch", 1.0)),
        )
        if pause > 0:
            result["_pause"] = pause
        parts.append(result)
        total += result["duration"] + pause

    # Concatenate the segment files into one WAV.
    if output_path is None:
        from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename

        output_path = str(unique_filename(get_subsystem_dir("voice"), "voice_expressive", "wav"))
    buffers: list = []
    for part in parts:
        data, sr = dsp.read_audio(part["output_path"])
        pause = float(part.get("_pause", 0.0))
        if pause:
            data = dsp.concatenate([data, dsp.silence(pause, sample_rate=sr)], sample_rate=sr)
        buffers.append(data)
    combined = dsp.concatenate(buffers, sample_rate=44100) if buffers else dsp.silence(0.5)
    dsp.write_audio(output_path, combined)
    return {
        "output_path": output_path,
        "duration": round(len(combined) / 44100, 3),
        "engine": "expressive",
        "segments": len(parts),
    }
