"""Quality Checker — scores translation quality without a reference.

Heuristics: length ratio sanity, glossary coverage, punctuation retention,
repetition, and character balance for CJK.
"""
from __future__ import annotations

import re


def _words(text: str) -> int:
    return len(re.findall(r"[\w'-]+", text))


def score_translation(source: str, translated: str, *, source_lang: str = "en",
                      target_lang: str = "", glossary_hits: int = 0, glossary_terms: int = 0) -> dict:
    """Return ``{score, checks}`` (0-100)."""
    checks: list[dict] = []
    score = 100.0

    def _penalty(amount: float, name: str, detail: str) -> None:
        nonlocal score
        score -= amount
        checks.append({"check": name, "detail": detail})

    s_words = max(1, _words(source))
    t_words = _words(translated)
    if t_words == 0:
        _penalty(40, "empty_output", "translation is empty")

    ratio = t_words / s_words
    if ratio < 0.3 or ratio > 3.0:
        _penalty(25, "length_ratio", f"word ratio {ratio:.2f} outside 0.3-3.0")

    src_punct = len(re.findall(r"[.!?]", source))
    tgt_punct = len(re.findall(r"[.!?]", translated))
    if src_punct > 0 and tgt_punct == 0:
        _penalty(10, "punctuation", "sentence punctuation lost")

    # CJK targets should not inflate word counts.
    if target_lang in ("zh", "ja", "ko") and t_words > s_words * 2.5:
        _penalty(10, "cjk_ratio", "target looks too long for a CJK language")

    if glossary_terms:
        coverage = glossary_hits / glossary_terms
        if coverage < 0.5:
            _penalty(15 * (1 - coverage), "glossary", f"glossary coverage {coverage:.0%}")

    repeats = len(set(re.findall(r"\b(\w{6,})\b", translated))) / max(1, t_words)
    if repeats < 0.05:
        _penalty(5, "repetition", "suspiciously little lexical variety")

    return {
        "score": round(max(0.0, min(100.0, score)), 1),
        "checks": checks,
        "words_source": s_words,
        "words_target": t_words,
    }
