"""Multilingual TTS — resolves the best voice for any target language."""
from __future__ import annotations

from modules.ai_video_studio.ai_voice_studio.synthesis.tts_engine import get_tts_engine

# Language → (gTTS code, example edge-tts voice) for quick capability lookup.
LANGUAGE_TABLE: dict[str, dict[str, str]] = {
    "en": {"gtts": "en", "edge": "en-US-AriaNeural"},
    "pt": {"gtts": "pt", "edge": "pt-BR-FranciscaNeural"},
    "es": {"gtts": "es", "edge": "es-ES-ElviraNeural"},
    "fr": {"gtts": "fr", "edge": "fr-FR-DeniseNeural"},
    "de": {"gtts": "de", "edge": "de-DE-KatjaNeural"},
    "it": {"gtts": "it", "edge": "it-IT-ElsaNeural"},
    "ja": {"gtts": "ja", "edge": "ja-JP-NanamiNeural"},
    "zh": {"gtts": "zh-CN", "edge": "zh-CN-XiaoxiaoNeural"},
    "ko": {"gtts": "ko", "edge": "ko-KR-SunHiNeural"},
    "ru": {"gtts": "ru", "edge": "ru-RU-SvetlanaNeural"},
    "ar": {"gtts": "ar", "edge": "ar-SA-ZariyahNeural"},
    "hi": {"gtts": "hi", "edge": "hi-IN-SwaraNeural"},
    "nl": {"gtts": "nl", "edge": "nl-NL-ColetteNeural"},
    "pl": {"gtts": "pl", "edge": "pl-PL-ZofiaNeural"},
    "sv": {"gtts": "sv", "edge": "sv-SE-SofieNeural"},
    "tr": {"gtts": "tr", "edge": "tr-TR-EmelNeural"},
}

SUPPORTED_LANGUAGES = sorted(LANGUAGE_TABLE)


def normalize_language(language: str) -> str:
    """Map a BCP-47 code to our table key ('' when unsupported)."""
    lang = language.lower().split("-")[0]
    return lang if lang in LANGUAGE_TABLE else ""


def is_supported(language: str) -> bool:
    return bool(normalize_language(language))


def voice_for_language(language: str) -> str:
    """Catalog voice id whose language matches, else 'default'."""
    lang = normalize_language(language)
    if not lang:
        return "default"
    for voice in get_tts_engine().list_voices():
        if voice["language"].lower().startswith(lang):
            return voice["id"]
    return "default"


def list_languages() -> list[str]:
    return SUPPORTED_LANGUAGES
