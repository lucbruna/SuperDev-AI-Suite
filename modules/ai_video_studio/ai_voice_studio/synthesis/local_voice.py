"""Select an installed OS TTS voice matching the requested language."""
from __future__ import annotations

import re
from typing import Any


_LOCALE_IDS = {
    "pt-br": ("0416", "ptbr", "portuguese (brazil)", "portuguese brazil"),
    "pt-pt": ("0816", "ptpt", "portuguese (portugal)", "portuguese portugal"),
    "en-us": ("0409", "enus", "english (united states)", "english united states"),
    "en-gb": ("0809", "engb", "english (united kingdom)", "english united kingdom"),
    "es-es": ("0c0a", "eses", "spanish (spain)", "spanish spain"),
}


def _voice_text(value: Any) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore").lower()
    if isinstance(value, (list, tuple, set)):
        return " ".join(_voice_text(item) for item in value)
    return str(value or "").lower()


def select_local_voice(engine: Any, language: str, voice_id: str = "default") -> str:
    """Set a matching installed voice or fail rather than silently speak another language."""
    requested = (language or "").replace("_", "-").lower()
    voices = engine.getProperty("voices") or []
    if not requested:
        return ""

    candidates = _LOCALE_IDS.get(requested, ())
    base = requested.split("-", 1)[0]
    for voice in voices:
        metadata = " ".join(
            _voice_text(getattr(voice, key, ""))
            for key in ("id", "name", "languages")
        )
        normalized = re.sub(r"[^a-z0-9]+", "", metadata)
        matched = any(
            token in metadata or re.sub(r"[^a-z0-9]+", "", token) in normalized
            for token in candidates
        )
        if not matched and requested == base:
            matched = re.search(rf"(^|[^a-z]){re.escape(base)}([^a-z]|$)", metadata) is not None
        if matched:
            voice_token = str(getattr(voice, "id", "") or "")
            if voice_token:
                engine.setProperty("voice", voice_token)
            return voice_token

    raise RuntimeError(
        f"No installed offline voice matches {language}. "
        "Install a Windows/macOS/Linux speech voice for this language or use online TTS."
    )
