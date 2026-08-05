"""DSP toolkit — real audio primitives for the AI Voice/Audio Studio (Volume 4).

Everything here is implemented with numpy (plus scipy/soundfile when present)
and operates on float32 sample arrays in ``[-1, 1]``. It is the shared
foundation for the music generator, sound effects, audio mixer, voice clone
analysis and lip-sync subsystems, so each of those stays small and consistent.

No heavyweight ML dependencies: all algorithms are deterministic DSP.
"""
from __future__ import annotations

import math
import subprocess
import tempfile
import wave
from pathlib import Path
from typing import Any

import numpy as np

SAMPLE_RATE = 44100

# ── Oscillators ──────────────────────────────────────────────────

def sine(frequency: float, duration: float, *, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    t = np.arange(int(sample_rate * duration)) / sample_rate
    return np.sin(2 * math.pi * frequency * t).astype(np.float32)


def saw(frequency: float, duration: float, *, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    t = np.arange(int(sample_rate * duration)) / sample_rate
    phase = (frequency * t) % 1.0
    return (2.0 * phase - 1.0).astype(np.float32)


def square(frequency: float, duration: float, *, duty: float = 0.5, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    t = np.arange(int(sample_rate * duration)) / sample_rate
    phase = (frequency * t) % 1.0
    return np.where(phase < duty, 1.0, -1.0).astype(np.float32)


def triangle(frequency: float, duration: float, *, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    t = np.arange(int(sample_rate * duration)) / sample_rate
    phase = (frequency * t) % 1.0
    return (4.0 * np.abs(phase - 0.5) - 1.0).astype(np.float32)


def noise_white(duration: float, *, sample_rate: int = SAMPLE_RATE, seed: int = 0) -> np.ndarray:
    # round() (not int()) so callers that compute n = int(sample_rate * duration)
    # always get an array of exactly that length — float truncation otherwise
    # produces n-1 samples and breaks in-place additions.
    rng = np.random.default_rng(seed)
    return rng.uniform(-1.0, 1.0, max(1, round(sample_rate * duration))).astype(np.float32)


def noise_pink(duration: float, *, sample_rate: int = SAMPLE_RATE, seed: int = 0) -> np.ndarray:
    """Pink noise via Paul Kellet's economical filter (3 dB/oct rolloff)."""
    n = max(1, round(sample_rate * duration))
    rng = np.random.default_rng(seed)
    white = rng.uniform(-1.0, 1.0, n)
    b = np.zeros(7, dtype=np.float64)
    out = np.zeros(n, dtype=np.float64)
    for i in range(n):
        b[0] = 0.99886 * b[0] + white[i] * 0.0555179
        b[1] = 0.99332 * b[1] + white[i] * 0.0750759
        b[2] = 0.96900 * b[2] + white[i] * 0.1538520
        b[3] = 0.86650 * b[3] + white[i] * 0.3104856
        b[4] = 0.55000 * b[4] + white[i] * 0.5329522
        b[5] = -0.7616 * b[5] - white[i] * 0.0168980
        out[i] = b[0] + b[1] + b[2] + b[3] + b[4] + b[5] + b[6] + white[i] * 0.5362
        b[6] = white[i] * 0.115926
    return (out / np.max(np.abs(out))).astype(np.float32)


def noise_brown(duration: float, *, sample_rate: int = SAMPLE_RATE, seed: int = 0) -> np.ndarray:
    """Brown/red noise: integrated white noise (6 dB/oct rolloff)."""
    n = max(1, round(sample_rate * duration))
    rng = np.random.default_rng(seed)
    white = rng.uniform(-1.0, 1.0, n)
    out = np.cumsum(white)
    out -= np.linspace(out[0], out[-1], n)  # remove drift
    out /= np.max(np.abs(out)) + 1e-9
    return out.astype(np.float32)


# ── Envelopes ────────────────────────────────────────────────────

def adsr(n: int, *, attack: float = 0.01, decay: float = 0.1, sustain: float = 0.7,
         release: float = 0.2, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Classic ADSR envelope over ``n`` samples (attack/decay/release in seconds).

    Robust for short signals: the phases are scaled to fit ``n`` when the
    total would exceed it.
    """
    env = np.zeros(n, dtype=np.float32)
    if n <= 0:
        return env
    a = max(1, min(n // 2, int(attack * sample_rate)))
    r = max(1, min(n // 2, int(release * sample_rate)))
    remaining = n - a - r
    d = max(1, min(remaining // 2, int(decay * sample_rate)))
    s_len = max(0, remaining - d)
    env[:a] = np.linspace(0.0, 1.0, a, dtype=np.float32)
    env[a:a + d] = np.linspace(1.0, sustain, d, dtype=np.float32)
    if s_len > 0:
        env[a + d:a + d + s_len] = sustain
    env[n - r:] = np.linspace(sustain, 0.0, r, dtype=np.float32)
    return env


def exp_decay(n: int, *, tau: float = 0.5, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    t = np.arange(n) / sample_rate
    return np.exp(-t / tau).astype(np.float32)


def fade_io(samples: np.ndarray, *, fade_in: float = 0.01, fade_out: float = 0.1,
            sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    out = samples.copy()
    n = len(out)
    fi = max(1, int(fade_in * sample_rate))
    fo = max(1, int(fade_out * sample_rate))
    if n > 2 * fi:
        out[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)
    if n > 2 * fo:
        out[n - fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)
    return out


# ── Filters ──────────────────────────────────────────────────────

def one_pole_lp(x: np.ndarray, cutoff: float, *, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """One-pole low-pass (smoothing) filter."""
    alpha = 1.0 - math.exp(-2.0 * math.pi * cutoff / sample_rate)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += alpha * (x[i] - acc)
        y[i] = acc
    return y.astype(np.float32)


def one_pole_hp(x: np.ndarray, cutoff: float, *, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """One-pole high-pass filter."""
    alpha = math.exp(-2.0 * math.pi * cutoff / sample_rate)
    y = np.empty_like(x)
    prev_x = 0.0
    prev_y = 0.0
    for i in range(len(x)):
        y[i] = alpha * (prev_y + x[i] - prev_x)
        prev_x = x[i]
        prev_y = y[i]
    return y.astype(np.float32)


def biquad_peak(x: np.ndarray, freq: float, q: float, gain_db: float, *, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Cookbook biquad peaking EQ filter (real recursive filter)."""
    a = 10 ** (gain_db / 40.0)
    w0 = 2.0 * math.pi * freq / sample_rate
    alpha = math.sin(w0) / (2.0 * q)
    b0 = 1 + alpha * a
    b1 = -2 * math.cos(w0)
    b2 = 1 - alpha * a
    a0 = 1 + alpha / a
    a1 = -2 * math.cos(w0)
    a2 = 1 - alpha / a
    return _biquad(x, b0, b1, b2, a0, a1, a2)


def biquad_lowshelf(x: np.ndarray, freq: float, gain_db: float, *, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    a = 10 ** (gain_db / 40.0)
    w0 = 2.0 * math.pi * freq / sample_rate
    alpha = math.sin(w0) / math.sqrt(2.0)
    b0 = a * ((a + 1) - (a - 1) * math.cos(w0) + 2 * math.sqrt(a) * alpha)
    b1 = 2 * a * ((a - 1) - (a + 1) * math.cos(w0))
    b2 = a * ((a + 1) - (a - 1) * math.cos(w0) - 2 * math.sqrt(a) * alpha)
    a0 = (a + 1) + (a - 1) * math.cos(w0) + 2 * math.sqrt(a) * alpha
    a1 = -2 * ((a - 1) + (a + 1) * math.cos(w0))
    a2 = (a + 1) + (a - 1) * math.cos(w0) - 2 * math.sqrt(a) * alpha
    return _biquad(x, b0, b1, b2, a0, a1, a2)


def biquad_highshelf(x: np.ndarray, freq: float, gain_db: float, *, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    a = 10 ** (gain_db / 40.0)
    w0 = 2.0 * math.pi * freq / sample_rate
    alpha = math.sin(w0) / math.sqrt(2.0)
    b0 = a * ((a + 1) + (a - 1) * math.cos(w0) + 2 * math.sqrt(a) * alpha)
    b1 = -2 * a * ((a - 1) + (a + 1) * math.cos(w0))
    b2 = a * ((a + 1) + (a - 1) * math.cos(w0) - 2 * math.sqrt(a) * alpha)
    a0 = (a + 1) - (a - 1) * math.cos(w0) + 2 * math.sqrt(a) * alpha
    a1 = 2 * ((a - 1) - (a + 1) * math.cos(w0))
    a2 = (a + 1) - (a - 1) * math.cos(w0) - 2 * math.sqrt(a) * alpha
    return _biquad(x, b0, b1, b2, a0, a1, a2)


def _biquad(x: np.ndarray, b0: float, b1: float, b2: float, a0: float, a1: float, a2: float) -> np.ndarray:
    y = np.zeros_like(x, dtype=np.float64)
    x1 = x2 = y1 = y2 = 0.0
    a0i = 1.0 / a0
    for i in range(len(x)):
        y[i] = b0 * a0i * x[i] + b1 * a0i * x1 + b2 * a0i * x2 - a1 * a0i * y1 - a2 * a0i * y2
        x2, x1 = x1, x[i]
        y2, y1 = y1, y[i]
    return y.astype(np.float32)


def resonant_lp(x: np.ndarray, cutoff: float, resonance: float = 1.0, *, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Simple state-variable resonant low-pass (Chamberlin SVF)."""
    f = 2.0 * math.sin(math.pi * min(cutoff, sample_rate * 0.49) / sample_rate)
    q = max(0.1, resonance)
    low = high = band = 0.0
    out = np.empty_like(x, dtype=np.float32)
    for i in range(len(x)):
        low += f * band
        high = x[i] - low - q * band
        band += f * high
        out[i] = low
    return out


def comb(x: np.ndarray, delay_s: float, feedback: float = 0.5, *, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    d = max(1, int(delay_s * sample_rate))
    y = np.zeros_like(x)
    for i in range(len(x)):
        y[i] = x[i] + feedback * (y[i - d] if i >= d else 0.0)
    return y.astype(np.float32)


def allpass(x: np.ndarray, delay_s: float, feedback: float = 0.5, *, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    d = max(1, int(delay_s * sample_rate))
    y = np.zeros_like(x)
    for i in range(len(x)):
        xn = x[i]
        delayed = y[i - d] if i >= d else 0.0
        y[i] = -feedback * xn + delayed + feedback * (x[i - d] if i >= d else 0.0)
    return y.astype(np.float32)


# ── Phase vocoder (pitch shift / time stretch) ───────────────────

def _phase_vocoder(x: np.ndarray, rate: float, *, window: int = 2048, hop: int = 512) -> np.ndarray:
    """Time-stretch a mono signal by ``rate`` using the phase vocoder.

    ``rate > 1`` speeds up (pitch preserved), ``rate < 1`` slows down.
    """
    if rate <= 0:
        return x.copy()
    n = len(x)
    if n <= window:
        return x.copy()
    n_out = int(n / rate)
    win = np.hanning(window).astype(np.float32)
    out = np.zeros(n_out + window, dtype=np.float64)
    acc = np.zeros(n_out + window, dtype=np.float64)
    phase_adv = 2 * math.pi * hop / window
    prev_phase = 0.0
    in_idx = 0
    out_idx = 0
    while in_idx + window <= n and out_idx + window <= n_out:
        frame = x[in_idx:in_idx + window] * win
        spec = np.fft.rfft(frame)
        mag = np.abs(spec)
        phase = np.angle(spec)
        # expected phase advance per bin
        expected = prev_phase + hop * 2 * math.pi * np.arange(len(mag)) / window
        delta = phase - expected
        delta = np.mod(delta + math.pi, 2 * math.pi) - math.pi
        new_phase = prev_phase + delta + phase_adv * np.arange(len(mag))
        prev_phase = phase
        resyn = mag * np.exp(1j * new_phase)
        out[out_idx:out_idx + window] += np.fft.irfft(resyn, window) * win
        acc[out_idx:out_idx + window] += win * win
        in_idx += hop
        out_idx += int(hop * rate)
    acc[acc < 1e-6] = 1.0
    out /= acc
    return out[:n_out].astype(np.float32)


def pitch_shift(x: np.ndarray, semitones: float, *, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Shift pitch by ``semitones`` while keeping duration (phase vocoder)."""
    if abs(semitones) < 0.01:
        return x.copy()
    rate = 2 ** (-semitones / 12.0)
    stretched = _phase_vocoder(x, rate)
    return resample(stretched, len(x))


def time_stretch(x: np.ndarray, rate: float) -> np.ndarray:
    """Time-stretch by ``rate`` (>1 faster) with pitch preserved."""
    return _phase_vocoder(x, rate)


def resample(x: np.ndarray, target_len: int) -> np.ndarray:
    """Linear resample to a target length."""
    if target_len <= 0 or len(x) == target_len:
        return x.copy()
    if len(x) == 0:
        return np.zeros(target_len, dtype=np.float32)
    idx = np.linspace(0, len(x) - 1, target_len)
    x0 = np.floor(idx).astype(int)
    x1 = np.minimum(x0 + 1, len(x) - 1)
    frac = (idx - x0).astype(np.float32)
    return (x[x0] * (1 - frac) + x[x1] * frac).astype(np.float32)


# ── Analysis ─────────────────────────────────────────────────────

def rms(samples: np.ndarray) -> float:
    if len(samples) == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(samples.astype(np.float64)))))


def peak(samples: np.ndarray) -> float:
    return float(np.max(np.abs(samples))) if len(samples) else 0.0


def normalize_peak(samples: np.ndarray, target: float = 0.95) -> np.ndarray:
    p = peak(samples)
    if p < 1e-9:
        return samples.copy()
    return (samples * (target / p)).astype(np.float32)


def normalize_rms(samples: np.ndarray, target: float = 0.2) -> np.ndarray:
    r = rms(samples)
    if r < 1e-9:
        return samples.copy()
    return (samples * (target / r)).astype(np.float32)


def limiter(samples: np.ndarray, threshold: float = 0.98, *, release: float = 0.1,
            lookahead: float = 0.005, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Brickwall peak limiter with lookahead: output never exceeds threshold.

    The signal is delayed by ``lookahead`` seconds and the gain is the
    minimum ``threshold / envelope`` over that lookahead window, so a
    transient is fully clamped *before* it reaches the output (a plain
    feedback limiter lets the first peak leak through). Gain reduction is
    instantaneous; only the release back to unity is smoothed to avoid
    pumping. ``desired`` is capped at 1.0 so quiet passages are never
    amplified by ``threshold / tiny``.
    """
    n = len(samples)
    if n == 0:
        return samples.copy()
    la = min(n - 1, max(1, int(lookahead * sample_rate)))
    env = np.abs(samples.astype(np.float64))
    desired = np.minimum(1.0, threshold / (env + 1e-9))
    # Output index ``i`` plays original sample ``i - la``. Its gain is the
    # minimum desired gain over the window ``[i - la, i]`` (original indices),
    # so a transient at original index T is already fully clamped when it
    # reaches the output at ``T + la`` — the clamp never leaks through.
    if la + 1 < n:
        windows = np.lib.stride_tricks.sliding_window_view(desired, la + 1)
        slide_min = np.min(windows, axis=1)  # slide_min[k] = min(desired[k..k+la])
    else:
        slide_min = np.array([float(np.min(desired))])
    gain = np.ones(n)
    # i < la: window starts at 0 → prefix minimum. i >= la: slide_min[i - la].
    gain[:la] = np.minimum.accumulate(desired[:la])
    tail_len = min(n - la, len(slide_min))
    gain[la:la + tail_len] = slide_min[:tail_len]
    rt = math.exp(-1.0 / (release * sample_rate))
    g = 1.0
    for i in range(n):
        target = float(gain[i])
        # instant reduction — lookahead makes it inaudible; release smoothed
        g = target if target < g else rt * g + (1 - rt) * 1.0
        gain[i] = g
    delayed = np.concatenate([np.zeros(la, dtype=np.float32), samples[:-la]])
    return (delayed * gain).astype(np.float32)


def f0_autocorr(x: np.ndarray, *, sample_rate: int = SAMPLE_RATE, fmin: float = 60.0, fmax: float = 500.0) -> float:
    """Fundamental frequency via autocorrelation (returns 0 when unvoiced)."""
    n = len(x)
    if n < sample_rate // fmax * 2:
        return 0.0
    x = x - np.mean(x)
    lo = max(1, int(sample_rate / fmax))
    hi = min(n // 2, int(sample_rate / fmin))
    if hi <= lo:
        return 0.0
    corr = np.correlate(x, x, mode="full")[n - 1:]
    lag = lo + int(np.argmax(corr[lo:hi]))
    if lag <= 0 or corr[lag] <= 0:
        return 0.0
    rms0 = np.sqrt(np.mean(x * x)) + 1e-9
    norm = corr[lag] / (n * rms0 * rms0)
    if norm < 0.3:  # weak periodicity → unvoiced
        return 0.0
    return sample_rate / lag


def spectral_centroid(x: np.ndarray, *, sample_rate: int = SAMPLE_RATE) -> float:
    spec = np.abs(np.fft.rfft(x))
    freqs = np.fft.rfftfreq(len(x), 1.0 / sample_rate)
    total = np.sum(spec) + 1e-9
    return float(np.sum(freqs * spec) / total)


def spectral_rolloff(x: np.ndarray, percentile: float = 0.85, *, sample_rate: int = SAMPLE_RATE) -> float:
    spec = np.abs(np.fft.rfft(x))
    freqs = np.fft.rfftfreq(len(x), 1.0 / sample_rate)
    total = np.sum(spec) + 1e-9
    cum = np.cumsum(spec)
    idx = int(np.searchsorted(cum, percentile * total))
    idx = min(idx, len(freqs) - 1)
    return float(freqs[idx])


def band_energy(x: np.ndarray, lo: float, hi: float, *, sample_rate: int = SAMPLE_RATE) -> float:
    spec = np.abs(np.fft.rfft(x))
    freqs = np.fft.rfftfreq(len(x), 1.0 / sample_rate)
    mask = (freqs >= lo) & (freqs <= hi)
    return float(np.sum(spec[mask] ** 2))


def spectral_gate(x: np.ndarray, *, threshold: float = 0.02, fft_size: int = 2048,
                  sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Spectral noise gate: zero FFT bins below an adaptive noise floor.

    The floor is estimated from the signal itself (20th percentile of all
    frame-bin magnitudes) so the gate preserves speech no matter the input
    level — a fixed floor would destroy quiet-but-clean audio.
    """
    n = len(x)
    if n < fft_size:
        return x.copy()
    win = np.hanning(fft_size)
    out = np.zeros(n + fft_size)
    acc = np.zeros(n + fft_size)
    hop = fft_size // 4

    # Estimate the noise floor from the quietest 20% of frame bins.
    magnitudes: list[np.ndarray] = []
    for start in range(0, n - fft_size, hop):
        frame = x[start:start + fft_size] * win
        magnitudes.append(np.abs(np.fft.rfft(frame)))
    if not magnitudes:
        return x.copy()
    all_mags = np.concatenate(magnitudes)
    noise_floor = float(np.percentile(all_mags, 20)) * max(threshold, 0.02)

    for start in range(0, n - fft_size, hop):
        frame = x[start:start + fft_size] * win
        spec = np.fft.rfft(frame)
        mag = np.abs(spec)
        mag[mag < noise_floor] = 0.0
        cleaned = np.fft.irfft(mag * np.exp(1j * np.angle(spec)), fft_size) * win
        out[start:start + fft_size] += cleaned
        acc[start:start + fft_size] += win * win
    acc[acc < 1e-6] = 1.0
    out /= acc
    return out[:n].astype(np.float32)


def silence(duration: float, *, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    return np.zeros(int(sample_rate * duration), dtype=np.float32)


def concatenate(chunks: list[np.ndarray], *, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Concatenate variable-length audio chunks into one buffer."""
    if not chunks:
        return silence(0.5, sample_rate=sample_rate)
    return np.concatenate([np.asarray(c, dtype=np.float32).reshape(-1) for c in chunks]).astype(np.float32)


# ── Stereo / mixing ──────────────────────────────────────────────

def to_stereo(mono: np.ndarray, *, pan: float = 0.0) -> np.ndarray:
    """Mono → stereo. ``pan`` in [-1, 1] (left → right)."""
    left = mono * min(1.0, 1.0 - pan)
    right = mono * min(1.0, 1.0 + pan)
    return np.stack([left, right], axis=-1).astype(np.float32)


def stereo_pan(stereo: np.ndarray, pan: float = 0.0) -> np.ndarray:
    """Apply pan to a stereo signal (equal-power)."""
    if stereo.ndim != 2 or stereo.shape[1] != 2:
        return to_stereo(np.asarray(stereo).reshape(-1), pan=pan)
    angle = (pan + 1.0) * 0.25 * math.pi  # 0 → π/2
    l = np.cos(angle)
    r = np.sin(angle)
    out = stereo.copy()
    out[:, 0] *= l * math.sqrt(2)
    out[:, 1] *= r * math.sqrt(2)
    return out.astype(np.float32)


def mix_tracks(
    tracks: list[dict[str, Any]],
    *,
    total_duration: float | None = None,
    sample_rate: int = SAMPLE_RATE,
) -> np.ndarray:
    """Mix a list of ``{samples, offset, gain, pan}`` dicts into one mono buffer."""
    if not tracks:
        return np.zeros(int((total_duration or 1.0) * sample_rate), dtype=np.float32)
    length = int((total_duration or 1.0) * sample_rate)
    for tr in tracks:
        end = int((tr.get("offset", 0.0) + len(tr["samples"]) / sample_rate) * sample_rate) + 1
        length = max(length, end)
    out = np.zeros(length, dtype=np.float64)
    for tr in tracks:
        samples = np.asarray(tr["samples"], dtype=np.float64)
        offset = int(tr.get("offset", 0.0) * sample_rate)
        gain = float(tr.get("gain", 1.0))
        end = min(length, offset + len(samples))
        if end > offset:
            out[offset:end] += samples[: end - offset] * gain
    return (out / (1.0 + np.max(np.abs(out)) + 1e-9)).astype(np.float32)


# ── File IO ──────────────────────────────────────────────────────

def read_audio(path: str | Path, *, target_sr: int = SAMPLE_RATE) -> tuple[np.ndarray, int]:
    """Read any audio file into a mono float32 array (wav/flac/ogg/mp3)."""
    p = Path(path)
    data: np.ndarray | None = None
    sr = target_sr
    if p.suffix.lower() in (".wav", ".flac", ".ogg", ".aiff", ".aif"):
        try:
            import soundfile as sf

            data, sr = sf.read(str(p), dtype="float32", always_2d=False)
        except Exception:  # noqa: BLE001 — fall back to stdlib wave
            data = _read_wav_stdlib(p)
            sr = SAMPLE_RATE
    else:
        # mp3/m4a/opus and anything else → decode with ffmpeg to wav
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name
            result = subprocess.run(
                ["ffmpeg", "-y", "-i", str(p), "-ac", "1", "-ar", str(target_sr), tmp_path],
                capture_output=True, text=True, timeout=120,
            )
            if result.returncode == 0:
                data = _read_wav_stdlib(tmp_path)
                sr = target_sr
            Path(tmp_path).unlink(missing_ok=True)
        except Exception:  # noqa: BLE001
            data = None
    if data is None or len(data) == 0:
        return np.zeros(1, dtype=np.float32), sr
    data = np.asarray(data, dtype=np.float32).reshape(-1)
    return data, sr


def _read_wav_stdlib(p: Path) -> np.ndarray:
    with wave.open(str(p), "rb") as w:
        n = w.getnframes()
        raw = w.readframes(n)
        data = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32767.0
    return data


def write_audio(path: str | Path, samples: np.ndarray, *, sample_rate: int = SAMPLE_RATE,
                bitrate: str = "192k") -> Path:
    """Write float samples to a real audio file (wav via stdlib, else ffmpeg)."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    mono = np.clip(samples.reshape(-1), -1.0, 1.0)
    pcm = (mono * 32767).astype(np.int16)
    if out.suffix.lower() == ".wav":
        with wave.open(str(out), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sample_rate)
            w.writeframes(pcm.tobytes())
        return out
    # Compressed formats (mp3/flac/ogg) → pipe through ffmpeg.
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name
    with wave.open(tmp_path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(pcm.tobytes())
    codec_map = {".mp3": "libmp3lame", ".flac": "flac", ".ogg": "libvorbis", ".m4a": "aac"}
    codec = codec_map.get(out.suffix.lower())
    cmd = ["ffmpeg", "-y", "-i", tmp_path]
    if codec:
        cmd += ["-c:a", codec]
        if codec == "libmp3lame":
            cmd += ["-b:a", bitrate]
    cmd += [str(out)]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    Path(tmp_path).unlink(missing_ok=True)
    if result.returncode != 0 or not out.exists() or out.stat().st_size == 0:
        raise RuntimeError(f"ffmpeg encode to {out.name} failed: {result.stderr[-200:]}")
    return out
