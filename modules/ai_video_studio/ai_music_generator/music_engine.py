"""Music Engine — composes and renders real music (WAV/MP3).

Pipeline: genre spec (bpm/key/progression/instruments) → song structure
(chords, bass, melody, drums) → instrument rendering (numpy synthesis) →
mixing → mastering → file. Output is always a real audio file.
"""
from __future__ import annotations

import logging
import math
import random
from pathlib import Path
from typing import Any

import numpy as np

from modules.ai_video_studio.media import dsp
from modules.ai_video_studio.media.output_paths import get_subsystem_dir, unique_filename
from modules.ai_video_studio.ai_music_generator.music_models import Note, Track, Song
from modules.ai_video_studio.ai_music_generator import music_library as lib
from modules.ai_video_studio.ai_music_generator.genres import get_genre, list_genres
from modules.ai_video_studio.ai_music_generator.instruments import get_instrument, available_instruments
from modules.ai_video_studio.ai_music_generator.music_scheduler import MusicScheduler
from modules.ai_video_studio.ai_music_generator.music_optimizer import MusicOptimizer
from modules.ai_video_studio.ai_music_generator.music_learning import MusicLearning

logger = logging.getLogger(__name__)

_MUSIC = None


def get_music_engine() -> MusicEngine:
    global _MUSIC
    if _MUSIC is None:
        _MUSIC = MusicEngine()
    return _MUSIC


# Chord instruments play block chords; lead instruments play a melody.
_CHORD_INSTRUMENTS = {"piano", "guitar", "synthesizer", "synth", "choir", "cello", "organ"}
_LEAD_INSTRUMENTS = {"violin", "flute", "trumpet", "fiddle"}


class MusicEngine:
    """Composes and renders music for a genre."""

    def __init__(self) -> None:
        self.scheduler = MusicScheduler()
        self.optimizer = MusicOptimizer()
        self.learning = MusicLearning()

    def list_genres(self) -> list[str]:
        return list_genres()

    def list_instruments(self) -> list[str]:
        return available_instruments()

    # ── Main entry ────────────────────────────────────────────────
    def generate(
        self,
        genre: str = "cinematic",
        *,
        duration: float = 20.0,
        bpm: float | None = None,
        key: str | None = None,
        output_path: str | None = None,
        seed: int = 7,
    ) -> dict[str, Any]:
        """Generate a real music file for a genre."""
        spec = get_genre(genre)
        bpm = bpm or float(spec["bpm"])
        root = key or str(spec["root"])
        scale = str(spec["scale"])
        bars = max(2, int(math.ceil(duration / lib.bar_duration(bpm))))

        song = self._compose(spec, root, scale, bars, bpm, seed)
        track_names = self.scheduler.schedule([t.instrument for t in song.tracks])

        buffers: dict[str, np.ndarray] = {}
        for idx, track in enumerate(song.tracks):
            buffers[track.instrument] = self._render_track(track, bpm, spec, sample_rate=dsp.SAMPLE_RATE)
            self.scheduler.report(done=idx + 1, total=len(track_names), track=track.instrument)

        # Mix all tracks with per-instrument gains.
        tracks_mix: list[dict[str, Any]] = []
        for instrument, buffer in buffers.items():
            gain = 0.6 if instrument == "drums" else (0.5 if instrument == "bass" else 0.35)
            tracks_mix.append({"samples": buffer, "offset": 0.0, "gain": gain})
        mix = dsp.mix_tracks(tracks_mix, total_duration=duration)
        mix = dsp.limiter(mix, 0.96)
        mix = dsp.normalize_peak(mix, 0.95)
        mix = dsp.fade_io(mix, fade_in=0.02, fade_out=0.4)

        out_dir = Path(output_path).parent if output_path else get_subsystem_dir("music")
        out_path = output_path or str(unique_filename(out_dir, f"music_{genre}", "wav"))
        dsp.write_audio(out_path, mix)
        self.learning.record_generation(genre, round(len(mix) / dsp.SAMPLE_RATE, 2))

        return {
            "output_path": out_path,
            "bytes": int(Path(out_path).stat().st_size),
            "duration": round(len(mix) / dsp.SAMPLE_RATE, 3),
            "genre": spec["name"],
            "bpm": bpm,
            "key": f"{root} {scale}",
            "bars": bars,
            "tracks": [t.to_dict() for t in song.tracks],
            "instruments": track_names,
        }

    # ── Composition ───────────────────────────────────────────────
    def _compose(self, spec: dict, root: str, scale: str, bars: int,
                 bpm: float, seed: int) -> Song:
        progression = spec["progression"]
        instruments = spec["instruments"]
        beats_per_bar = 4
        song = Song(title=f"{spec['name']} sketch", genre=spec["name"],
                    bpm=bpm, key=f"{root} {scale}", bars=bars)

        rng = random.Random(seed)

        # Chords for every bar.
        bar_chords: list[list[str]] = []
        for bar in range(bars):
            degree, quality = progression[bar % len(progression)]
            bar_chords.append(lib.chord_for_degree(root, scale, int(degree), str(quality)))

        for instrument in instruments:
            notes: list[Note] = []
            if instrument == "drums":
                notes = self._drum_notes(spec, bars, beats_per_bar, rng)
            elif instrument == "bass":
                notes = self._bass_notes(bar_chords, bars, beats_per_bar, spec, rng)
            elif instrument in _LEAD_INSTRUMENTS:
                notes = self._lead_notes(bar_chords, bars, beats_per_bar, spec, rng, instrument)
            else:
                notes = self._chord_notes(bar_chords, bars, beats_per_bar, spec, instrument, rng)
            notes = self.optimizer.dedupe(notes)
            song.tracks.append(Track(instrument=instrument, notes=notes))
        return song

    def _chord_notes(self, bar_chords, bars, beats, spec, instrument, rng) -> list[Note]:
        notes: list[Note] = []
        density = float(spec.get("density", 0.7))
        arpeggio = bool(spec.get("arpeggio", False))
        octave_offset = -1 if instrument in ("cello",) else 0
        for bar, chord in enumerate(bar_chords):
            start_beat = bar * beats
            if arpeggio:
                step = beats / max(2, len(chord))
                for i, tone in enumerate(chord):
                    dur = step * 0.9
                    notes.append(Note(_shift(tone, octave_offset), start_beat + i * step, dur,
                                      velocity=0.5 + 0.3 * density, instrument=instrument))
            else:
                for i, tone in enumerate(chord):
                    dur = beats * 0.95
                    if density > 0.6:
                        dur = beats * (0.5 if i % 2 == 1 else 0.95)
                    notes.append(Note(_shift(tone, octave_offset), start_beat, dur,
                                      velocity=0.4 + 0.4 * density, instrument=instrument))
        return notes

    def _bass_notes(self, bar_chords, bars, beats, spec, rng) -> list[Note]:
        notes: list[Note] = []
        pattern = spec.get("bass_pattern", "root_four")
        for bar, chord in enumerate(bar_chords):
            start_beat = bar * beats
            root = chord[0]
            low_root = _shift(root, -2)
            if pattern == "root_eighth":
                for step in range(0, beats * 2):
                    pitch = low_root if step % 2 == 0 else _shift(root, -2)
                    notes.append(Note(pitch, start_beat + step * 0.5, 0.45, velocity=0.7))
            else:  # root_four — root on 1 and 3
                notes.append(Note(low_root, start_beat, 1.9, velocity=0.75))
                notes.append(Note(_shift(root, -2), start_beat + 2, 1.9, velocity=0.7))
        return notes

    def _lead_notes(self, bar_chords, bars, beats, spec, rng, instrument: str) -> list[Note]:
        notes: list[Note] = []
        # Deterministic melodic contour over chord tones: 0, 2, 3, 2 pattern.
        contour = [0, 2, 3, 2, 1, 3, 2, 0]
        density = float(spec.get("density", 0.6))
        notes_per_bar = int(4 if density > 0.65 else 2)
        step = beats / notes_per_bar
        pos = 0
        for bar, chord in enumerate(bar_chords):
            start_beat = bar * beats
            for i in range(notes_per_bar):
                if rng.random() < 0.2:
                    pos += 1
                    continue
                tone = chord[contour[pos % len(contour)] % len(chord)]
                pos += 1
                notes.append(Note(_shift(tone, 1), start_beat + i * step, step * 0.85,
                                  velocity=0.6 + 0.3 * density, instrument=instrument))
        return notes

    def _drum_notes(self, spec, bars, beats, rng) -> list[Note]:
        notes: list[Note] = []
        pattern = spec.get("drums_pattern", "backbeat")
        swing = float(spec.get("swing", 0.0))
        for bar in range(bars):
            start = bar * beats
            if pattern in ("none",):
                continue
            if pattern == "four_on_floor":
                for b in range(4):
                    notes.append(Note("kick", start + b, 0.9, velocity=0.9))
                notes.append(Note("snare", start + 1, 0.9))
                notes.append(Note("snare", start + 3, 0.9))
                self._hihats(notes, start, beats, swing)
            elif pattern == "backbeat":
                notes.append(Note("kick", start, 0.9, velocity=0.9))
                notes.append(Note("kick", start + 2, 0.9, velocity=0.85))
                notes.append(Note("snare", start + 1, 0.9))
                notes.append(Note("snare", start + 3, 0.9))
                self._hihats(notes, start, beats, swing)
            elif pattern == "trap":
                notes.append(Note("kick", start, 0.9, velocity=0.95))
                notes.append(Note("kick", start + 2.5, 0.9, velocity=0.8))
                notes.append(Note("snare", start + 1.5, 0.9))
                notes.append(Note("snare", start + 3.5, 0.9))
                self._hihats(notes, start, beats, swing)
            elif pattern == "swing":
                notes.append(Note("kick", start, 0.9, velocity=0.85))
                notes.append(Note("kick", start + 2, 0.9, velocity=0.8))
                notes.append(Note("snare", start + 1, 0.9))
                notes.append(Note("snare", start + 3, 0.9))
                for step in range(8):
                    offset = 0.5 * swing if step % 2 else 0.0
                    notes.append(Note("hihat", start + step * 0.5 + offset, 0.4, velocity=0.35))
            elif pattern == "shuffle":
                for step in range(8):
                    notes.append(Note("kick" if step % 2 == 0 else "snare",
                                      start + step * 0.5 + (0.17 if step % 2 else 0.0),
                                      0.4, velocity=0.8))
            elif pattern == "pulse":
                for b in range(4):
                    notes.append(Note("kick", start + b, 0.5, velocity=0.7))
            else:
                notes.append(Note("kick", start, 0.9, velocity=0.8))
        return notes

    @staticmethod
    def _hihats(notes: list[Note], start: float, beats: int, swing: float) -> None:
        for step in range(int(beats * 2)):
            offset = 0.5 * swing if step % 2 else 0.0
            notes.append(Note("hihat", start + step * 0.5 + offset, 0.35, velocity=0.3))

    # ── Rendering ─────────────────────────────────────────────────
    def _render_track(self, track: Track, bpm: float, spec: dict, *, sample_rate: int) -> np.ndarray:
        beats_to_sec = 60.0 / bpm
        total_sec = 0.0
        for note in track.notes:
            end = (note.start + note.duration) * beats_to_sec
            total_sec = max(total_sec, end)
        buffer_len = int(total_sec * sample_rate) + sample_rate // 4
        buffer = np.zeros(buffer_len, dtype=np.float64)
        cache: dict[str, np.ndarray] = {}
        render_fn = get_instrument(track.instrument)

        for note in track.notes:
            freq = 0.0
            if note.name not in ("kick", "snare", "hihat", "clap", "tom"):
                freq = lib.note_frequency(note.name)
            dur = max(0.08, note.duration * beats_to_sec)
            key = f"{note.instrument}:{note.name}:{round(note.velocity, 2)}"
            if key not in cache:
                cache[key] = render_fn(note.name, freq, dur, amplitude=note.velocity,
                                       sample_rate=sample_rate)
            start = int(note.start * beats_to_sec * sample_rate)
            end = min(buffer_len, start + len(cache[key]))
            if end > start:
                buffer[start:end] += cache[key][: end - start]

        if "drums" in track.instrument:
            return buffer.astype(np.float32)
        # Slight master low-pass on melodic tracks for cohesion.
        return dsp.one_pole_lp(buffer, 12000.0, sample_rate=sample_rate).astype(np.float32)


def _shift(note_name: str, octaves: int) -> str:
    from modules.ai_video_studio.ai_music_generator import music_library as _lib

    idx = _lib.note_index(note_name) + octaves * 12
    return _lib.note_from_semitone(idx)
