from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from .language_detector import LanguageDetector
from .translator import Translator
from .localization import Localizer


@dataclass
class EngineConfig:
    default_source_language: str = "auto"
    default_target_language: str = "en"
    localization_locale: str = "en-US"
    cache_enabled: bool = True


@dataclass
class EngineState:
    running: bool = False
    started_at: Optional[datetime] = None
    current_locale: str = "en-US"


@dataclass
class EngineMetrics:
    total_translations: int = 0
    total_detections: int = 0
    total_localizations: int = 0
    avg_translation_time_ms: float = 0.0
    errors: int = 0
    supported_languages_count: int = 0


class TranslationEngine:
    def __init__(self, config: Optional[EngineConfig] = None) -> None:
        self.config = config or EngineConfig()
        self.state = EngineState()
        self.metrics = EngineMetrics()
        self.detector = LanguageDetector()
        self.translator = Translator()
        self.localizer = Localizer()
        self._cache: dict[str, str] = {}

    async def initialize(self) -> None:
        self.state.running = True
        self.state.started_at = datetime.now()
        self.state.current_locale = self.config.localization_locale
        self.metrics.supported_languages_count = len(self.detector.get_supported_languages())

    async def stop(self) -> None:
        self.state.running = False

    async def detect_language(self, text: str) -> dict[str, Any]:
        if not self.state.running:
            raise RuntimeError("TranslationEngine is not running")
        self.metrics.total_detections += 1
        lang = self.detector.detect_language(text)
        confidence = self.detector.get_confidence(text)
        return {"language": lang, "confidence": confidence, "text": text[:50]}

    async def translate(
        self, text: str, source: str = "auto", target: str = "en"
    ) -> dict[str, Any]:
        if not self.state.running:
            raise RuntimeError("TranslationEngine is not running")

        cache_key = f"{source}:{target}:{text}"
        if cache_key in self._cache and self.config.cache_enabled:
            return {"translated_text": self._cache[cache_key], "cached": True, "source": source, "target": target}

        self.metrics.total_translations += 1

        if source == "auto":
            source = self.detector.detect_language(text)

        translated = self.translator.translate(text, source, target)
        self._cache[cache_key] = translated
        return {"translated_text": translated, "cached": False, "source": source, "target": target}

    async def localize(self, content: str, locale: Optional[str] = None) -> dict[str, Any]:
        if not self.state.running:
            raise RuntimeError("TranslationEngine is not running")
        self.metrics.total_localizations += 1
        target_locale = locale or self.state.current_locale
        localized = self.localizer.localize_content(content, target_locale)
        return {"localized_content": localized, "locale": target_locale}

    async def get_supported_languages(self) -> list[str]:
        return self.detector.get_supported_languages()
