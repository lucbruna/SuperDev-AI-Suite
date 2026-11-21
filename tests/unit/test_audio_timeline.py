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


def test_final_mix_quality_report_detects_masking_silence_and_pre_limiter_peak():
    sample_rate = 1000
    samples = np.full((3000, 2), 0.2, dtype=np.float32)
    samples[1000:2000] = 0.0
    windows = 30
    voice_energy = np.zeros(windows, dtype=np.float64)
    voice_counts = np.zeros(windows, dtype=np.int64)
    music_energy = np.zeros(windows, dtype=np.float64)
    music_counts = np.zeros(windows, dtype=np.int64)
    voice_energy[:10] = 10 * (0.1 ** 2)
    voice_counts[:10] = 10
    music_energy[:10] = 10 * (0.2 ** 2)
    music_counts[:10] = 10
    report = audio_timeline.build_audio_quality_report(
        samples, sample_rate=sample_rate,
        narration_energy=voice_energy, narration_counts=voice_counts,
        music_energy=music_energy, music_counts=music_counts,
        pre_limiter_peak=1.2,
    )
    assert report["status"] == "needs_review"
    assert report["export_allowed"] is True
    assert report["silence_gaps"] == [{"start": 1.0, "end": 2.0, "duration": 1.0}]
    assert report["narration_music_masking"][0]["start"] == 0.0
    assert report["recommendations"][0]["action"] == "increase_ducking"
    assert report["recommendations"][0]["recommended_ducking_db"] == 12.0
    assert {item["code"] for item in report["warnings"]} == {
        "pre_limiter_clipping", "internal_silence_gaps", "narration_may_be_masked",
    }


def test_final_mix_quality_does_not_mistake_phase_inverted_stereo_for_silence():
    mono = np.full(2000, 0.1, dtype=np.float32)
    stereo = np.column_stack([mono, -mono])
    report = audio_timeline.build_audio_quality_report(stereo, sample_rate=1000)
    assert report["silence_gaps"] == []
    assert report["rms_dbfs"] < 0

def test_final_mix_quality_report_blocks_actual_output_clipping():
    samples = np.zeros((1000, 2), dtype=np.float32)
    samples[500:510] = 1.0
    report = audio_timeline.build_audio_quality_report(samples, sample_rate=1000)
    assert report["status"] == "blocked"
    assert report["export_allowed"] is False
    assert report["critical_count"] == 1
    assert any(item["code"] == "final_clipping_detected" for item in report["warnings"])


def test_mix_audio_timeline_returns_quality_report(tmp_path, monkeypatch):
    _audio_roots(tmp_path, monkeypatch)
    voice = np.full(8000, 0.1, dtype=np.float32)
    music = np.full(8000, 0.2, dtype=np.float32)
    result = audio_timeline.mix_audio_timeline(
        [
            {"samples": voice, "kind": "narration", "start": 0, "end": 1},
            {"samples": music, "kind": "music", "start": 0, "end": 1},
        ],
        tmp_path / "quality_mix.wav", total_duration=1, sample_rate=8000,
        normalization_enabled=False,
    )
    assert result["quality"]["duration_seconds"] == 1.0
    assert result["quality"]["export_allowed"] is True
    assert result["quality"]["narration_music_masking"]


def test_audio_intelligence_flags_clipping_silence_and_stereo_imbalance(tmp_path, monkeypatch):
    downloads = _audio_roots(tmp_path, monkeypatch)
    path = downloads / "music" / "analysis.wav"
    path.parent.mkdir(parents=True, exist_ok=True)
    audio = np.zeros((44100, 2), dtype=np.float32)
    audio[:22050, 0] = 1.0
    audio[:22050, 1] = 0.1
    dsp.write_audio(path, audio)
    report = audio_timeline.analyze_audio_file(path)
    assert report["channels"] == 2
    assert report["duration_seconds"] == pytest.approx(1.0, abs=0.01)
    assert report["clipping_ratio"] > 0
    assert report["silence_ratio"] >= 0.4
    assert "clipping_or_near_full_scale_peak" in report["warnings"]
    assert "strong_left_right_imbalance" in report["warnings"]


def test_audio_intelligence_detects_phase_cancellation_risk(tmp_path, monkeypatch):
    downloads = _audio_roots(tmp_path, monkeypatch)
    path = downloads / "music" / "phase.wav"
    path.parent.mkdir(parents=True, exist_ok=True)
    mono = np.sin(np.arange(44100, dtype=np.float32) * 0.04)
    dsp.write_audio(path, np.column_stack([mono, -mono]))
    report = audio_timeline.analyze_audio_file(path)
    assert report["stereo_correlation"] == pytest.approx(-1.0, abs=0.01)
    assert "possible_stereo_phase_cancellation" in report["warnings"]


def test_ducking_recommendation_uses_measured_narration_and_music_levels():
    recommendation = audio_timeline.recommend_ducking(
        [{"rms_dbfs": -24.0}, {"rms_dbfs": -26.0}],
        [{"rms_dbfs": -18.0}],
    )
    assert recommendation["available"] is True
    assert recommendation["recommended_ducking_db"] == 9.8
    assert recommendation["recommended_threshold_db"] == -35.0


def test_ducking_recommendation_requires_voice_and_music():
    assert audio_timeline.recommend_ducking([], [{"rms_dbfs": -20}])["available"] is False


def test_list_audio_assets_returns_only_approved_generated_files(tmp_path, monkeypatch):
    downloads = _audio_roots(tmp_path, monkeypatch)
    music = downloads / "music" / "theme.wav"
    effects = downloads / "effects" / "whoosh.mp3"
    music.parent.mkdir(parents=True, exist_ok=True)
    effects.parent.mkdir(parents=True, exist_ok=True)
    dsp.write_audio(music, np.zeros(100, dtype=np.float32))
    effects.write_bytes(b"fake-mp3")
    outside = tmp_path / "secret.wav"
    dsp.write_audio(outside, np.zeros(100, dtype=np.float32))

    assets = audio_timeline.list_audio_assets()
    assert {item["asset"] for item in assets} == {"music/theme.wav", "effects/whoosh.mp3"}
    assert all("secret" not in item["asset"] for item in assets)



def test_compressor_reduces_level_above_threshold_and_preserves_stereo_ratio():
    audio = np.column_stack([
        np.full(44100, 0.8, dtype=np.float32),
        np.full(44100, 0.4, dtype=np.float32),
    ])
    compressed = dsp.compressor(audio, threshold_db=-12, ratio=4, attack=0.005, release=0.05)
    assert compressed.shape == audio.shape
    assert dsp.rms(compressed) < dsp.rms(audio)
    active = compressed[10000:]
    assert np.mean(active[:, 1] / active[:, 0]) == pytest.approx(0.5, abs=0.01)


def test_compressor_rejects_invalid_controls():
    with pytest.raises(ValueError, match="compressor controls"):
        dsp.compressor(np.ones(100, dtype=np.float32), ratio=0.5)


def test_three_band_eq_boosts_low_frequency_and_preserves_stereo_shape():
    sample_rate = 8000
    time = np.arange(sample_rate, dtype=np.float32) / sample_rate
    bass = np.sin(2 * np.pi * 80 * time).astype(np.float32)
    stereo = np.column_stack([bass, bass * 0.5])
    equalized = dsp.three_band_eq(stereo, low_db=6, mid_db=0, high_db=0, sample_rate=sample_rate)
    assert equalized.shape == stereo.shape
    assert dsp.rms(equalized[:, 0]) > dsp.rms(stereo[:, 0]) * 1.4
    assert np.mean(equalized[:, 1] / equalized[:, 0]) == pytest.approx(0.5, abs=0.02)


def test_three_band_eq_rejects_out_of_range_gains():
    with pytest.raises(ValueError, match="EQ gains"):
        dsp.three_band_eq(np.ones(100, dtype=np.float32), low_db=13)


def test_audio_mixer_reports_applied_mastering_settings(tmp_path, monkeypatch):
    _audio_roots(tmp_path, monkeypatch)
    source = np.full((8000, 2), 0.15, dtype=np.float32)
    result = audio_timeline.mix_audio_timeline(
        [{"samples": source, "start": 0, "end": 1, "kind": "narration"}],
        tmp_path / "mastered.wav", total_duration=1, sample_rate=8000,
        compressor_enabled=True, compressor_threshold_db=-20, compressor_ratio=4,
        eq_enabled=True, eq_low_db=2, eq_mid_db=-1, eq_high_db=1,
        normalization_enabled=False,
    )
    assert result["mastering"]["compressor_enabled"] is True
    assert result["mastering"]["compressor_ratio"] == 4
    assert result["mastering"]["eq_enabled"] is True
    assert result["mastering"]["eq_low_db"] == 2


def test_dsp_round_trips_stereo_wav_without_collapsing_channels(tmp_path):
    source = tmp_path / "stereo.wav"
    stereo = np.column_stack([np.full(800, 0.25, dtype=np.float32), np.full(800, -0.1, dtype=np.float32)])
    dsp.write_audio(source, stereo, sample_rate=8000)
    decoded, rate = dsp.read_audio(source, target_sr=8000, preserve_channels=True)
    assert rate == 8000
    assert decoded.shape == (800, 2)
    assert np.mean(decoded[:, 0]) == pytest.approx(0.25, abs=0.001)
    assert np.mean(decoded[:, 1]) == pytest.approx(-0.1, abs=0.001)

def test_dsp_resamples_stereo_frames_without_channel_broadcast_errors():
    source = np.column_stack([np.linspace(0, 1, 100, dtype=np.float32), np.linspace(1, 0, 100, dtype=np.float32)])
    result = dsp.resample(source, 200)
    assert result.shape == (200, 2)
    assert result[0, 0] == pytest.approx(0)
    assert result[0, 1] == pytest.approx(1)
    assert result[-1, 0] == pytest.approx(1)
    assert result[-1, 1] == pytest.approx(0)


def test_stereo_mixer_keeps_channels_and_applies_pan(tmp_path, monkeypatch):
    _audio_roots(tmp_path, monkeypatch)
    stereo = np.column_stack([np.full(8000, 0.2, dtype=np.float32), np.full(8000, 0.2, dtype=np.float32)])
    output = tmp_path / "panned.wav"
    result = audio_timeline.mix_audio_timeline(
        [{"samples": stereo, "start": 0, "end": 1, "kind": "sound_effect", "pan": -1}],
        output, total_duration=1, sample_rate=8000, normalization_enabled=False,
    )
    with wave.open(str(output), "rb") as rendered:
        assert rendered.getnchannels() == 2
    rendered, rate = dsp.read_audio(output, target_sr=8000, preserve_channels=True)
    assert result["channels"] == 2
    assert result["channel_layout"] == "stereo"
    assert np.mean(np.abs(rendered[:, 0])) > 0.1
    assert np.max(np.abs(rendered[:, 1])) < 0.001

def test_stereo_limiter_uses_linked_gain_for_both_channels():
    stereo = np.zeros((2000, 2), dtype=np.float32)
    stereo[500, 0] = 1.2
    stereo[500, 1] = 0.6
    limited = dsp.limiter(stereo, threshold=0.8, sample_rate=8000)
    assert np.max(np.abs(limited)) <= 0.801
    assert limited[500 + 40, 1] / limited[500 + 40, 0] == pytest.approx(0.5, abs=0.02)

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


def test_mix_audio_timeline_loops_short_music_only_when_requested(tmp_path, monkeypatch):
    downloads = _audio_roots(tmp_path, monkeypatch)
    source = downloads / "music" / "short.wav"
    dsp.write_audio(source, np.full(dsp.SAMPLE_RATE // 4, 0.12, dtype=np.float32))
    output = tmp_path / "looped.wav"
    result = audio_timeline.mix_audio_timeline(
        [{"asset": str(source), "start": 0, "end": 1, "loop": True}],
        output, total_duration=1.0,
    )
    assert result["clips"][0]["loop"] is True
    samples, rate = dsp.read_audio(output, target_sr=dsp.SAMPLE_RATE, preserve_channels=True)
    assert rate == dsp.SAMPLE_RATE
    assert samples.shape == (dsp.SAMPLE_RATE, 2)
    assert np.max(np.abs(samples[rate // 2:])) > 0.08


def test_mix_audio_timeline_ducks_music_during_narration(tmp_path, monkeypatch):
    _audio_roots(tmp_path, monkeypatch)
    sample_rate = 8000
    music = np.full(sample_rate * 2, 0.2, dtype=np.float32)
    narration = np.full(sample_rate, 0.2, dtype=np.float32)
    output = tmp_path / "ducked.wav"
    result = audio_timeline.mix_audio_timeline(
        [
            {"samples": music, "start": 0, "end": 2, "kind": "music"},
            {"samples": narration, "offset": 0.5, "kind": "narration"},
        ],
        output, total_duration=2, sample_rate=sample_rate,
        ducking_db=12, ducking_threshold_db=-40, ducking_attack=0.01, ducking_release=0.05,
    )
    mixed, _ = dsp.read_audio(output, target_sr=sample_rate)
    before = np.sqrt(np.mean(mixed[int(0.1 * sample_rate):int(0.4 * sample_rate)] ** 2))
    during_with_voice = mixed[int(0.9 * sample_rate):int(1.3 * sample_rate)]
    during_music = during_with_voice - 0.2
    during = np.sqrt(np.mean(during_music ** 2))
    assert result["ducking"]["speech_detected"] is True
    assert result["clips"][0]["ducking_applied"] is True
    assert during < before * 0.4

def test_mix_audio_timeline_normalizes_rms_with_gain_cap_and_limiter(tmp_path, monkeypatch):
    _audio_roots(tmp_path, monkeypatch)
    sample_rate = 8000
    quiet = np.full(sample_rate, 0.01, dtype=np.float32)
    output = tmp_path / "normalized.wav"
    result = audio_timeline.mix_audio_timeline(
        [{"samples": quiet, "start": 0, "end": 1}],
        output, total_duration=1, sample_rate=sample_rate,
        normalization_enabled=True, normalization_target_dbfs=-20, normalization_max_gain_db=6,
    )
    rendered, _ = dsp.read_audio(output, target_sr=sample_rate)
    assert result["normalization"]["gain_db"] == 6
    assert 0.018 <= dsp.rms(rendered) <= 0.022
    assert result["peak"] <= 0.97


def test_audio_mixer_voice_preset_applies_known_mastering_curve(tmp_path, monkeypatch):
    _audio_roots(tmp_path, monkeypatch)
    result = audio_timeline.mix_audio_timeline(
        [{"samples": np.full((8000, 2), 0.1, dtype=np.float32), "start": 0, "end": 1, "kind": "narration"}],
        tmp_path / "voice_preset.wav", total_duration=1, sample_rate=8000,
        mastering_preset="voice", normalization_enabled=False,
    )
    mastering = result["mastering"]
    assert mastering["preset"] == "voice"
    assert mastering["compressor_enabled"] is True
    assert mastering["compressor_threshold_db"] == -22
    assert mastering["compressor_ratio"] == 3.5
    assert mastering["eq_low_db"] == -2
    assert mastering["eq_mid_db"] == 1.5
    assert mastering["eq_high_db"] == 2


def test_audio_mixer_rejects_unknown_mastering_preset(tmp_path, monkeypatch):
    _audio_roots(tmp_path, monkeypatch)
    with pytest.raises(ValueError, match="mastering_preset"):
        audio_timeline.mix_audio_timeline(
            [{"samples": np.zeros(800, dtype=np.float32), "start": 0, "end": 0.1}],
            tmp_path / "invalid_preset.wav", total_duration=0.1, sample_rate=8000,
            mastering_preset="not-a-preset",
        )


def test_normalize_loudness_file_uses_two_pass_ebu_r128(tmp_path, monkeypatch):
    source = tmp_path / "mix.wav"
    source.write_bytes(b"source")
    calls = []
    report = '{"input_i":"-19.0", "input_tp":"-3.0", "input_lra":"5.0", "input_thresh":"-29.0", "target_offset":"0.2"}'
    def fake_run(command, **kwargs):
        calls.append(command)
        if command[-1] != "-":
            from pathlib import Path
            Path(command[-1]).write_bytes(b"normalized")
        return type("Result", (), {"returncode": 0, "stderr": report, "stdout": ""})()
    monkeypatch.setattr(audio_timeline.subprocess, "run", fake_run)
    monkeypatch.setattr(dsp, "read_audio", lambda path, target_sr, preserve_channels=False: (np.full((4410, 2), 0.1, dtype=np.float32) if preserve_channels else np.full(4410, 0.1, dtype=np.float32), 44100))
    monkeypatch.setattr(dsp, "limiter", lambda samples, **kwargs: samples)
    written = []
    monkeypatch.setattr(dsp, "write_audio", lambda path, samples, sample_rate: written.append((path, sample_rate)) or path)
    result = audio_timeline.normalize_loudness_file(source, target_lufs=-14, true_peak_db=-1, lra=11)
    assert len(calls) == 3  # analysis, normalization, and final-output verification
    assert "loudnorm=I=-14:TP=-1:LRA=11" in calls[0][calls[0].index("-af") + 1]
    assert "measured_I=-19.0" in calls[1][calls[1].index("-af") + 1]
    assert result["input_i"] == -19
    assert result["output_i"] == -19
    assert result["normalization_pass_i"] == -19
    assert result["passes"] == 2
    assert result["verified"] is True
    assert written and written[0][0] == source


def test_mix_audio_timeline_bypasses_rms_limiter_when_lufs_is_enabled(tmp_path, monkeypatch):
    _audio_roots(tmp_path, monkeypatch)
    limiter_calls = []
    monkeypatch.setattr(dsp, "limiter", lambda samples, **kwargs: limiter_calls.append(True) or samples)
    monkeypatch.setattr(audio_timeline, "normalize_loudness_file", lambda path, **kwargs: {"target_lufs": -14, "output_i": -14, "output_tp": -1, "output_lra": 6, "passes": 2, "verified": True})
    result = audio_timeline.mix_audio_timeline(
        [{"samples": np.full(8000, 0.8, dtype=np.float32), "kind": "narration", "offset": 0}],
        tmp_path / "lufs_mix.wav", total_duration=1, sample_rate=8000,
        loudness_normalization_enabled=True, normalization_enabled=True,
    )
    assert limiter_calls == []
    assert result["normalization"]["bypassed_for_loudness"] is True
    assert result["normalization"]["enabled"] is False
    assert result["loudness"]["verified"] is True


@pytest.mark.parametrize("kwargs", [
    {"target_lufs": -40},
    {"true_peak_db": -12},
    {"lra": 25},
])
def test_normalize_loudness_file_rejects_out_of_range_targets(tmp_path, kwargs):
    source = tmp_path / "mix.wav"
    source.write_bytes(b"placeholder")
    with pytest.raises(ValueError, match="LUFS target"):
        audio_timeline.normalize_loudness_file(source, **kwargs)

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


def test_quality_report_blocks_true_peak_over_configured_ceiling():
    samples = np.full((800, 2), 0.1, dtype=np.float32)
    report = audio_timeline.build_audio_quality_report(
        samples, sample_rate=8000,
        measured_true_peak_dbTP=-0.4,
        target_true_peak_dbTP=-1.0,
    )
    assert report["status"] == "blocked"
    assert report["export_allowed"] is False
    assert report["true_peak_dbTP"] == -0.4
    assert any(item["code"] == "true_peak_target_exceeded" for item in report["warnings"])


def test_quality_report_accepts_true_peak_within_tolerance():
    samples = np.full((800, 2), 0.1, dtype=np.float32)
    report = audio_timeline.build_audio_quality_report(
        samples, sample_rate=8000,
        measured_true_peak_dbTP=-0.9,
        target_true_peak_dbTP=-1.0,
    )
    assert report["export_allowed"] is True
    assert report["true_peak_dbTP"] == -0.9


def test_measure_encoded_audio_parses_decoded_stream_loudness(monkeypatch, tmp_path):
    from modules.ai_video_studio.media import audio_timeline
    media = tmp_path / "final.mp4"
    media.write_bytes(b"fake mp4")
    monkeypatch.setattr(audio_timeline.shutil, "which", lambda name: "/usr/bin/ffmpeg")
    class Result:
        returncode = 0
        stderr = """frame=1
{
 "input_i" : "-14.2",
 "input_tp" : "-1.3",
 "input_lra" : "4.1"
}
"""
    monkeypatch.setattr(audio_timeline.subprocess, "run", lambda *args, **kwargs: Result())
    report = audio_timeline.measure_encoded_audio(media)
    assert report["verified"] is True
    assert report["measured"]["integrated_lufs"] == -14.2
    assert report["measured"]["true_peak_dbTP"] == -1.3


def test_mix_audio_timeline_ducks_music_for_asset_backed_narration(tmp_path, monkeypatch):
    downloads = _audio_roots(tmp_path, monkeypatch)
    sample_rate = 8000
    voice_path = downloads / "voice" / "spoken.wav"
    music_path = downloads / "music" / "bed.wav"
    voice_path.parent.mkdir(parents=True, exist_ok=True)
    music_path.parent.mkdir(parents=True, exist_ok=True)
    dsp.write_audio(voice_path, np.full(sample_rate, 0.2, dtype=np.float32), sample_rate=sample_rate)
    dsp.write_audio(music_path, np.full(sample_rate * 2, 0.2, dtype=np.float32), sample_rate=sample_rate)
    output = tmp_path / "asset_ducking.wav"

    result = audio_timeline.mix_audio_timeline(
        [
            {"asset": str(music_path), "start": 0, "end": 2, "kind": "music"},
            {"asset": str(voice_path), "start": 0.5, "end": 1.5, "kind": "narration"},
        ],
        output, total_duration=2, sample_rate=sample_rate,
        ducking_db=12, ducking_threshold_db=-40, ducking_attack=0.01, ducking_release=0.05,
        normalization_enabled=False,
    )
    mixed, _ = dsp.read_audio(output, target_sr=sample_rate)
    before = np.sqrt(np.mean(mixed[int(0.1 * sample_rate):int(0.4 * sample_rate)] ** 2))
    during_with_voice = mixed[int(0.9 * sample_rate):int(1.2 * sample_rate)]
    during_music = during_with_voice - 0.2
    during = np.sqrt(np.mean(during_music ** 2))
    assert result["ducking"]["speech_detected"] is True
    assert result["clips"][0]["ducking_applied"] is True
    assert during < before * 0.4


def test_mix_audio_timeline_downmixes_multichannel_music_to_stereo(tmp_path, monkeypatch):
    _audio_roots(tmp_path, monkeypatch)
    multichannel = np.zeros((8000, 8), dtype=np.float32)
    multichannel[:, 0] = 0.2
    multichannel[:, 1] = 0.1
    multichannel[:, 2] = 0.05
    result = audio_timeline.mix_audio_timeline(
        [{"samples": multichannel, "kind": "music", "start": 0, "end": 1}],
        tmp_path / "multichannel_mix.wav",
        total_duration=1,
        sample_rate=8000,
        ducking_enabled=False,
        normalization_enabled=False,
    )
    rendered, rate = dsp.read_audio(tmp_path / "multichannel_mix.wav", target_sr=8000, preserve_channels=True)
    assert rate == 8000
    assert rendered.shape == (8000, 2)
    assert np.mean(rendered[:, 0]) > np.mean(rendered[:, 1])
    assert result["channels"] == 2
