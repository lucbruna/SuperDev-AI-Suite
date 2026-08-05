"""Unit tests for the media DSP toolkit (Volume 4) — determinism & correctness.

Covers: oscillators, seeded noise, filters, envelopes, the brickwall
lookahead limiter, analysis (f0/loudness), pitch shift, and file I/O.
"""
from __future__ import annotations

import numpy as np
import pytest

from modules.ai_video_studio.media import dsp

SR = dsp.SAMPLE_RATE


# ── Oscillators ──────────────────────────────────────────────────────


def test_sine_length_and_range() -> None:
    sig = dsp.sine(440.0, 0.5)
    assert len(sig) == int(0.5 * SR)
    assert sig.dtype == np.float32
    assert sig.min() >= -1.0 and sig.max() <= 1.0
    assert abs(dsp.peak(sig) - 1.0) < 1e-3


def test_oscillators_deterministic() -> None:
    for fn in (dsp.sine, dsp.saw, dsp.square, dsp.triangle):
        a = fn(220.0, 0.3)
        b = fn(220.0, 0.3)
        assert np.array_equal(a, b)


def test_square_duty_cycle() -> None:
    sig = dsp.square(10.0, 0.2, duty=0.5)
    assert np.all(np.abs(sig) == 1.0)  # bipolar square wave


# ── Noise (seeded determinism) ───────────────────────────────────────


@pytest.mark.parametrize("fn", [dsp.noise_white, dsp.noise_pink, dsp.noise_brown])
def test_noise_deterministic_same_seed(fn) -> None:
    a = fn(1.0, seed=42)
    b = fn(1.0, seed=42)
    assert np.array_equal(a, b)


def test_noise_different_seed_differs() -> None:
    a = dsp.noise_white(1.0, seed=1)
    b = dsp.noise_white(1.0, seed=2)
    assert not np.array_equal(a, b)


def test_noise_length_exact() -> None:
    # Callers rely on len() == round(sr * duration) — float truncation bug.
    n = int(SR * 0.27)
    assert len(dsp.noise_white(0.27)) == n
    assert len(dsp.noise_pink(0.27)) == n


def test_noise_bounded() -> None:
    assert dsp.peak(dsp.noise_white(0.5)) <= 1.0
    assert dsp.peak(dsp.noise_pink(0.5)) <= 1.0


# ── Envelopes ────────────────────────────────────────────────────────


def test_adsr_short_signal_robust() -> None:
    # Must not crash or produce NaN for tiny buffers.
    env = dsp.adsr(10)
    assert len(env) == 10
    assert np.all(np.isfinite(env))
    assert env[0] == 0.0  # starts at silence


def test_adsr_endpoints() -> None:
    env = dsp.adsr(SR)
    assert env[0] == 0.0
    assert np.all(env >= 0.0)


# ── Filters ──────────────────────────────────────────────────────────


def test_one_pole_lp_smooths() -> None:
    x = np.concatenate([np.zeros(100, dtype=np.float32), np.ones(100, dtype=np.float32)])
    y = dsp.one_pole_lp(x, 500.0)
    # Output is a smooth step — no oscillation, still rises.
    assert np.all(np.isfinite(y))
    assert y.max() > 0.5
    assert y[-1] > y[0]


def test_biquad_finite() -> None:
    x = dsp.noise_white(0.5, seed=3)
    y = dsp.biquad_peak(x, 1000.0, 1.0, 6.0)
    assert np.all(np.isfinite(y))
    z = dsp.biquad_lowshelf(x, 200.0, 3.0)
    assert np.all(np.isfinite(z))


def test_comb_allpass_stable() -> None:
    x = dsp.noise_white(0.5, seed=5)
    for fn in (dsp.comb, dsp.allpass):
        y = fn(x, 0.01, 0.4)
        assert len(y) == len(x)
        assert np.all(np.isfinite(y))
        assert dsp.peak(y) < 2.0  # no runaway feedback


# ── Limiter (lookahead brickwall) ────────────────────────────────────


def test_limiter_below_threshold_untouched() -> None:
    sig = dsp.sine(440.0, 1.0) * 0.5
    out = dsp.limiter(sig, 0.97)
    assert abs(dsp.peak(out) - 0.5) < 0.01  # gain stays ~1.0


def test_limiter_clamps_above_threshold() -> None:
    sig = np.full(SR, 0.05, dtype=np.float32)
    sig[1000:6000] = 2.0  # hot transient
    out = dsp.limiter(sig, 0.97)
    assert dsp.peak(out) <= 0.97 + 1e-3


def test_limiter_never_amplifies_silence_tail() -> None:
    sig = np.zeros(SR * 2, dtype=np.float32)
    sig[1000:5000] = 2.0
    out = dsp.limiter(sig, 0.97)
    tail = out[SR:]
    assert dsp.rms(tail) < 1e-3  # the old bug amplified this to ~96e6


def test_limiter_deterministic() -> None:
    sig = dsp.noise_white(0.5, seed=9) * 1.5
    assert np.array_equal(dsp.limiter(sig, 0.9), dsp.limiter(sig, 0.9))


def test_spectral_gate_preserves_tone() -> None:
    tone = dsp.sine(440.0, 1.0) * 0.4
    cleaned = dsp.spectral_gate(tone, threshold=0.02)
    assert dsp.rms(cleaned) > dsp.rms(tone) * 0.5


# ── Analysis ─────────────────────────────────────────────────────────


def test_f0_autocorr_detects_sine() -> None:
    f0 = dsp.f0_autocorr(dsp.sine(220.0, 0.5))
    assert 200 < f0 < 240


def test_spectral_centroid_rolloff() -> None:
    x = dsp.sine(1000.0, 0.5)
    assert 800 < dsp.spectral_centroid(x) < 1200
    roll = dsp.spectral_rolloff(x, 0.85)
    assert roll > 0


def test_loudness_metrics() -> None:
    sig = dsp.sine(440.0, 0.5) * 0.5
    assert 0.3 < dsp.rms(sig) < 0.4  # sine rms ≈ 0.707 * peak
    assert abs(dsp.peak(sig) - 0.5) < 1e-3


def test_normalize_peak_rms() -> None:
    sig = dsp.noise_white(0.5, seed=2) * 0.3
    assert abs(dsp.peak(dsp.normalize_peak(sig, 0.9)) - 0.9) < 1e-3
    assert abs(dsp.rms(dsp.normalize_rms(sig, 0.2)) - 0.2) < 1e-3


# ── Pitch shift / resample ───────────────────────────────────────────


def test_pitch_shift_preserves_length() -> None:
    x = dsp.sine(200.0, 1.0)
    shifted = dsp.pitch_shift(x, 2.0)
    assert len(shifted) == len(x)


def test_pitch_shift_zero_is_identity() -> None:
    x = dsp.sine(200.0, 0.5)
    assert np.array_equal(dsp.pitch_shift(x, 0.0), x)


def test_resample_target_length() -> None:
    x = dsp.sine(200.0, 0.5)
    assert len(dsp.resample(x, 1000)) == 1000
    assert len(dsp.resample(x, 10)) == 10


def test_time_stretch_changes_length() -> None:
    x = dsp.sine(200.0, 0.5)
    faster = dsp.time_stretch(x, 2.0)
    assert len(faster) < len(x)


# ── Mixing / stereo ──────────────────────────────────────────────────


def test_to_stereo_pan() -> None:
    mono = dsp.sine(440.0, 0.2)
    st = dsp.to_stereo(mono, pan=-1.0)
    assert st.shape == (len(mono), 2)
    assert dsp.rms(st[:, 0]) > dsp.rms(st[:, 1])  # hard left


def test_mix_tracks_length() -> None:
    t1 = dsp.sine(330.0, 1.0)
    t2 = dsp.sine(494.0, 1.0)
    mixed = dsp.mix_tracks([{"samples": t1, "gain": 0.5}, {"samples": t2, "gain": 0.5}])
    assert len(mixed) >= len(t1)
    assert dsp.peak(mixed) <= 1.0


# ── File I/O ─────────────────────────────────────────────────────────


def test_write_read_wav_roundtrip(tmp_path) -> None:
    out = tmp_path / "tone.wav"
    sig = dsp.sine(440.0, 0.5)
    dsp.write_audio(str(out), sig)
    data, sr = dsp.read_audio(str(out))
    assert sr == SR
    assert len(data) == len(sig)
    assert abs(dsp.peak(data) - dsp.peak(sig)) < 0.01


def test_read_missing_mp3_returns_silence(tmp_path) -> None:
    # Non-wav files go through the ffmpeg path which degrades to silence.
    data, sr = dsp.read_audio(str(tmp_path / "nope.mp3"))
    assert len(data) >= 1
    assert sr > 0


def test_read_missing_wav_raises(tmp_path) -> None:
    # Stdlib wav path surfaces the missing file error.
    import pytest as _pytest

    with _pytest.raises(FileNotFoundError):
        dsp.read_audio(str(tmp_path / "nope.wav"))
