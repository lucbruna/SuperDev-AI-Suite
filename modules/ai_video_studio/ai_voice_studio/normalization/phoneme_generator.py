"""Phoneme Generator — rough grapheme-to-phoneme mapping and syllable counts.

Used by the lip-sync subsystem to turn narration text into a phoneme
timeline. It is a deterministic approximation (not a learned G2P model),
good enough to drive visemes.
"""
from __future__ import annotations

import re

# English grapheme → ARPABET-ish phoneme approximations.
_MAP = {
    "a": "AA", "e": "EH", "i": "IH", "o": "AA", "u": "AH",
    "b": "B", "c": "K", "d": "D", "f": "F", "g": "G", "h": "HH",
    "j": "JH", "k": "K", "l": "L", "m": "M", "n": "N", "p": "P",
    "q": "K", "r": "R", "s": "S", "t": "T", "v": "V", "w": "W",
    "x": "K S", "y": "Y", "z": "Z",
}

_DIPHTHONGS = {
    "ai": "AY", "ay": "EY", "ee": "IY", "ea": "IY", "oa": "OW",
    "oo": "UW", "ou": "AW", "oi": "OY", "oy": "OY", "au": "AW",
    "aw": "AO", "ei": "EY", "ie": "AY", "igh": "AY", "ough": "AO",
}

_VOWELS = set("aeiouy")
_WORD_RE = re.compile(r"[a-zA-Z']+")


def word_to_phonemes(word: str) -> list[str]:
    """Return a list of phoneme tokens for an English-ish word."""
    word = word.lower().strip("'")
    if not word:
        return []
    phonemes: list[str] = []
    i = 0
    while i < len(word):
        matched = False
        for length in (4, 3, 2):
            if i + length <= len(word) and word[i:i + length] in _DIPHTHONGS:
                phonemes.append(_DIPHTHONGS[word[i:i + length]])
                i += length
                matched = True
                break
        if matched:
            continue
        phonemes.append(_MAP.get(word[i], " " if word[i] == "'" else "AH"))
        i += 1
    return [p for p in phonemes if p != " "]


def text_to_phonemes(text: str) -> list[str]:
    """Convert full text to a flat phoneme list."""
    phonemes: list[str] = []
    for match in _WORD_RE.finditer(text):
        phonemes.extend(word_to_phonemes(match.group(0)))
        phonemes.append("PAUSE")
    return phonemes


def count_syllables(word: str) -> int:
    """Heuristic syllable count: vowel groups in the word."""
    word = word.lower().strip("'")
    groups = re.findall(r"[aeiouy]+", word)
    count = len(groups)
    if word.endswith("e") and count > 1:
        count -= 1
    return max(1, count)


def phoneme_duration(phoneme: str, *, speaking_rate: float = 1.0) -> float:
    """Average duration (seconds) of a phoneme at the given speaking rate."""
    if phoneme == "PAUSE":
        return 0.10 / max(0.25, speaking_rate)
    if phoneme in {"AA", "AY", "EY", "IY", "OW", "UW", "AW", "OY", "AO"}:
        return 0.12 / max(0.25, speaking_rate)
    if phoneme in {"S", "Z", "SH", "ZH", "F", "V", "TH", "DH"}:
        return 0.08 / max(0.25, speaking_rate)
    return 0.06 / max(0.25, speaking_rate)
