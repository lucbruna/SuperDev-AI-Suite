"""Automatic Translation — translates dialogue lines via the AI translation engine."""
from __future__ import annotations

import asyncio
from typing import Any

from modules.ai_video_studio.ai_translation import get_translation_engine


class AutomaticTranslation:
    """Bulk translation of script lines with per-line report."""

    def __init__(self) -> None:
        self.engine = get_translation_engine()

    def translate_lines(self, lines: list[str], target: str, *,
                        source: str | None = None, use_llm: bool = True,
                        provider_timeout: float = 90.0) -> tuple[list[str], dict[str, Any]]:
        try:
            return asyncio.run(self.translate_lines_async(
                lines, target, source=source, use_llm=use_llm, provider_timeout=provider_timeout))
        except RuntimeError:
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                return pool.submit(
                    asyncio.run, self.translate_lines_async(
                        lines, target, source=source, use_llm=use_llm, provider_timeout=provider_timeout)
                ).result()

    async def translate_lines_async(self, lines: list[str], target: str, *,
                                    source: str | None = None, use_llm: bool = True,
                                    provider_timeout: float = 90.0) -> tuple[list[str], dict[str, Any]]:
        translated: list[str] = []
        engines: set[str] = set()
        for line in lines:
            result = await self.engine.translate_async(
                line, target, source=source, use_llm=use_llm, provider_timeout=provider_timeout)
            translated.append(result["text"])
            engines.add(result["engine"])
        return translated, {"engine": ", ".join(sorted(engines)), "lines": len(translated)}
