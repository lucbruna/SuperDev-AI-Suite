"""Translation Engine — real AI translation with layered fallbacks.

1. Local **Ollama** (real AI translation, works offline).
2. Platform ``LLMClient`` (services/ai_studio) when a provider is set.
3. Glossary + memory (deterministic, always works).

Output is never a failure: worst case returns the source text with a
``fallback`` marker. Glossary terms and translation memory are always applied.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from modules.ai_video_studio.core.exceptions import ValidationError
from modules.ai_video_studio.ai_translation.language_detector import detect_language
from modules.ai_video_studio.ai_translation.glossary_manager import GlossaryManager
from modules.ai_video_studio.ai_translation.terminology_engine import TerminologyEngine
from modules.ai_video_studio.ai_translation.multilingual_memory import MultilingualMemory
from modules.ai_video_studio.ai_translation.quality_checker import score_translation

logger = logging.getLogger(__name__)

_TRANSLATION = None


def get_translation_engine() -> TranslationEngine:
    global _TRANSLATION
    if _TRANSLATION is None:
        _TRANSLATION = TranslationEngine()
    return _TRANSLATION


class TranslationEngine:
    """Translates text between languages with layered providers."""

    def __init__(self) -> None:
        self.glossary = GlossaryManager()
        self.terminology = TerminologyEngine(self.glossary)
        self.memory = MultilingualMemory()

    # ── Public API ────────────────────────────────────────────────
    def translate(self, text: str, target: str, *, source: str | None = None,
                  use_memory: bool = True, use_llm: bool = True,
                  provider_timeout: float = 90.0) -> dict[str, Any]:
        """Translate ``text`` to ``target``; returns ``{text, engine, ...}``."""
        if not text or not text.strip():
            raise ValidationError("Cannot translate empty text", field="text")
        source = source or detect_language(text) or "en"
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.translate_async(
                text, target, source=source, use_memory=use_memory, use_llm=use_llm,
                provider_timeout=provider_timeout,
            ))
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(
                asyncio.run,
                self.translate_async(
                    text, target, source=source, use_memory=use_memory, use_llm=use_llm,
                    provider_timeout=provider_timeout,
                ),
            ).result()

    async def translate_async(self, text: str, target: str, *, source: str | None = None,
                              use_memory: bool = True, use_llm: bool = True,
                              provider_timeout: float = 90.0) -> dict[str, Any]:
        source = source or detect_language(text) or "en"

        if use_memory:
            cached = self.memory.get(source, target, text)
            if cached:
                return {"text": cached, "engine": "memory", "source": source,
                        "target": target, "cached": True}

        # Protect glossary terms, then try the LLM providers.
        protected_text, protected = self.terminology.protect(text, source, target)

        result: dict[str, Any] = {"source": source, "target": target, "cached": False}
        if use_llm:
            translated = await self._try_ollama(protected_text, source, target, timeout=provider_timeout) or \
                await self._try_platform(protected_text, source, target)
        else:
            translated = None
        if translated:
            translated = self.terminology.restore(translated, protected, source, target)
            result.update({"text": translated, "engine": result.get("engine") or "llm"})
            quality = score_translation(text, translated, source_lang=source, target_lang=target)
            result["quality"] = quality["score"]
            if use_memory:
                self.memory.store(source, target, text, translated)
            return result

        # Deterministic fallback: glossary + memory + original text.
        fallback = self.glossary.apply(text, source, target)
        if not fallback or fallback == text:
            fallback = self._phrase_fallback(text, source, target)
        result.update({"text": fallback, "engine": "fallback", "quality": 0.0})
        return result

    # ── Providers ─────────────────────────────────────────────────
    async def _try_ollama(self, text: str, source: str, target: str, *, timeout: float) -> str | None:
        try:
            from modules.ai_video_studio.media.llm import generate_text

            response = await asyncio.to_thread(
                generate_text,
                f"Translate from {source} to {target}:\n\n{text}",
                system=(
                    "You are a professional translator. Reply with ONLY the translated "
                    "text, no quotes, no commentary, no markdown."
                ),
                temperature=0.2,
                timeout=timeout,
                max_tokens=512,
            )
            cleaned = response.strip().strip('"').strip()
            if cleaned and not cleaned.lower().startswith("error"):
                return cleaned
        except Exception as e:  # noqa: BLE001
            logger.debug("Ollama translation unavailable: %s", e)
        return None

    async def _try_platform(self, text: str, source: str, target: str) -> str | None:
        try:
            from modules.ai_video_studio.services.ai_studio import LLMClient

            result = await LLMClient.generate(
                f"Translate from {source} to {target}:\n\n{text}",
                system="Reply with ONLY the translated text.",
                temperature=0.2,
            )
            translated = (result.get("content") or "").strip()
            if translated:
                return translated
        except Exception as e:  # noqa: BLE001
            logger.debug("platform LLM translation unavailable: %s", e)
        return None

    def _phrase_fallback(self, text: str, source: str, target: str) -> str:
        """Small bilingual phrasebook so common phrases survive offline."""
        phrasebook = {
            ("en", "pt"): {"hello": "olá", "thanks": "obrigado", "goodbye": "adeus",
                           "yes": "sim", "no": "não", "welcome": "bem-vindo"},
            ("pt", "en"): {"olá": "hello", "obrigado": "thanks", "adeus": "goodbye",
                           "sim": "yes", "não": "no"},
            ("en", "es"): {"hello": "hola", "thanks": "gracias", "goodbye": "adiós",
                           "yes": "sí", "no": "no"},
        }
        book = phrasebook.get((source.lower(), target.lower()), {})
        out = text
        for word, replacement in book.items():
            import re

            out = re.sub(rf"\b{word}\b", replacement, out, flags=re.IGNORECASE)
        return out
