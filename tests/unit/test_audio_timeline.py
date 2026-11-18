from __future__ import annotations

import wave

import numpy as np
import pytest

from modules.ai_video_studio.media import audio_timeline, dsp


def _audio_roots(tmp_path, monkeypatch):
    downloads = tmp_path / "downloads"
    downloads.mkdir()
    def subsystem(name):
        path = downloads / name
        path.mkdir(parents=True, exist_ok=True)
        return path
    monkeypatch.setattr(audio_timeline, "get_downloads_dir", lambda: downloads)
    monkeypatch.setattr(audio_timeline, "get_subsystem_dir", subsystem)
    return downloads


def test_mix_audio_timeline_places_trimmed_clip_with_fades_and_fixed_duration(tmp_path, monkeypatch):
    downloads = _audio_roots(tmp_path, monkeypatch)
    source = downloads / "music" / "bed.wav"
    dsp.write_audio(source, np.ones(dsp.SAMPLE_RATE, dtype=np.float32) * 0.2)
    output = tmp_path / "mix.wav"

    result = audio_timeline.mix_audio_timeline(
        [{
            "asset": str(source), "start": 0.5, "end": 2.0,
            "trim_start": 0.1, "volume": 0.5, "fade_in": 0.2, "fade_out": 0.2,
        }],
        output,
        total_duration=3.0,
    )

    assert result["clip_count"] == 1
    assert result["clips"][0]["status"] == "mixed"
    with wave.open(str(output), "rb") as rendered:
        assert rendered.getnframes() == 3 * dsp.SAMPLE_RATE
        assert rendered.getframerate() == dsp.SAMPLE_RATE


def test_mix_audio_timeline_accepts_pre_aligned_narration_samples(tmp_path, monkeypatch):
    _audio_roots(tmp_path, monkeypatch)
    output = tmp_path / "narration_mix.wav"
    result = audio_timeline.mix_audio_timeline(
        [{"samples": np.ones(dsp.SAMPLE_RATE, dtype=np.float32) * 0.1,
          "offset": 0.5, "gain": 0.7}],
        output,
        total_duration=2.0,
    )
    assert result["clips"][0]["asset"] == "narration"
    assert result["clips"][0]["start"] == 0.5
    with wave.open(str(output), "rb") as rendered:
        assert rendered.getnframes() == 2 * dsp.SAMPLE_RATE


def test_mix_audio_timeline_rejects_arbitrary_files(tmp_path, monkeypatch):
    _audio_roots(tmp_path, monkeypatch)
    outside = tmp_path / "private.wav"
    dsp.write_audio(outside, np.ones(1000, dtype=np.float32) * 0.1)

    with pytest.raises(ValueError, match="approved generated-audio"):
        audio_timeline.mix_audio_timeline(
            [{"asset": str(outside), "start": 0, "end": 1}],
            tmp_path / "mix.wav",
            total_duration=1,
        )


@pytest.mark.parametrize("clip", [
    {"asset": "missing.wav", "start": 0, "end": 1, "volume": 2.1},
    {"asset": "missing.wav", "start": -1, "end": 1},
    {"asset": "missing.wav", "start": 0, "end": 1, "fade_in": 2},
])
def test_mix_audio_timeline_rejects_invalid_clip_controls(tmp_path, monkeypatch, clip):
    downloads = _audio_roots(tmp_path, monkeypatch)
    source = downloads / "music" / "tone.wav"
    dsp.write_audio(source, np.ones(dsp.SAMPLE_RATE, dtype=np.float32) * 0.1)
    clip["asset"] = str(source)

    with pytest.raises(ValueError):
        audio_timeline.mix_audio_timeline([clip], tmp_path / "mix.wav", total_duration=1)
