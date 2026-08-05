"""Pronunciation Validator — flags words that may be mispronounced."""
from __future__ import annotations

import re

from modules.ai_video_studio.ai_voice_studio.synthesis.pronunciation_engine import PRONUNCIATIONS

# Foreign/acronym-heavy words are common sources of TTS mispronunciation.
_RISK_PATTERNS = [
    re.compile(r"\b[A-Z]{3,}\b"),                      # acronyms
    re.compile(r"\b\w+\d+\w*\b"),                       # alphanumerics
    re.compile(r"\b[a-z]+\.[a-z]+\b"),                  # dotted words
]


def validate_line(text: str) -> dict:
    """Return ``{risky, words, suggestion}`` for a line."""
    risky: set[str] = set()
    for pattern in _RISK_PATTERNS:
        risky.update(pattern.findall(text))
    covered = [w for w in risky if w.lower() in PRONUNCIATIONS]
    return {
        "risky": sorted(risky),
        "covered_by_pronunciations": covered,
        "needs_attention": [w for w in risky if w.lower() not in PRONUNCIATIONS],
    }


def report(lines: list[str]) -> dict:
    flagged: list[dict] = []
    for i, line in enumerate(lines):
        result = validate_line(line)
        if result["needs_attention"]:
            flagged.append({"index": i, "line": line, **result})
    return {"lines_checked": len(lines), "flagged": flagged}
