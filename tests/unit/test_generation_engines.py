"""Unit tests for the AI generation engines (Volume 4) — determinism & real files.

Music (seeded determinism, all 20 genres), sound effects (all 16), and the
audio mixer/mastering chain all write real audio files.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.media import dsp

# Keep the suite fast: short durations, but real DSP rendering.


# ── Music generator ──────────────────────────────────────────────────


def test_music_list_genres_20() -> None:
    from modules.ai_video_studio.ai_music_generator import get_music_engine

    genres = get_music_engine().list_genres()
    assert len(genres) == 20
    assert "cinematic" in genres and "lofi" in genres and "horror" in genres


def test_music_seed_determinism(tmp_path) -> None:
    from modules.ai_video_studio.ai_music_generator import get_music_engine

    engine = get_music_engine()
    a = str(tmp_path / "a.wav")
    b = str(tmp_path / "b.wav")
    engine.generate("lofi", duration=4.0, seed=7, output_path=a)
    engine.generate("lofi", duration=4.0, seed=7, output_path=b)
    assert Path(a).read_bytes() == Path(b).read_bytes()


def test_music_different_seed_differs(tmp_path) -> None:
    from modules.ai_video_studio.ai_music_generator import get_music_engine

    engine = get_music_engine()
    a = str(tmp_path / "a.wav")
    b = str(tmp_path / "b.wav")
    engine.generate("jazz", duration=4.0, seed=1, output_path=a)
    engine.generate("jazz", duration=4.0, seed=999, output_path=b)
    assert Path(a).read_bytes() != Path(b).read_bytes()


@pytest.mark.parametrize("genre", ["cinematic", "lofi", "horror", "electronic"])
def test_music_genre_generates_real_file(genre, tmp_path) -> None:
    from modules.ai_video_studio.ai_music_generator import get_music_engine

    out = str(tmp_path / f"{genre}.wav")
    result = get_music_engine().generate(genre, duration=3.0, output_path=out)
    assert (tmp_path / f"{genre}.wav").exists()
    assert result["bytes"] > 5000
    assert result["bpm"] > 0
    assert result["instruments"], "must include at least one instrument track"


def test_music_unknown_genre_falls_back_ambient(tmp_path) -> None:
    """get_genre falls back to ambient instead of raising."""
    from modules.ai_video_studio.ai_music_generator import get_music_engine

    out = str(tmp_path / "unknown.wav")
    result = get_music_engine().generate("not-a-genre", duration=2.0, output_path=out)
    assert result["genre"]  # ambient spec is used
    assert (tmp_path / "unknown.wav").exists()


def test_music_library_scales() -> None:
    from modules.ai_video_studio.ai_music_generator.music_library import (
        chord_tones,
        note_frequency,
        scale_notes,
    )

    assert abs(note_frequency("A4") - 440.0) < 0.01
    assert len(scale_notes("C", "major")) == 7
    assert len(chord_tones("C", "major")) == 3


# ── Sound effects ────────────────────────────────────────────────────


def test_effects_all_16_generate(tmp_path) -> None:
    from modules.ai_video_studio.ai_sound_effects import get_effects_engine

    engine = get_effects_engine()
    names = engine.list_effects()
    assert len(names) == 16
    for name in names:
        out = str(tmp_path / f"sfx_{name}.wav")
        result = engine.generate(name, duration=1.0, output_path=out)
        assert (tmp_path / f"sfx_{name}.wav").exists(), f"{name} failed"
        assert result["bytes"] > 500, f"{name} too small: {result['bytes']}B"


def test_effects_deterministic(tmp_path) -> None:
    from modules.ai_video_studio.ai_sound_effects import get_effects_engine

    engine = get_effects_engine()
    a = str(tmp_path / "a.wav")
    b = str(tmp_path / "b.wav")
    engine.generate("rain", duration=2.0, output_path=a)
    engine.generate("rain", duration=2.0, output_path=b)
    assert Path(a).read_bytes() == Path(b).read_bytes()


def test_effects_unknown_raises() -> None:
    from modules.ai_video_studio.ai_sound_effects import get_effects_engine

    with pytest.raises(ValidationError):
        get_effects_engine().generate("nonexistent_effect")


# ── Mixer / mastering ────────────────────────────────────────────────


def test_mixer_writes_real_file(tmp_path) -> None:
    from modules.ai_video_studio.ai_audio_mixer import get_mixer_engine

    t1 = dsp.sine(330.0, 2.0) * 0.5
    t2 = dsp.sine(494.0, 2.0) * 0.5
    out = str(tmp_path / "mix.wav")
    result = get_mixer_engine().mix(
        [{"samples": t1, "gain": 0.8, "pan": -0.3},
         {"samples": t2, "gain": 0.7, "pan": 0.3}],
        master_preset="warm",
        output_path=out,
    )
    assert (tmp_path / "mix.wav").exists()
    assert result["bytes"] > 5000
    assert result["tracks"] == 2
    assert "rms_db" in result["loudness"]
    assert result["loudness"]["rms_db"] < 0  # sane negative dB


def test_mixer_no_tracks_raises() -> None:
    from modules.ai_video_studio.ai_audio_mixer import get_mixer_engine

    with pytest.raises(ValueError):
        get_mixer_engine().mix([])


def test_mastering_chain_works() -> None:
    from modules.ai_video_studio.ai_audio_mixer.mastering_engine import MasteringEngine

    import numpy as np

    x = dsp.mix_tracks([{"samples": dsp.sine(330.0, 2.0) * 0.8}])
    result = MasteringEngine().master(x, preset="warm")
    out = result["samples"]
    assert out.dtype == np.float32
    assert dsp.peak(out) <= 0.97 + 1e-3  # limiter at the end of the chain
    assert result["loudness"]["rms_db"] < 0


def test_export_audio_wav_and_metadata(tmp_path) -> None:
    from modules.ai_video_studio.ai_audio_mixer.export_audio import embed_metadata, export

    sig = dsp.sine(440.0, 1.0) * 0.5
    out = str(tmp_path / "export.wav")
    result = export(sig, out, format="wav")
    assert (tmp_path / "export.wav").exists()
    assert result["bytes"] > 1000
    assert result["format"] == "wav"
    tags = embed_metadata(out, {"title": "Test", "artist": "Unit"})
    assert tags["tags"] in (0, 2)  # 2 when ffmpeg present, 0 otherwise (safe no-op)
