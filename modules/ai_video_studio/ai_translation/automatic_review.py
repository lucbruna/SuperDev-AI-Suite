"""Automatic Review — verifies translations before they are used."""
from __future__ import annotations

import asyncio
from typing import Any

from modules.ai_video_studio.ai_translation.quality_checker import score_translation


class AutomaticReview:
    """Runs quality checks and (optionally) an LLM self-review."""

    def __init__(self) -> None:
        self._count = 0
        self._accepted = 0

    async def review(self, source: str, translated: str, *, source_lang: str = "en",
                     target_lang: str = "pt", glossary_hits: int = 0,
                     glossary_terms: int = 0, llm_review: bool = True) -> dict[str, Any]:
        report = score_translation(
            source, translated, source_lang=source_lang, target_lang=target_lang,
            glossary_hits=glossary_hits, glossary_terms=glossary_terms,
        )
        llm_note = ""
        if llm_review and report["score"] >= 60:
            llm_note = await self._llm_check(source, translated, source_lang, target_lang)

        approved = report["score"] >= 60 and "BLOCKED" not in llm_note.upper()
        self._count += 1
        self._accepted += int(approved)
        return {
            "approved": approved,
            "score": report["score"],
            "checks": report["checks"],
            "llm_note": llm_note[:200] or None,
        }

    async def _llm_check(self, source: str, translated: str, src: str, tgt: str) -> str:
        try:
            from modules.ai_video_studio.media.llm import generate_text

            result = await asyncio.to_thread(
                generate_text,
                f"Review this {src}→{tgt} translation for fidelity. Reply APPROVED or "
                f"BLOCKED plus one reason.\\nSource: {source}\\nTranslation: {translated}",
                system="You are a strict translation QA reviewer.",
                temperature=0.1,
                timeout=60.0,
                max_tokens=80,
            )
            return result
        except Exception:  # noqa: BLE001 — LLM review is optional
            return ""

    def stats(self) -> dict[str, Any]:
        return {
            "reviewed": self._count,
            "accepted": self._accepted,
            "acceptance_rate": round(self._accepted / self._count, 3) if self._count else 0.0,
        }
