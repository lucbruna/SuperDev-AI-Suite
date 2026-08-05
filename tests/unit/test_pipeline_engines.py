"""Unit tests for the pipeline engines (Volume 4) — dubbing & lip sync.

Both produce real MP4 files. Dubbing uses ``use_llm=False`` and a mocked
voice engine so tests never hit the network or Ollama.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from modules.ai_video_studio.media import dsp
from modules.ai_video_studio.media.video import ffmpeg_available

_FFMPEG = pytest.mark.skipif(not ffmpeg_available(), reason="ffmpeg not installed")


# ── Lip sync ─────────────────────────────────────────────────────────


def test_lip_sync_timeline_deterministic() -> None:
    from modules.ai_video_studio.ai_lip_sync import get_lip_sync_engine

    engine = get_lip_sync_engine()
    a = engine.generate("Hello world", duration=1.5, render_video=False)
    b = engine.generate("Hello world", duration=1.5, render_video=False)
    assert a["timeline"] == b["timeline"]
    assert a["frames"] == b["frames"]
    assert a["facial"], "facial timeline must be populated"


def test_lip_sync_phoneme_mapping() -> None:
    from modules.ai_video_studio.ai_lip_sync.phoneme_mapper import map_text_to_phonemes

    phonemes = map_text_to_phonemes("hello", duration=1.0)
    assert phonemes
    assert all("start" in p and "end" in p and "phoneme" in p for p in phonemes)


@_FFMPEG
def test_lip_sync_renders_mp4(tmp_path) -> None:
    from modules.ai_video_studio.ai_lip_sync import get_lip_sync_engine

    out_dir = str(tmp_path)
    result = get_lip_sync_engine().generate(
        "The mouth animation is rendered to a real video file.",
        duration=1.0, fps=10, output_dir=out_dir,
    )
    assert result["output_bytes"] > 100
    assert Path(result["output_path"]).exists()


# ── Dubbing ──────────────────────────────────────────────────────────


@pytest.fixture
def fake_voice_engine(monkeypatch, tmp_path):
    """Offline voice engine: writes real audio, never touches the network."""
    from modules.ai_video_studio.ai_voice_studio.synthesis.offline_tts import formant_synth

    class _Fake:
        async def synthesize_async(
            self, text, *, voice_id="default", language="en", emotion=None,
            speed=1.0, pitch=1.0, output_path=None, use_cache=True,
        ):
            out = output_path or str(tmp_path / f"line_{abs(hash(text)) % 1000}.mp3")
            samples = formant_synth(text, rate=max(0.5, speed))
            samples = dsp.normalize_peak(samples, 0.9)
            dsp.write_audio(out, samples)
            return {
                "output_path": out,
                "duration": round(len(samples) / dsp.SAMPLE_RATE, 3),
                "engine": "formant",
                "voice_id": voice_id,
                "language": language,
            }

    monkeypatch.setattr(
        "modules.ai_video_studio.ai_voice_studio.voice_engine.VoiceEngine.synthesize_async",
        _Fake.synthesize_async,
    )
    return _Fake()


@pytest.fixture
def small_video(tmp_path):
    """A 2s solid-color MP4 to dub (requires ffmpeg)."""
    out = tmp_path / "src.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=navy:s=160x90:d=2",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out)],
        capture_output=True, text=True, timeout=120, check=True,
    )
    return str(out)


@_FFMPEG
def test_dubbing_pipeline_muxes(fake_voice_engine, small_video, tmp_path) -> None:
    from modules.ai_video_studio.ai_dubbing import get_dubbing_engine

    out = str(tmp_path / "dubbed.mp4")
    result = get_dubbing_engine().dub(
        small_video,
        "pt",
        source_transcript="Hello world. This is a dubbing test.",
        source_language="en",
        use_llm=False,
        output_path=out,
    )
    assert Path(out).exists()
    assert result["muxed"] is True
    assert result["lines"] >= 2
    assert result["translation"]["engine"] == "fallback"


@_FFMPEG
def test_dubbing_missing_video_raises(fake_voice_engine, tmp_path) -> None:
    from modules.ai_video_studio.core.exceptions import ValidationError
    from modules.ai_video_studio.ai_dubbing import get_dubbing_engine

    with pytest.raises(ValidationError):
        get_dubbing_engine().dub(
            str(tmp_path / "missing.mp4"), "pt",
            source_transcript="hello", use_llm=False,
        )


# ── Helpers used by the pipeline ─────────────────────────────────────


def test_sentence_alignment_simple() -> None:
    from modules.ai_video_studio.ai_dubbing.sentence_alignment import align_sentences

    slots = [{"start": 0.0, "end": 1.0, "text": "Hello."},
             {"start": 1.2, "end": 2.2, "text": "World."}]
    translated = ["Olá.", "Mundo."]
    layout = align_sentences(slots, translated)
    assert len(layout) == 2
    assert layout[0]["text"] == "Olá."


def test_timeline_timestamp_format() -> None:
    from modules.ai_video_studio.ai_subtitles.subtitle_timeline import to_timestamp

    assert to_timestamp(0.0, sep=",") == "00:00:00,000"
    assert to_timestamp(3661.5, sep=",") == "01:01:01,500"
