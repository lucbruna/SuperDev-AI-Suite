"""Unit tests for the AI audio engines (Volume 4) — fallbacks & determinism.

Voice studio, voice clone, translation and subtitles all have layered
fallbacks that must never raise, and deterministic outputs when the
network/AI providers are unavailable.
"""
from __future__ import annotations

import numpy as np
import pytest

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.media import dsp


# ── Voice studio ─────────────────────────────────────────────────────


def test_voice_catalog_nonempty() -> None:
    from modules.ai_video_studio.ai_voice_studio import get_voice_engine

    voices = get_voice_engine().list_voices()
    assert len(voices) >= 30
    assert all("id" in v and "language" in v for v in voices)


def test_offline_formant_deterministic() -> None:
    from modules.ai_video_studio.ai_voice_studio.synthesis.offline_tts import formant_synth

    a = formant_synth("hello world", rate=1.0)
    b = formant_synth("hello world", rate=1.0)
    assert np.array_equal(a, b)
    assert dsp.peak(a) > 0.0


def test_offline_tts_writes_file(tmp_path) -> None:
    from modules.ai_video_studio.ai_voice_studio.synthesis.offline_tts import OfflineTTS

    out = str(tmp_path / "offline.wav")
    result = OfflineTTS().synthesize("testing one two three", output_path=out)
    assert (tmp_path / "offline.wav").exists()
    assert result["engine"] in ("pyttsx3", "formant")
    assert result["duration"] > 0


def test_tts_chain_falls_back_when_network_down(monkeypatch, tmp_path) -> None:
    """When VoiceStudioService fails, the chain must fall back to offline."""
    from modules.ai_video_studio.ai_voice_studio.synthesis import tts_engine

    async def _boom(self, *args, **kwargs):
        raise RuntimeError("network unavailable")

    monkeypatch.setattr(
        "modules.ai_video_studio.services.voice_studio.VoiceStudioService.synthesize",
        _boom,
    )
    engine = tts_engine.TTSEngine()
    out = str(tmp_path / "fallback.wav")
    import asyncio

    result = asyncio.run(engine.synthesize("hello world", output_path=out))
    assert result["engine"] in ("pyttsx3", "formant")
    assert (tmp_path / "fallback.wav").exists()


# ── Voice clone ──────────────────────────────────────────────────────


@pytest.fixture
def speech_sample(tmp_path):
    """A real speech-like WAV that passes clone quality checks."""
    from modules.ai_video_studio.ai_voice_studio.synthesis.offline_tts import formant_synth

    samples = formant_synth("this is a reference voice sample for cloning and testing purposes")
    # extend to > 2s so validate_sample duration passes
    while len(samples) < int(2.5 * dsp.SAMPLE_RATE):
        samples = np.concatenate([samples, formant_synth("and more voice content for the sample", rate=1.0)])
    samples = dsp.normalize_peak(samples, 0.9)
    path = tmp_path / "ref.wav"
    dsp.write_audio(str(path), samples)
    return str(path)


class _FakeVoiceEngine:
    """Offline stand-in for the voice engine used inside clone()."""

    def synthesize(self, text, *, voice_id="default", language="en", speed=1.0,
                   pitch=1.0, output_path=None, use_cache=True, **kwargs):
        out = output_path or self._path
        dsp.write_audio(out, dsp.sine(220.0, max(0.5, len(text) / 15.0)) * 0.5)
        return {"output_path": out, "engine": "formant"}


def test_clone_roundtrip(monkeypatch, speech_sample, tmp_path) -> None:
    from modules.ai_video_studio.ai_voice_clone import get_clone_engine
    from modules.ai_video_studio.ai_voice_clone.quality_validator import validate_sample

    report = validate_sample(speech_sample)
    assert report["passed"], f"reference sample rejected: {report['checks']}"

    fake = _FakeVoiceEngine()
    fake._path = str(tmp_path / "base.wav")
    monkeypatch.setattr("modules.ai_video_studio.ai_voice_studio.get_voice_engine", lambda: fake)

    engine = get_clone_engine()
    profile = engine.create_profile([speech_sample], clone_id="pytest_clone")
    assert profile["clone_id"] == "pytest_clone"
    assert profile["analysis"]["f0_mean"] > 0

    out = str(tmp_path / "cloned.wav")
    result = engine.clone("the clone speaks this line", "pytest_clone", output_path=out)
    assert (tmp_path / "cloned.wav").exists()
    assert result["bytes"] > 1000

    assert engine.delete_clone("pytest_clone") is True


def test_clone_rejects_traversal(monkeypatch, speech_sample, tmp_path) -> None:
    from modules.ai_video_studio.ai_voice_clone import get_clone_engine

    fake = _FakeVoiceEngine()
    fake._path = str(tmp_path / "base.wav")
    monkeypatch.setattr("modules.ai_video_studio.ai_voice_studio.get_voice_engine", lambda: fake)
    engine = get_clone_engine()
    with pytest.raises(ValidationError):
        engine.clone("x", "../escape")


# ── Translation ──────────────────────────────────────────────────────


def test_translate_fallback_deterministic() -> None:
    from modules.ai_video_studio.ai_translation import get_translation_engine

    engine = get_translation_engine()
    a = engine.translate("Hello, welcome to the studio.", "pt", source="en", use_llm=False)
    b = engine.translate("Hello, welcome to the studio.", "pt", source="en", use_llm=False)
    assert a["engine"] == "fallback"
    assert a["text"] == b["text"]  # deterministic


def test_translate_phrasebook_en_pt() -> None:
    from modules.ai_video_studio.ai_translation import get_translation_engine

    result = get_translation_engine().translate("Hello", "pt", source="en", use_llm=False)
    assert result["engine"] == "fallback"
    assert "olá" in result["text"].lower()


def test_translate_empty_raises() -> None:
    from modules.ai_video_studio.ai_translation import get_translation_engine

    with pytest.raises(ValidationError):
        get_translation_engine().translate("", "pt")


def test_detect_language() -> None:
    from modules.ai_video_studio.ai_translation import detect_language

    assert detect_language("the quick brown fox and the dog") == "en"
    assert detect_language("olá como vai o amigo") == "pt"
    assert detect_language("") == ""


# ── Subtitles ────────────────────────────────────────────────────────


@pytest.mark.parametrize("fmt", ["srt", "vtt", "ass"])
def test_subtitle_formats_generate(fmt, tmp_path) -> None:
    from modules.ai_video_studio.ai_subtitles import get_subtitle_engine

    out = str(tmp_path / f"subs.{fmt}")
    result = get_subtitle_engine().generate(
        "This is the first subtitle line. And here is the second one.",
        format=fmt,
        output_path=out,
    )
    assert (tmp_path / f"subs.{fmt}").exists()
    assert result["cues"] >= 2
    assert result["bytes"] > 50


def test_subtitle_deterministic() -> None:
    from modules.ai_video_studio.ai_subtitles import get_subtitle_engine

    engine = get_subtitle_engine()
    a = engine.generate("Same text every time for determinism checking.")
    b = engine.generate("Same text every time for determinism checking.")
    assert a["cues"] == b["cues"]
    with open(a["file_path"], "rb") as fa, open(b["file_path"], "rb") as fb:
        assert fa.read() == fb.read()


def test_subtitle_unsupported_format_raises() -> None:
    from modules.ai_video_studio.ai_subtitles import get_subtitle_engine

    with pytest.raises(ValidationError):
        get_subtitle_engine().generate("text", format="txt")


def test_subtitle_requires_text_or_media() -> None:
    from modules.ai_video_studio.ai_subtitles import get_subtitle_engine

    with pytest.raises(ValidationError):
        get_subtitle_engine().generate()


def test_vad_transcribe_falls_back(tmp_path) -> None:
    """Without whisper installed, transcription must fall back to VAD."""
    from modules.ai_video_studio.ai_subtitles.speech_recognition import transcribe

    # Speech-like audio: tone bursts with silence gaps.
    burst = dsp.sine(220.0, 1.0) * 0.5
    audio = np.concatenate([burst, dsp.silence(0.8), burst, dsp.silence(0.8)])
    wav = tmp_path / "speech.wav"
    dsp.write_audio(str(wav), audio)
    result = transcribe(str(wav))
    assert result["engine"] in ("faster-whisper", "vad")
    assert isinstance(result["segments"], list)
