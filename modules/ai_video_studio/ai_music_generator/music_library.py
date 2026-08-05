"""Music Library — note frequencies, scales and chord tone helpers."""
from __future__ import annotations


NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

_SCALES: dict[str, list[int]] = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "natural_minor": [0, 2, 3, 5, 7, 8, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "pentatonic_major": [0, 2, 4, 7, 9],
    "pentatonic_minor": [0, 3, 5, 7, 10],
    "minor_pentatonic": [0, 3, 5, 7, 10],  # alias used by blues
    "chromatic": list(range(12)),
}

# chord quality → semitone offsets from the root
_QUALITIES: dict[str, list[int]] = {
    "major": [0, 4, 7],
    "minor": [0, 3, 7],
    "dim": [0, 3, 6],
    "aug": [0, 4, 8],
    "major7": [0, 4, 7, 11],
    "minor7": [0, 3, 7, 10],
    "dom7": [0, 4, 7, 10],
    "sus4": [0, 5, 7],
}


def note_index(name: str) -> int:
    """Map a note name like ``D#3`` to a semitone index (0 = C0)."""
    name = name.strip()
    pitch = name[:-1]
    octave = int(name[-1]) if name[-1].isdigit() else 4
    semitone = NOTE_NAMES.index(pitch) if pitch in NOTE_NAMES else 0
    return octave * 12 + semitone


def note_frequency(name: str) -> float:
    """Frequency (Hz) of a note name; A4 = 440 Hz.

    ``note_index`` maps C0 → 0, so A4 = 57 (not MIDI 69). The reference
    semitone must therefore be 57 — using 69 shifted every note an octave
    low.
    """
    index = note_index(name)
    return 440.0 * 2 ** ((index - 57) / 12.0)


def note_from_semitone(semitone: int) -> str:
    octave = semitone // 12
    name = NOTE_NAMES[semitone % 12]
    return f"{name}{octave}"


def scale_notes(root: str, scale: str) -> list[str]:
    """Note names in a scale starting at ``root`` (one octave, 7 pitches)."""
    root_idx = note_index(root)
    offsets = _SCALES.get(scale, _SCALES["major"])
    return [note_from_semitone(root_idx + o) for o in offsets]


def chord_tones(root: str, quality: str) -> list[str]:
    """Note names for a chord (root + quality)."""
    root_idx = note_index(root)
    return [note_from_semitone(root_idx + o) for o in _QUALITIES.get(quality, _QUALITIES["major"])]


def scale_degree_note(root: str, scale: str, degree: int) -> str:
    """The ``degree``-th (0-based) note of a scale rooted at ``root``."""
    notes = scale_notes(root, scale)
    return notes[degree % len(notes)]


def chord_for_degree(root: str, scale: str, degree: int, quality: str) -> list[str]:
    """Chord tones built on the ``degree`` scale note."""
    degree_note = scale_degree_note(root, scale, degree)
    return chord_tones(degree_note, quality)


def beat_duration(bpm: float) -> float:
    """Seconds per beat."""
    return 60.0 / max(1.0, bpm)


def bar_duration(bpm: float, beats_per_bar: int = 4) -> float:
    return beat_duration(bpm) * beats_per_bar
