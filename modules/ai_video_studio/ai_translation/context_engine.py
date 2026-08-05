"""Context Engine — packs surrounding sentences as context for better translation."""
from __future__ import annotations

import re

_SENTENCE_RE = re.compile(r"[^.!?…]+[.!?…]*")


def window(sentences: list[str], index: int, *, radius: int = 1) -> dict[str, str]:
    """Return ``{previous, current, next}`` context around ``sentences[index]``."""
    prev_text = " ".join(sentences[max(0, index - radius):index])
    nxt_text = " ".join(sentences[index + 1:index + 1 + radius])
    return {
        "previous": prev_text.strip(),
        "current": sentences[index] if 0 <= index < len(sentences) else "",
        "next": nxt_text.strip(),
    }


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_RE.findall(text) if s.strip()]


def build_prompt(sentences: list[str], index: int, source: str, target: str,
                 *, radius: int = 1) -> str:
    """Build an LLM prompt that includes neighbouring context."""
    ctx = window(sentences, index, radius=radius)
    parts = [f"Translate this {source} sentence to {target}. Preserve tone and length."]
    if ctx["previous"]:
        parts.append(f"Previous context: {ctx['previous']}")
    if ctx["next"]:
        parts.append(f"Following context: {ctx['next']}")
    parts.append(f"Sentence: {ctx['current']}")
    parts.append("Reply with ONLY the translation.")
    return "\n".join(parts)
