"""AI Translation — real multilingual translation for the studio (Volume 4).

Ollama-driven AI translation with glossary, terminology protection,
translation memory and deterministic fallbacks so translation never fails.
"""
from modules.ai_video_studio.ai_translation.translation_engine import TranslationEngine, get_translation_engine
from modules.ai_video_studio.ai_translation.language_detector import detect_language
from modules.ai_video_studio.ai_translation.glossary_manager import GlossaryManager
from modules.ai_video_studio.ai_translation.localization_engine import LocalizationEngine

__all__ = [
    "TranslationEngine",
    "get_translation_engine",
    "detect_language",
    "GlossaryManager",
    "LocalizationEngine",
]
